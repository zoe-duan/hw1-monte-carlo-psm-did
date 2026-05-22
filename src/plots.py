"""HW1 诊断和 Monte Carlo 结果绘图工具。"""

from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")
os.environ.setdefault("XDG_CACHE_HOME", "/tmp")
Path(os.environ["MPLCONFIGDIR"]).mkdir(parents=True, exist_ok=True)
Path(os.environ["XDG_CACHE_HOME"]).mkdir(parents=True, exist_ok=True)

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


def ensure_parent(path: str | Path) -> None:
    """必要时创建输出路径的父目录。"""

    Path(path).parent.mkdir(parents=True, exist_ok=True)


def plot_estimator_distributions(
    results: pd.DataFrame,
    tau: float = 2.0,
    output_dir: str | Path = "figures",
    suffix: str = "debug",
) -> dict[str, Path]:
    """Plot Monte Carlo estimator distributions, one figure per scenario.

    Args:
        results: Tidy Monte Carlo results with `scenario`, `estimator`,
            `estimate`, and `success` columns.
        tau: True treatment effect, shown as a vertical reference line.
        output_dir: Directory for saved PNG files.
        suffix: Filename suffix, e.g. `debug` or `final`.

    Returns:
        Mapping from scenario label to saved figure path.
    """

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    successful = results.copy()
    if "success" in successful.columns:
        successful = successful[successful["success"].astype(bool)]
    successful = successful[successful["estimate"].notna()]

    paths: dict[str, Path] = {}
    for scenario in sorted(successful["scenario"].dropna().unique()):
        subset = successful[successful["scenario"] == scenario]
        if subset.empty:
            continue
        path = output_path / f"scenario_{scenario}_estimator_distributions_{suffix}.png"
        plt.figure(figsize=(8, 5))
        estimators = list(subset["estimator"].dropna().unique())
        bins = _shared_bins(subset["estimate"], tau=tau)
        for estimator in estimators:
            estimates = subset.loc[subset["estimator"] == estimator, "estimate"]
            plt.hist(estimates, bins=bins, alpha=0.45, density=True, label=estimator)
        plt.axvline(tau, color="black", linestyle="--", linewidth=1.5, label=f"真实效应 = {tau}")
        plt.xlabel("估计值")
        plt.ylabel("密度")
        plt.title(f"估计量分布：场景 {scenario}")
        plt.legend()
        plt.tight_layout()
        plt.savefig(path, dpi=300)
        plt.close()
        paths[str(scenario)] = path
    return paths


def plot_common_support(
    support_data: pd.DataFrame,
    scenario: str,
    output_dir: str | Path = "figures",
    suffix: str = "debug",
) -> Path:
    """Plot estimated propensity-score distributions by treatment status.

    Args:
        support_data: Unit-level common-support data from
            `make_common_support_data`.
        scenario: Scenario label to plot.
        output_dir: Directory for saved PNG files.
        suffix: Filename suffix, e.g. `debug` or `final`.

    Returns:
        Saved figure path.
    """

    subset = support_data[support_data["scenario"] == scenario].copy()
    if subset.empty:
        raise ValueError(f"未找到场景 {scenario} 的共同支持数据。")

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    path = output_path / f"scenario_{scenario}_common_support_{suffix}.png"

    plt.figure(figsize=(8, 5))
    bins = np.linspace(0, 1, 31)
    for treated_value, label, color in [(1, "处理组", "#1f77b4"), (0, "控制组", "#ff7f0e")]:
        scores = subset.loc[subset["treated"] == treated_value, "propensity_score"]
        plt.hist(scores, bins=bins, alpha=0.45, density=True, label=label, color=color)

    common_min = subset["common_support_min"].iloc[0]
    common_max = subset["common_support_max"].iloc[0]
    plt.axvline(common_min, color="gray", linestyle=":", linewidth=1.2, label="共同支持边界")
    plt.axvline(common_max, color="gray", linestyle=":", linewidth=1.2)
    plt.xlabel("估计倾向得分")
    plt.ylabel("密度")
    plt.title(f"共同支持：场景 {scenario}")
    plt.legend()
    plt.tight_layout()
    plt.savefig(path, dpi=300)
    plt.close()
    return path


def plot_common_support_by_scenario(
    support_data: pd.DataFrame,
    output_dir: str | Path = "figures",
    suffix: str = "debug",
) -> dict[str, Path]:
    """为所有场景生成共同支持图。"""

    paths = {}
    for scenario in sorted(support_data["scenario"].dropna().unique()):
        paths[str(scenario)] = plot_common_support(
            support_data=support_data,
            scenario=str(scenario),
            output_dir=output_dir,
            suffix=suffix,
        )
    return paths


def plot_balance_smd(
    balance_table: pd.DataFrame,
    output_dir: str | Path = "figures",
    suffix: str = "debug",
) -> Path:
    """Plot before/after absolute standardized mean differences.

    Args:
        balance_table: Output from `make_balance_table` or concatenated scenario
            balance tables.
        output_dir: Directory for saved PNG file.
        suffix: Filename suffix.

    Returns:
        Saved figure path.
    """

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    path = output_path / f"balance_smd_{suffix}.png"

    plot_data = balance_table.copy()
    plot_data["label"] = plot_data["scenario"].astype(str) + ": " + plot_data["covariate"].astype(str)
    y_positions = np.arange(len(plot_data))
    height = 0.36

    plt.figure(figsize=(9, max(4.5, 0.45 * len(plot_data))))
    plt.barh(
        y_positions - height / 2,
        plot_data["abs_smd_before"],
        height=height,
        label="匹配前",
        color="#b0b0b0",
    )
    plt.barh(
        y_positions + height / 2,
        plot_data["abs_smd_after"],
        height=height,
        label="匹配后",
        color="#4c78a8",
    )
    plt.axvline(0.1, color="black", linestyle="--", linewidth=1, label="0.1 参考线")
    plt.yticks(y_positions, plot_data["label"])
    plt.xlabel("标准化均值差绝对值")
    plt.title("匹配前后的协变量平衡性")
    plt.legend()
    plt.tight_layout()
    plt.savefig(path, dpi=300)
    plt.close()
    return path


def _shared_bins(values: pd.Series, tau: float) -> np.ndarray:
    """创建包含真实效应的稳定直方图分箱。"""

    clean = values.dropna()
    lower = min(float(clean.min()), tau) - 0.25
    upper = max(float(clean.max()), tau) + 0.25
    if lower == upper:
        lower -= 0.5
        upper += 0.5
    return np.linspace(lower, upper, 26)
