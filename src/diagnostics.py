"""Diagnostics for covariate balance and common support."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

from .dgp import ScenarioName, generate_data
from .estimators import (
    DEFAULT_COVARIATES,
    estimate_propensity_scores,
    make_wide_panel,
    nearest_neighbor_match,
)


def standardized_mean_difference(x_treated: pd.Series, x_control: pd.Series) -> float:
    """Calculate the standardized mean difference for one covariate.

    Args:
        x_treated: Covariate values for treated units.
        x_control: Covariate values for control units.

    Returns:
        Difference in means divided by the pooled standard deviation. Returns
        NaN if the pooled standard deviation is zero or undefined.
    """

    pooled_sd = np.sqrt((x_treated.var(ddof=1) + x_control.var(ddof=1)) / 2)
    if pooled_sd == 0 or np.isnan(pooled_sd):
        return np.nan
    return float((x_treated.mean() - x_control.mean()) / pooled_sd)


def make_balance_table(
    data: pd.DataFrame,
    covariates: Iterable[str] = DEFAULT_COVARIATES,
    matched_pairs: pd.DataFrame | None = None,
    matching_options: dict | None = None,
) -> pd.DataFrame:
    """Create before/after matching covariate balance diagnostics.

    Args:
        data: Long-format two-period panel from the DGP.
        covariates: Observed pre-treatment covariates used for matching.
        matched_pairs: Optional output from `nearest_neighbor_match`. If omitted,
            matches are estimated using logistic propensity scores on `covariates`.
        matching_options: Optional nearest-neighbor matching options such as
            `replacement` and `caliper`.

    Returns:
        Balance table with treated/control means and standardized mean
        differences before and after matching.

    Notes:
        Matching uses only observed pre-treatment covariates, typically `x1` and
        `x2`. Simulation-only variables such as `alpha`, `u`, potential outcomes,
        true propensity scores, and untreated trends must not be requested.
    """

    covariate_list = list(covariates)
    match_opts = {"replacement": True}
    match_opts.update(matching_options or {})

    wide = make_wide_panel(data, covariate_list)
    scenario = _scenario_label(data)
    if matched_pairs is None:
        scored = estimate_propensity_scores(wide, covariate_list)
        matched_pairs, _ = nearest_neighbor_match(scored, **match_opts)

    after = _matched_covariate_frame(wide, matched_pairs, covariate_list)
    rows = []
    for covariate in covariate_list:
        treated_before = wide.loc[wide["treated"] == 1, covariate]
        control_before = wide.loc[wide["treated"] == 0, covariate]
        treated_after = after[f"treated_{covariate}"]
        control_after = after[f"control_{covariate}"]
        rows.append(
            {
                "scenario": scenario,
                "covariate": covariate,
                "treated_mean_before": treated_before.mean(),
                "control_mean_before": control_before.mean(),
                "smd_before": standardized_mean_difference(treated_before, control_before),
                "treated_mean_after": treated_after.mean(),
                "control_mean_after": control_after.mean(),
                "smd_after": standardized_mean_difference(treated_after, control_after),
                "abs_smd_before": abs(
                    standardized_mean_difference(treated_before, control_before)
                ),
                "abs_smd_after": abs(
                    standardized_mean_difference(treated_after, control_after)
                ),
                "n_treated_before": int((wide["treated"] == 1).sum()),
                "n_control_before": int((wide["treated"] == 0).sum()),
                "n_treated_after": int(len(after)),
                "n_control_after": int(len(after)),
                "n_unique_control_after": int(matched_pairs["control_unit_id"].nunique()),
                "matching_method": "nearest_neighbor_propensity_score",
                "replacement": bool(match_opts.get("replacement", True)),
                "caliper": match_opts.get("caliper"),
            }
        )
    return pd.DataFrame(rows)


def make_balance_tables_by_scenario(
    scenarios: Iterable[ScenarioName] = ("A", "B", "C"),
    n: int = 1000,
    tau: float = 2.0,
    seed: int = 12345,
    covariates: Iterable[str] = DEFAULT_COVARIATES,
    output_dir: str | Path = "tables",
    suffix: str = "debug",
    matching_options: dict | None = None,
) -> dict[str, pd.DataFrame | Path]:
    """Create and save balance and common-support diagnostics by scenario.

    Args:
        scenarios: DGP scenario labels.
        n: Number of units for each diagnostic sample.
        tau: True treatment effect for the DGP sample.
        seed: Base seed. Each scenario receives a distinct deterministic offset.
        covariates: Observed pre-treatment covariates for propensity scores.
        output_dir: Directory for CSV diagnostics.
        suffix: Filename suffix, e.g. `debug` or `final`.
        matching_options: Optional matching options shared across scenarios.

    Returns:
        Dictionary containing DataFrames and saved CSV paths.
    """

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    balance_tables = []
    support_data_tables = []
    support_summary_tables = []
    for scenario_index, scenario in enumerate(tuple(scenarios)):
        data = generate_data(
            scenario,
            n=n,
            tau=tau,
            seed=seed + 200_000 * (scenario_index + 1),
        )
        balance_tables.append(
            make_balance_table(
                data,
                covariates=covariates,
                matching_options=matching_options,
            )
        )
        support_data, support_summary = make_common_support_data(data, covariates)
        support_data_tables.append(support_data)
        support_summary_tables.append(support_summary)

    balance = pd.concat(balance_tables, ignore_index=True)
    support_data_all = pd.concat(support_data_tables, ignore_index=True)
    support_summary = pd.concat(support_summary_tables, ignore_index=True)

    balance_path = output_path / f"balance_table_{suffix}.csv"
    support_data_path = output_path / f"common_support_data_{suffix}.csv"
    support_summary_path = output_path / f"common_support_summary_{suffix}.csv"
    balance.to_csv(balance_path, index=False)
    support_data_all.to_csv(support_data_path, index=False)
    support_summary.to_csv(support_summary_path, index=False)

    return {
        "balance": balance,
        "support_data": support_data_all,
        "support_summary": support_summary,
        "balance_path": balance_path,
        "support_data_path": support_data_path,
        "support_summary_path": support_summary_path,
    }


def make_common_support_data(
    data: pd.DataFrame,
    covariates: Iterable[str] = DEFAULT_COVARIATES,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Estimate propensity scores and mark units inside common support.

    Args:
        data: Long-format two-period panel.
        covariates: Observed pre-treatment covariates used to estimate propensity
            scores. The true DGP propensity score is intentionally not used.

    Returns:
        A tuple of `(support_data, support_summary)`. The first has one row per
        unit and includes estimated propensity scores and common-support flags.
        The second summarizes overlap by scenario.
    """

    covariate_list = list(covariates)
    wide = estimate_propensity_scores(make_wide_panel(data, covariate_list), covariate_list)
    scenario = _scenario_label(data)

    treated_scores = wide.loc[wide["treated"] == 1, "propensity_score"]
    control_scores = wide.loc[wide["treated"] == 0, "propensity_score"]
    min_control = float(control_scores.min())
    max_control = float(control_scores.max())
    min_treated = float(treated_scores.min())
    max_treated = float(treated_scores.max())
    common_min = max(min_control, min_treated)
    common_max = min(max_control, max_treated)

    support = wide[["unit_id", "treated", "propensity_score"]].copy()
    support["id"] = support["unit_id"]
    support["scenario"] = scenario
    support["min_control_score"] = min_control
    support["max_control_score"] = max_control
    support["min_treated_score"] = min_treated
    support["max_treated_score"] = max_treated
    support["common_support_min"] = common_min
    support["common_support_max"] = common_max
    support["in_common_support"] = support["propensity_score"].between(
        common_min,
        common_max,
        inclusive="both",
    )

    treated_outside = int(((support["treated"] == 1) & ~support["in_common_support"]).sum())
    control_outside = int(((support["treated"] == 0) & ~support["in_common_support"]).sum())
    summary = pd.DataFrame(
        [
            {
                "scenario": scenario,
                "n_treated": int((support["treated"] == 1).sum()),
                "n_control": int((support["treated"] == 0).sum()),
                "treated_outside_control_support_count": treated_outside,
                "control_outside_treated_support_count": control_outside,
                "share_treated_outside_control_support": treated_outside
                / max(int((support["treated"] == 1).sum()), 1),
                "share_control_outside_treated_support": control_outside
                / max(int((support["treated"] == 0).sum()), 1),
                "min_control_score": min_control,
                "max_control_score": max_control,
                "min_treated_score": min_treated,
                "max_treated_score": max_treated,
                "common_support_min": common_min,
                "common_support_max": common_max,
            }
        ]
    )
    return support, summary


def _matched_covariate_frame(
    wide: pd.DataFrame,
    matched_pairs: pd.DataFrame,
    covariates: list[str],
) -> pd.DataFrame:
    """Attach covariates to matched treated-control pair ids."""

    treated_cov = wide[["unit_id", *covariates]].rename(
        columns={"unit_id": "treated_unit_id", **{cov: f"treated_{cov}" for cov in covariates}}
    )
    control_cov = wide[["unit_id", *covariates]].rename(
        columns={"unit_id": "control_unit_id", **{cov: f"control_{cov}" for cov in covariates}}
    )
    return matched_pairs[["treated_unit_id", "control_unit_id"]].merge(
        treated_cov,
        on="treated_unit_id",
        how="left",
    ).merge(control_cov, on="control_unit_id", how="left")


def _scenario_label(data: pd.DataFrame) -> str:
    """Extract a single scenario label from a DGP dataset."""

    if "scenario" not in data.columns:
        return "unknown"
    scenarios = data["scenario"].dropna().unique()
    if len(scenarios) != 1:
        raise ValueError("Expected diagnostics data to contain exactly one scenario.")
    return str(scenarios[0])
