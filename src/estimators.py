"""Estimator functions for PSM, DID, DID with covariates, and PSM-DID.

All matching and covariate adjustment in this file is restricted to observed
pre-treatment covariates. Simulation-only columns such as `alpha`, `u`,
potential outcomes, and true propensity scores are never valid estimator inputs.
"""

from __future__ import annotations

from typing import Iterable

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import NearestNeighbors

DEFAULT_COVARIATES = ("x1", "x2")
FORBIDDEN_ESTIMATION_COLUMNS = {
    "alpha",
    "u",
    "y",
    "y0",
    "y1_potential",
    "y1_untreated",
    "y1_treated",
    "untreated_trend",
    "treatment_effect",
    "propensity_true",
}


def make_wide_panel(data: pd.DataFrame, covariates: Iterable[str] = DEFAULT_COVARIATES) -> pd.DataFrame:
    """Convert a two-period long panel to one row per unit.

    Args:
        data: Long-format panel with one row per unit-period. Required columns
            are `unit_id`, `post`, `treated`, `y`, and the requested covariates.
        covariates: Observed pre-treatment covariates to carry into the unit
            level data. These must not include forbidden simulation-only or
            outcome columns.

    Returns:
        Wide-format DataFrame with `y_pre`, `y_post`, and `delta_y`.

    Notes:
        This helper does not estimate a treatment effect. It prepares unit-level
        data for DID and ATT-style matching estimators. `alpha` and `u` may exist
        in the input data for diagnostics, but they are not retained unless the
        caller incorrectly requests them, in which case an error is raised.
    """

    covariate_list = _validate_covariates(covariates)
    required = {"unit_id", "post", "treated", "y", *covariate_list}
    missing = required.difference(data.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    post_values = set(data["post"].dropna().unique())
    if post_values != {0, 1}:
        raise ValueError("Expected exactly two periods coded as post=0 and post=1.")

    counts = data.groupby("unit_id")["post"].nunique()
    if not (counts == 2).all():
        raise ValueError("Each unit_id must have exactly one pre and one post observation.")

    invariant_cols = ["treated", *covariate_list]
    for col in invariant_cols:
        max_unique = data.groupby("unit_id")[col].nunique(dropna=False).max()
        if max_unique != 1:
            raise ValueError(f"{col!r} must be time-invariant within unit_id.")

    base = data.sort_values(["unit_id", "post"]).drop_duplicates("unit_id")[
        ["unit_id", "treated", *covariate_list]
    ]
    y_wide = data.pivot(index="unit_id", columns="post", values="y").rename(
        columns={0: "y_pre", 1: "y_post"}
    )
    wide = base.merge(y_wide, left_on="unit_id", right_index=True, how="left")
    wide["delta_y"] = wide["y_post"] - wide["y_pre"]
    return wide.reset_index(drop=True)


def estimate_propensity_scores(
    wide_data: pd.DataFrame,
    covariates: Iterable[str] = DEFAULT_COVARIATES,
    propensity_col: str = "propensity_score",
) -> pd.DataFrame:
    """Estimate propensity scores using only observed pre-treatment covariates.

    Args:
        wide_data: One row per unit. Must contain `treated` and covariate columns.
        covariates: Observed pre-treatment covariates, typically `x1` and `x2`.
        propensity_col: Name of the estimated propensity score column to add.

    Returns:
        Copy of `wide_data` with an estimated propensity score column.

    Raises:
        ValueError: If forbidden columns such as `u`, `alpha`, outcomes, or true
        simulation quantities are requested as covariates.
    """

    covariate_list = _validate_covariates(covariates)
    required = {"treated", *covariate_list}
    missing = required.difference(wide_data.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    if wide_data["treated"].nunique() != 2:
        raise ValueError("Propensity score estimation requires treated and control units.")

    model = LogisticRegression(max_iter=1000)
    model.fit(wide_data[covariate_list], wide_data["treated"])

    out = wide_data.copy()
    out[propensity_col] = model.predict_proba(out[covariate_list])[:, 1]
    return out


def nearest_neighbor_match(
    wide_data: pd.DataFrame,
    propensity_col: str = "propensity_score",
    replacement: bool = True,
    caliper: float | None = None,
) -> tuple[pd.DataFrame, dict]:
    """Match treated units to controls by nearest propensity score.

    Args:
        wide_data: Unit-level data containing `unit_id`, `treated`, outcomes, and
            the propensity score column.
        propensity_col: Column containing estimated propensity scores.
        replacement: If True, controls may be reused across treated units.
        caliper: Optional maximum absolute propensity-score distance. Treated
            units outside the caliper are dropped from the matched-pair table.

    Returns:
        A pair-level DataFrame and a diagnostics dictionary. Each row of the
        pair-level table contains one treated unit, its matched control, the
        propensity-score distance, post outcomes, and outcome changes. This is an
        ATT-style match.
    """

    required = {"unit_id", "treated", "y_post", "delta_y", propensity_col}
    missing = required.difference(wide_data.columns)
    if missing:
        raise ValueError(f"Missing required columns for matching: {sorted(missing)}")

    treated = wide_data[wide_data["treated"] == 1].copy().reset_index(drop=True)
    controls = wide_data[wide_data["treated"] == 0].copy().reset_index(drop=True)
    if treated.empty or controls.empty:
        raise ValueError("Both treated and control groups are required for matching.")

    if replacement:
        pairs = _match_with_replacement(treated, controls, propensity_col, caliper)
    else:
        pairs = _greedy_match_without_replacement(treated, controls, propensity_col, caliper)

    diagnostics = _matching_diagnostics(
        wide_data=wide_data,
        pairs=pairs,
        propensity_col=propensity_col,
        caliper=caliper,
        replacement=replacement,
    )
    if pairs.empty:
        raise ValueError("No treated units were matched. Check overlap or relax the caliper.")
    return pairs, diagnostics


def estimate_psm(
    data: pd.DataFrame,
    covariates: Iterable[str] = DEFAULT_COVARIATES,
    replacement: bool = True,
    caliper: float | None = None,
) -> dict:
    """Estimate a PSM-only post-period ATT.

    Args:
        data: Long-format two-period panel.
        covariates: Observed pre-treatment covariates used for propensity scores.
        replacement: Whether nearest-neighbor controls can be reused.
        caliper: Optional maximum propensity-score distance.

    Returns:
        Structured result dictionary. `estimate` is the mean matched difference
        in post-period outcomes, `Y_i1 - Y_m(i)1`, for treated units.

    Notes:
        This cross-sectional matching estimator does not use DID. It can remain
        biased when unobserved time-invariant heterogeneity such as `alpha`
        affects treatment and outcomes.
    """

    covariate_list = _validate_covariates(covariates)
    wide = estimate_propensity_scores(make_wide_panel(data, covariate_list), covariate_list)
    pairs, diagnostics = nearest_neighbor_match(
        wide,
        propensity_col="propensity_score",
        replacement=replacement,
        caliper=caliper,
    )
    estimate = float((pairs["treated_y_post"] - pairs["control_y_post"]).mean())
    return _result_dict(
        estimator="psm",
        estimate=estimate,
        wide=wide,
        covariates=covariate_list,
        uses_matching=True,
        estimand="ATT",
        match_diagnostics=diagnostics,
    )


def estimate_did(data: pd.DataFrame) -> dict:
    """Estimate simple DID using first differences.

    Args:
        data: Long-format two-period panel.

    Returns:
        Structured result dictionary. `estimate` is the coefficient on `treated`
        in `delta_y ~ treated`, where `delta_y = Y_i1 - Y_i0`.

    Notes:
        This estimator does not use matching and targets the treatment effect
        under unconditional parallel trends.
    """

    wide = make_wide_panel(data, DEFAULT_COVARIATES)
    model = smf.ols("delta_y ~ treated", data=wide).fit()
    return _result_dict(
        estimator="did",
        estimate=float(model.params["treated"]),
        wide=wide,
        covariates=[],
        uses_matching=False,
        estimand="ATE/ATT under constant tau",
        model_formula="delta_y ~ treated",
    )


def estimate_did_with_covariates(
    data: pd.DataFrame,
    covariates: Iterable[str] = DEFAULT_COVARIATES,
) -> dict:
    """Estimate DID with pre-treatment covariates using first differences.

    Args:
        data: Long-format two-period panel.
        covariates: Observed pre-treatment covariates included in the differenced
            outcome regression.

    Returns:
        Structured result dictionary. `estimate` is the coefficient on `treated`
        in `delta_y ~ treated + x1 + x2` or the analogous requested covariates.

    Notes:
        This intentionally avoids the common mistake of adding time-invariant
        covariates only as main effects in a long-format DID regression. In
        long format, the equivalent adjustment would require `post x covariate`
        interactions.
    """

    covariate_list = _validate_covariates(covariates)
    wide = make_wide_panel(data, covariate_list)
    rhs = " + ".join(["treated", *covariate_list])
    formula = f"delta_y ~ {rhs}"
    model = smf.ols(formula, data=wide).fit()
    return _result_dict(
        estimator="did_with_covariates",
        estimate=float(model.params["treated"]),
        wide=wide,
        covariates=covariate_list,
        uses_matching=False,
        estimand="ATE/ATT under constant tau",
        model_formula=formula,
    )


def estimate_psm_did(
    data: pd.DataFrame,
    covariates: Iterable[str] = DEFAULT_COVARIATES,
    replacement: bool = True,
    caliper: float | None = None,
) -> dict:
    """Estimate PSM-DID as an ATT-style matched change comparison.

    Args:
        data: Long-format two-period panel.
        covariates: Observed pre-treatment covariates used for propensity scores.
        replacement: Whether nearest-neighbor controls can be reused.
        caliper: Optional maximum propensity-score distance.

    Returns:
        Structured result dictionary. `estimate` is
        mean(`delta_y_treated - delta_y_matched_control`) across matched treated
        units.

    Notes:
        Matching is done before differencing comparisons and uses only observed
        pre-treatment covariates. This estimator is naturally interpreted as an
        ATT-style PSM-DID estimator.
    """

    covariate_list = _validate_covariates(covariates)
    wide = estimate_propensity_scores(make_wide_panel(data, covariate_list), covariate_list)
    pairs, diagnostics = nearest_neighbor_match(
        wide,
        propensity_col="propensity_score",
        replacement=replacement,
        caliper=caliper,
    )
    estimate = float((pairs["treated_delta_y"] - pairs["control_delta_y"]).mean())
    return _result_dict(
        estimator="psm_did",
        estimate=estimate,
        wide=wide,
        covariates=covariate_list,
        uses_matching=True,
        estimand="ATT",
        match_diagnostics=diagnostics,
    )


def estimate_all(data: pd.DataFrame, covariates: Iterable[str] = DEFAULT_COVARIATES) -> list[dict]:
    """Run all required estimators on one simulated dataset.

    Args:
        data: Long-format two-period panel from `generate_data`.
        covariates: Observed pre-treatment covariates allowed for matching and
            covariate-adjusted DID.

    Returns:
        List of structured result dictionaries for PSM-only, simple DID,
        covariate-adjusted DID, and PSM-DID.
    """

    covariate_list = _validate_covariates(covariates)
    return [
        estimate_psm(data, covariate_list),
        estimate_did(data),
        estimate_did_with_covariates(data, covariate_list),
        estimate_psm_did(data, covariate_list),
    ]


def sanity_check_estimators(
    n: int = 500,
    tau: float = 2.0,
    seed: int = 20260501,
    covariates: Iterable[str] = DEFAULT_COVARIATES,
) -> pd.DataFrame:
    """Run a lightweight estimator check on one dataset per scenario.

    Args:
        n: Number of units per scenario for the debug check.
        tau: True constant treatment effect used by the DGP.
        seed: Base random seed.
        covariates: Observed pre-treatment covariates for allowed estimators.

    Returns:
        DataFrame summarizing whether each estimator ran, its estimate, sample
        sizes, matched sample sizes, and whether forbidden variables were used.

    Notes:
        This is a code sanity check only. Its estimates should not be reported as
        final Monte Carlo results.
    """

    from .dgp import generate_data

    rows: list[dict] = []
    for offset, scenario in enumerate(("A", "B", "C")):
        data = generate_data(scenario, n=n, tau=tau, seed=seed + offset)
        for result in estimate_all(data, covariates):
            rows.append(
                {
                    "scenario": scenario,
                    "estimator": result["estimator"],
                    "estimate": result["estimate"],
                    "n_treated": result["n_treated"],
                    "n_control": result["n_control"],
                    "n_matched_treated": result.get("n_matched_treated"),
                    "n_unique_matched_controls": result.get("n_unique_matched_controls"),
                    "uses_forbidden_variables": result["uses_forbidden_variables"],
                    "ran_ok": np.isfinite(result["estimate"]),
                }
            )
    return pd.DataFrame(rows)


def _match_with_replacement(
    treated: pd.DataFrame,
    controls: pd.DataFrame,
    propensity_col: str,
    caliper: float | None,
) -> pd.DataFrame:
    """Return nearest-neighbor pairs when controls may be reused."""

    nn = NearestNeighbors(n_neighbors=1)
    nn.fit(controls[[propensity_col]])
    distances, indices = nn.kneighbors(treated[[propensity_col]])

    rows = []
    for treated_pos, (distance, control_pos) in enumerate(zip(distances.flatten(), indices.flatten())):
        if caliper is not None and distance > caliper:
            continue
        rows.append(_pair_row(treated.iloc[treated_pos], controls.iloc[control_pos], float(distance)))
    return pd.DataFrame(rows)


def _greedy_match_without_replacement(
    treated: pd.DataFrame,
    controls: pd.DataFrame,
    propensity_col: str,
    caliper: float | None,
) -> pd.DataFrame:
    """Return greedy nearest-neighbor pairs without reusing controls."""

    available = controls.copy()
    rows = []
    treated_order = treated.sort_values(propensity_col).index
    for treated_idx in treated_order:
        if available.empty:
            break
        treated_row = treated.loc[treated_idx]
        distances = (available[propensity_col] - treated_row[propensity_col]).abs()
        control_idx = distances.idxmin()
        distance = float(distances.loc[control_idx])
        if caliper is not None and distance > caliper:
            continue
        rows.append(_pair_row(treated_row, available.loc[control_idx], distance))
        available = available.drop(index=control_idx)
    return pd.DataFrame(rows)


def _pair_row(treated_row: pd.Series, control_row: pd.Series, distance: float) -> dict:
    """Build one matched-pair record."""

    return {
        "treated_unit_id": treated_row["unit_id"],
        "control_unit_id": control_row["unit_id"],
        "treated_propensity_score": treated_row["propensity_score"],
        "control_propensity_score": control_row["propensity_score"],
        "match_distance": distance,
        "treated_y_post": treated_row["y_post"],
        "control_y_post": control_row["y_post"],
        "treated_delta_y": treated_row["delta_y"],
        "control_delta_y": control_row["delta_y"],
    }


def _matching_diagnostics(
    wide_data: pd.DataFrame,
    pairs: pd.DataFrame,
    propensity_col: str,
    caliper: float | None,
    replacement: bool,
) -> dict:
    """Summarize overlap and matched sample diagnostics."""

    treated = wide_data[wide_data["treated"] == 1]
    controls = wide_data[wide_data["treated"] == 0]
    treated_range = (float(treated[propensity_col].min()), float(treated[propensity_col].max()))
    control_range = (float(controls[propensity_col].min()), float(controls[propensity_col].max()))
    support_min = max(treated_range[0], control_range[0])
    support_max = min(treated_range[1], control_range[1])
    outside_support = (
        (treated[propensity_col] < support_min) | (treated[propensity_col] > support_max)
    ).mean()
    n_matched = int(len(pairs))
    n_treated = int(len(treated))

    warnings = []
    if support_min >= support_max:
        warnings.append("No overlapping propensity-score range between treated and controls.")
    if outside_support > 0.2:
        warnings.append("More than 20% of treated units lie outside common support.")
    if n_matched < n_treated:
        warnings.append("Some treated units were dropped by caliper or no-replacement matching.")

    return {
        "replacement": replacement,
        "caliper": caliper,
        "n_matched_treated": n_matched,
        "n_unique_matched_controls": int(pairs["control_unit_id"].nunique()) if n_matched else 0,
        "mean_match_distance": float(pairs["match_distance"].mean()) if n_matched else np.nan,
        "max_match_distance": float(pairs["match_distance"].max()) if n_matched else np.nan,
        "treated_pscore_min": treated_range[0],
        "treated_pscore_max": treated_range[1],
        "control_pscore_min": control_range[0],
        "control_pscore_max": control_range[1],
        "common_support_min": support_min,
        "common_support_max": support_max,
        "share_treated_outside_common_support": float(outside_support),
        "warnings": warnings,
    }


def _result_dict(
    estimator: str,
    estimate: float,
    wide: pd.DataFrame,
    covariates: list[str],
    uses_matching: bool,
    estimand: str,
    match_diagnostics: dict | None = None,
    model_formula: str | None = None,
) -> dict:
    """Create a consistent structured estimator result."""

    n_treated = int((wide["treated"] == 1).sum())
    n_control = int((wide["treated"] == 0).sum())
    result = {
        "estimator": estimator,
        "estimate": estimate,
        "n_total": int(len(wide)),
        "n_treated": n_treated,
        "n_control": n_control,
        "n_matched_treated": None,
        "n_unique_matched_controls": None,
        "covariates": list(covariates),
        "uses_matching": uses_matching,
        "estimand": estimand,
        "uses_forbidden_variables": False,
        "forbidden_variables": sorted(FORBIDDEN_ESTIMATION_COLUMNS.intersection(covariates)),
        "model_formula": model_formula,
        "warnings": [],
    }
    if match_diagnostics:
        result.update(
            {
                "n_matched_treated": match_diagnostics["n_matched_treated"],
                "n_unique_matched_controls": match_diagnostics["n_unique_matched_controls"],
                "mean_match_distance": match_diagnostics["mean_match_distance"],
                "max_match_distance": match_diagnostics["max_match_distance"],
                "share_treated_outside_common_support": match_diagnostics[
                    "share_treated_outside_common_support"
                ],
                "warnings": match_diagnostics["warnings"],
                "matching_diagnostics": match_diagnostics,
            }
        )
    return result


def _validate_covariates(covariates: Iterable[str]) -> list[str]:
    """Validate that requested covariates are observed pre-treatment variables."""

    covariate_list = list(covariates)
    if not covariate_list:
        raise ValueError("At least one observed pre-treatment covariate is required.")
    forbidden = FORBIDDEN_ESTIMATION_COLUMNS.intersection(covariate_list)
    if forbidden:
        raise ValueError(
            "Forbidden estimator covariate(s) requested: "
            f"{sorted(forbidden)}. Use only observed pre-treatment covariates."
        )
    return covariate_list
