"""Monte Carlo runner and summary utilities."""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

from .dgp import ScenarioName, generate_data
from .estimators import (
    DEFAULT_COVARIATES,
    estimate_did,
    estimate_did_with_covariates,
    estimate_psm,
    estimate_psm_did,
)


@dataclass(frozen=True)
class MonteCarloConfig:
    """Configuration for a Monte Carlo run.

    This dataclass is retained for compatibility with earlier code. New code can
    call `run_monte_carlo()` directly with keyword arguments.
    """

    scenarios: tuple[ScenarioName, ...] = ("A", "B", "C")
    n: int = 1000
    tau: float = 2.0
    replications: int = 500
    seed: int = 12345
    covariates: tuple[str, ...] = DEFAULT_COVARIATES
    params: dict[str, float] | None = None
    matching_options: dict | None = None


def run_one_replication(
    scenario: ScenarioName,
    n: int,
    tau: float,
    seed: int,
    covariates: Iterable[str] = DEFAULT_COVARIATES,
    params: dict[str, float] | None = None,
    matching_options: dict | None = None,
) -> pd.DataFrame:
    """Run all estimators on one newly generated dataset.

    Args:
        scenario: DGP scenario label, A, B, or C.
        n: Number of units in this replication.
        tau: True constant treatment effect.
        seed: Replication-specific random seed. A new dataset is generated for
            every call.
        covariates: Observed pre-treatment covariates available to estimators.
        params: Optional DGP parameter overrides.
        matching_options: Optional arguments for PSM and PSM-DID, such as
            `replacement` and `caliper`.

    Returns:
        Tidy DataFrame with one row per estimator. Failed estimators are recorded
        with `success=False` and an `error` message rather than stopping the
        whole Monte Carlo run.
    """

    covariate_tuple = tuple(covariates)
    match_opts = dict(matching_options or {})
    data = generate_data(scenario, n=n, tau=tau, seed=seed, params=params)

    estimator_calls = [
        ("psm", lambda: estimate_psm(data, covariate_tuple, **match_opts)),
        ("did", lambda: estimate_did(data)),
        (
            "did_with_covariates",
            lambda: estimate_did_with_covariates(data, covariate_tuple),
        ),
        ("psm_did", lambda: estimate_psm_did(data, covariate_tuple, **match_opts)),
    ]

    rows: list[dict] = []
    for estimator_name, estimator_fn in estimator_calls:
        try:
            result = estimator_fn()
            rows.append(
                _row_from_estimator_result(
                    result=result,
                    scenario=scenario,
                    seed=seed,
                    n=n,
                    tau=tau,
                    params=params,
                    matching_options=match_opts,
                    success=True,
                    error="",
                )
            )
        except Exception as exc:  # noqa: BLE001 - record estimator failure in results.
            rows.append(
                _failure_row(
                    scenario=scenario,
                    estimator=estimator_name,
                    seed=seed,
                    n=n,
                    tau=tau,
                    covariates=covariate_tuple,
                    params=params,
                    matching_options=match_opts,
                    error=str(exc),
                )
            )
    return pd.DataFrame(rows)


def run_monte_carlo(
    scenarios: Iterable[ScenarioName] | MonteCarloConfig = ("A", "B", "C"),
    n: int = 1000,
    tau: float = 2.0,
    r: int = 500,
    seed: int = 12345,
    covariates: Iterable[str] = DEFAULT_COVARIATES,
    params: dict[str, float] | None = None,
    matching_options: dict | None = None,
) -> pd.DataFrame:
    """Run Monte Carlo simulations across scenarios and replications.

    Args:
        scenarios: Scenario labels or a `MonteCarloConfig` object.
        n: Number of units per replication.
        tau: True constant treatment effect used for bias/RMSE.
        r: Number of replications per scenario.
        seed: Base random seed.
        covariates: Observed pre-treatment covariates for estimators.
        params: Optional DGP parameter overrides.
        matching_options: Optional PSM/PSM-DID matching options.

    Returns:
        Tidy DataFrame with one row per scenario-replication-estimator result.
    """

    if isinstance(scenarios, MonteCarloConfig):
        config = scenarios
        scenarios = config.scenarios
        n = config.n
        tau = config.tau
        r = config.replications
        seed = config.seed
        covariates = config.covariates
        params = config.params
        matching_options = config.matching_options

    rows: list[pd.DataFrame] = []
    for scenario_index, scenario in enumerate(tuple(scenarios)):
        for replication in range(r):
            rep_seed = seed + 100_000 * (scenario_index + 1) + replication
            rep_results = run_one_replication(
                scenario=scenario,
                n=n,
                tau=tau,
                seed=rep_seed,
                covariates=covariates,
                params=params,
                matching_options=matching_options,
            )
            rep_results.insert(1, "replication", replication)
            rows.append(rep_results)

    if not rows:
        return pd.DataFrame()
    return pd.concat(rows, ignore_index=True)


def summarize_results(results: pd.DataFrame, tau: float) -> pd.DataFrame:
    """Summarize Monte Carlo estimates by scenario and estimator.

    The bias and RMSE are computed relative to the true treatment effect `tau`.
    Failed estimator rows are counted but excluded from estimate moments.
    """

    if results.empty:
        return pd.DataFrame()

    data = results.copy()
    data["estimate"] = pd.to_numeric(data["estimate"], errors="coerce")
    data["success"] = data["success"].astype(bool)
    data["warning_count_row"] = data["warnings"].apply(_count_warnings)
    successful = data[data["success"] & data["estimate"].notna()].copy()
    successful["squared_error"] = (successful["estimate"] - tau) ** 2

    keys = ["scenario", "estimator"]
    total = data.groupby(keys).size().reset_index(name="n_replications_total")
    failures = (
        data.assign(failed=~data["success"])
        .groupby(keys)["failed"]
        .sum()
        .reset_index(name="failure_count")
    )
    warnings = data.groupby(keys)["warning_count_row"].sum().reset_index(name="warning_count")

    moments = (
        successful.groupby(keys)
        .agg(
            n_replications_successful=("estimate", "size"),
            mean_estimate=("estimate", "mean"),
            sd=("estimate", "std"),
            mean_n_matched_treated=("n_matched_treated", "mean"),
            mean_n_unique_matched_controls=("n_unique_matched_controls", "mean"),
            mean_share_treated_outside_common_support=(
                "share_treated_outside_common_support",
                "mean",
            ),
            mean_squared_error=("squared_error", "mean"),
        )
        .reset_index()
    )
    summary = total.merge(moments, on=keys, how="left")
    summary = summary.merge(failures, on=keys, how="left")
    summary = summary.merge(warnings, on=keys, how="left")
    summary["bias"] = summary["mean_estimate"] - tau
    summary["rmse"] = summary["mean_squared_error"].apply(
        lambda value: math.sqrt(value) if pd.notna(value) else np.nan
    )

    ordered = [
        "scenario",
        "estimator",
        "n_replications_successful",
        "n_replications_total",
        "mean_estimate",
        "bias",
        "rmse",
        "sd",
        "mean_n_matched_treated",
        "mean_n_unique_matched_controls",
        "mean_share_treated_outside_common_support",
        "failure_count",
        "warning_count",
    ]
    return summary[ordered].sort_values(["scenario", "estimator"]).reset_index(drop=True)


def save_monte_carlo_outputs(
    results: pd.DataFrame,
    summary: pd.DataFrame,
    output_dir: str | Path = "tables",
    label: str = "debug",
) -> dict[str, Path]:
    """Save full Monte Carlo results and summary tables as CSV files.

    Args:
        results: Tidy row-level Monte Carlo results.
        summary: Scenario-estimator summary table.
        output_dir: Directory for CSV outputs.
        label: Filename suffix, e.g. `debug` or `final`.

    Returns:
        Paths to the saved result and summary files.
    """

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    results_path = output_path / f"monte_carlo_results_{label}.csv"
    summary_path = output_path / f"monte_carlo_summary_{label}.csv"
    results.to_csv(results_path, index=False)
    summary.to_csv(summary_path, index=False)
    return {"results": results_path, "summary": summary_path}


def _row_from_estimator_result(
    result: dict,
    scenario: ScenarioName,
    seed: int,
    n: int,
    tau: float,
    params: dict[str, float] | None,
    matching_options: dict,
    success: bool,
    error: str,
) -> dict:
    """Flatten one structured estimator result into a Monte Carlo row."""

    warnings = result.get("warnings") or []
    estimate = result.get("estimate", np.nan)
    return {
        "scenario": scenario,
        "seed": seed,
        "n": n,
        "tau": tau,
        "estimator": result.get("estimator"),
        "estimate": estimate,
        "bias": estimate - tau if pd.notna(estimate) else np.nan,
        "success": success,
        "error": error,
        "n_total": result.get("n_total"),
        "n_treated": result.get("n_treated"),
        "n_control": result.get("n_control"),
        "n_matched_treated": result.get("n_matched_treated"),
        "n_unique_matched_controls": result.get("n_unique_matched_controls"),
        "uses_matching": result.get("uses_matching"),
        "estimand": result.get("estimand"),
        "covariates": ",".join(result.get("covariates") or []),
        "uses_forbidden_variables": result.get("uses_forbidden_variables", False),
        "mean_match_distance": result.get("mean_match_distance"),
        "max_match_distance": result.get("max_match_distance"),
        "share_treated_outside_common_support": result.get(
            "share_treated_outside_common_support"
        ),
        "warnings": " | ".join(warnings),
        "model_formula": result.get("model_formula"),
        "params_overridden": bool(params),
        "matching_options": repr(matching_options),
    }


def _failure_row(
    scenario: ScenarioName,
    estimator: str,
    seed: int,
    n: int,
    tau: float,
    covariates: tuple[str, ...],
    params: dict[str, float] | None,
    matching_options: dict,
    error: str,
) -> dict:
    """Create a tidy row for an estimator failure."""

    return {
        "scenario": scenario,
        "seed": seed,
        "n": n,
        "tau": tau,
        "estimator": estimator,
        "estimate": np.nan,
        "bias": np.nan,
        "success": False,
        "error": error,
        "n_total": n,
        "n_treated": np.nan,
        "n_control": np.nan,
        "n_matched_treated": np.nan,
        "n_unique_matched_controls": np.nan,
        "uses_matching": estimator in {"psm", "psm_did"},
        "estimand": "ATT" if estimator in {"psm", "psm_did"} else "ATE/ATT under constant tau",
        "covariates": ",".join(covariates),
        "uses_forbidden_variables": False,
        "mean_match_distance": np.nan,
        "max_match_distance": np.nan,
        "share_treated_outside_common_support": np.nan,
        "warnings": "",
        "model_formula": "",
        "params_overridden": bool(params),
        "matching_options": repr(matching_options),
    }


def _count_warnings(value: object) -> int:
    """Count warning messages stored as a pipe-separated string."""

    if not isinstance(value, str) or not value.strip():
        return 0
    return len([part for part in value.split("|") if part.strip()])
