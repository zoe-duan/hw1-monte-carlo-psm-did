"""Data-generating processes for HW1.

The three DGPs are designed to isolate the identification logic behind DID,
PSM, and PSM-DID in a two-period panel:

    A. Unconditional parallel trends.
    B. Trends driven by observed pre-treatment covariates.
    C. Trends driven partly by an unobserved time-varying confounder.

All scenarios use a constant treatment effect, so ATT and ATE are numerically
equal in the simulation. Matching-based estimators should still be described as
ATT-oriented because they compare treated units to matched controls.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
import pandas as pd

ScenarioName = Literal["A", "B", "C"]


@dataclass(frozen=True)
class DGPConfig:
    """Configuration for one Monte Carlo DGP.

    Args:
        scenario: Scenario label: A, B, or C.
        n: Number of units.
        tau: Constant treatment effect.
        seed: Random seed.
        params: Optional parameter overrides for calibration checks.
    """

    scenario: ScenarioName
    n: int
    tau: float
    seed: int
    params: dict[str, float] | None = None


BASELINE_PARAMS: dict[str, float] = {
    "beta_0": 1.0,
    "beta_1": 1.0,
    "beta_2": 0.5,
    "sigma_alpha": 1.0,
    "sigma_epsilon": 1.0,
    "lambda_time": 1.0,
    "kappa_1": 0.8,
    "kappa_2": 0.6,
    "delta_u": 1.0,
    "gamma_0": -0.3,
    "gamma_1": 0.8,
    "gamma_2": 0.6,
    "gamma_alpha": 0.5,
    "gamma_u": 0.8,
}


def generate_data(
    scenario: ScenarioName | DGPConfig,
    n: int | None = None,
    tau: float | None = None,
    seed: int | None = None,
    params: dict[str, float] | None = None,
) -> pd.DataFrame:
    """Generate one simulated two-period panel dataset.

    Args:
        scenario: Scenario label or a DGPConfig object.
        n: Number of units when `scenario` is a string.
        tau: Constant treatment effect when `scenario` is a string.
        seed: Random seed when `scenario` is a string.
        params: Optional parameter overrides.

    Returns:
        Long-format DataFrame with two rows per unit. Key columns include:
        `id`, `unit_id`, `scenario`, `treated`, `post`, `time`, `y`, `y0`,
        `y1_potential`, `x1`, `x2`, `alpha`, `u`, and `propensity_true`.

    Assumptions:
        Treatment is assigned at the unit level and only affects observed
        outcomes in the post period. Estimators should use only pre-treatment
        observed covariates such as `x1` and `x2` for matching; `alpha` and `u`
        are simulation diagnostics, not valid matching variables.
    """

    config = _coerce_config(scenario, n=n, tau=tau, seed=seed, params=params)
    p = _merge_params(config.params)
    rng = _rng(config.seed)

    unit_id = np.arange(config.n)
    x1 = rng.normal(loc=0.0, scale=1.0, size=config.n)
    x2 = rng.binomial(n=1, p=0.5, size=config.n)
    alpha = rng.normal(loc=0.0, scale=p["sigma_alpha"], size=config.n)
    u = rng.normal(loc=0.0, scale=1.0, size=config.n)

    linear_score = (
        p["gamma_0"]
        + p["gamma_1"] * x1
        + p["gamma_2"] * x2
        + p["gamma_alpha"] * alpha
    )
    if config.scenario == "C":
        linear_score = linear_score + p["gamma_u"] * u

    propensity_true = _logistic(linear_score)
    treated = rng.binomial(n=1, p=propensity_true, size=config.n)

    eps0 = rng.normal(loc=0.0, scale=p["sigma_epsilon"], size=config.n)
    eps1 = rng.normal(loc=0.0, scale=p["sigma_epsilon"], size=config.n)

    y_pre = p["beta_0"] + p["beta_1"] * x1 + p["beta_2"] * x2 + alpha + eps0
    untreated_trend = _untreated_trend(config.scenario, x1=x1, x2=x2, u=u, params=p)
    y_post_untreated = (
        p["beta_0"]
        + p["beta_1"] * x1
        + p["beta_2"] * x2
        + alpha
        + untreated_trend
        + eps1
    )
    y_post_treated = y_post_untreated + config.tau

    pre = pd.DataFrame(
        {
            "id": unit_id,
            "unit_id": unit_id,
            "scenario": config.scenario,
            "treated": treated,
            "post": 0,
            "time": 0,
            "y": y_pre,
            "y0": y_pre,
            "y1_potential": y_post_untreated,
            "x1": x1,
            "x2": x2,
            "alpha": alpha,
            "u": u,
            "propensity_true": propensity_true,
            "y1_untreated": y_post_untreated,
            "y1_treated": y_post_treated,
            "untreated_trend": untreated_trend,
            "treatment_effect": config.tau,
            "u_allowed_for_estimation": False,
            "alpha_allowed_for_estimation": False,
        }
    )
    post = pre.copy()
    post["post"] = 1
    post["time"] = 1
    post["y"] = np.where(treated == 1, y_post_treated, y_post_untreated)
    post["y0"] = y_post_untreated
    post["y1_potential"] = y_post_treated

    return (
        pd.concat([pre, post], ignore_index=True)
        .sort_values(["unit_id", "post"])
        .reset_index(drop=True)
    )


def sanity_check_dgp(
    scenarios: tuple[ScenarioName, ...] = ("A", "B", "C"),
    n: int = 500,
    tau: float = 2.0,
    seed: int = 20260501,
    params: dict[str, float] | None = None,
) -> pd.DataFrame:
    """Run lightweight DGP checks without estimating treatment effects.

    The checks verify panel shape, time-invariant unit attributes, post-period
    treatment activation, and the intended trend structure for each scenario.
    This is intended for debugging the DGP only, not for final Monte Carlo
    reporting.
    """

    rows: list[dict[str, object]] = []
    for offset, scenario in enumerate(scenarios):
        data = generate_data(
            scenario=scenario,
            n=n,
            tau=tau,
            seed=seed + offset,
            params=params,
        )
        unit_counts = data.groupby("unit_id")["post"].nunique()
        invariant_cols = ["x1", "x2", "treated", "alpha", "u"]
        invariant_ok = all(
            data.groupby("unit_id")[col].nunique().max() == 1 for col in invariant_cols
        )

        wide = data.pivot(index="unit_id", columns="post", values=["y", "y0", "treated"])
        observed_gain = wide[("y", 1)] - wide[("y0", 1)]
        treated = wide[("treated", 0)]
        treatment_effect_ok = np.allclose(observed_gain, treated * tau)

        pre_rows = data[data["post"] == 0].drop_duplicates("unit_id")
        trend = pre_rows["untreated_trend"]
        trend_x_corr = _safe_corr(trend, pre_rows["x1"])
        trend_u_corr = _safe_corr(trend, pre_rows["u"])

        rows.append(
            {
                "scenario": scenario,
                "n": n,
                "rows": len(data),
                "treatment_rate": float(pre_rows["treated"].mean()),
                "two_periods_per_id": bool((unit_counts == 2).all()),
                "invariant_unit_attributes": bool(invariant_ok),
                "post_treatment_effect_only": bool(treatment_effect_ok),
                "trend_x1_correlation": trend_x_corr,
                "trend_u_correlation": trend_u_corr,
                "u_allowed_for_estimation": False,
            }
        )

    return pd.DataFrame(rows)


def _untreated_trend(
    scenario: ScenarioName,
    x1: np.ndarray,
    x2: np.ndarray,
    u: np.ndarray,
    params: dict[str, float],
) -> np.ndarray:
    """Return the untreated period-1 minus period-0 trend component."""

    if scenario == "A":
        return np.full_like(x1, fill_value=params["lambda_time"], dtype=float)
    if scenario == "B":
        return params["lambda_time"] + params["kappa_1"] * x1 + params["kappa_2"] * x2
    if scenario == "C":
        return (
            params["lambda_time"]
            + params["kappa_1"] * x1
            + params["kappa_2"] * x2
            + params["delta_u"] * u
        )
    raise ValueError(f"Unknown scenario: {scenario!r}")


def _coerce_config(
    scenario: ScenarioName | DGPConfig,
    n: int | None,
    tau: float | None,
    seed: int | None,
    params: dict[str, float] | None,
) -> DGPConfig:
    """Accept either the direct function signature or a DGPConfig object."""

    if isinstance(scenario, DGPConfig):
        merged_params = dict(scenario.params or {})
        if params:
            merged_params.update(params)
        return DGPConfig(
            scenario=scenario.scenario,
            n=scenario.n,
            tau=scenario.tau,
            seed=scenario.seed,
            params=merged_params or None,
        )

    if scenario not in ("A", "B", "C"):
        raise ValueError("scenario must be one of 'A', 'B', or 'C'.")
    if n is None or tau is None or seed is None:
        raise ValueError("n, tau, and seed are required when scenario is a string.")
    return DGPConfig(scenario=scenario, n=n, tau=tau, seed=seed, params=params)


def _merge_params(overrides: dict[str, float] | None) -> dict[str, float]:
    """Merge baseline DGP parameters with optional overrides."""

    params = BASELINE_PARAMS.copy()
    if overrides:
        unknown = set(overrides).difference(params)
        if unknown:
            raise ValueError(f"Unknown DGP parameter(s): {sorted(unknown)}")
        params.update(overrides)
    return params


def _logistic(value: np.ndarray) -> np.ndarray:
    """Compute logistic probabilities."""

    return 1.0 / (1.0 + np.exp(-value))


def _safe_corr(left: pd.Series, right: pd.Series) -> float:
    """Return a correlation or NaN when either variable is constant."""

    if left.nunique() <= 1 or right.nunique() <= 1:
        return float("nan")
    return float(left.corr(right))


def _rng(seed: int) -> np.random.Generator:
    """Return a NumPy random generator for reproducibility."""

    return np.random.default_rng(seed)
