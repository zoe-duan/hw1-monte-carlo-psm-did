"""HW1 Monte Carlo 模拟的命令行入口。"""

from __future__ import annotations

import argparse

from src.diagnostics import make_balance_tables_by_scenario
from src.monte_carlo import run_monte_carlo, save_monte_carlo_outputs, summarize_results
from src.plots import (
    plot_balance_smd,
    plot_common_support_by_scenario,
    plot_estimator_distributions,
)


def main() -> None:
    """运行 debug 或 final Monte Carlo 管线。"""

    args = _parse_args()
    if args.mode == "debug":
        n = 500
        replications = 20
        label = "debug"
    else:
        n = 1000
        replications = 500
        label = "final"

    print(
        f"正在运行 {args.mode} Monte Carlo：scenarios=A,B,C, "
        f"N={n}, R={replications}, tau={args.tau}, seed={args.seed}"
    )
    if args.mode == "debug":
        print("debug 输出仅用于检查代码管线，不应作为最终报告结果。")
    else:
        print("final 模式可能需要更长时间。final 输出应在学生审阅后使用。")

    results = run_monte_carlo(
        scenarios=("A", "B", "C"),
        n=n,
        tau=args.tau,
        r=replications,
        seed=args.seed,
        covariates=("x1", "x2"),
    )
    summary = summarize_results(results, tau=args.tau)
    paths = save_monte_carlo_outputs(results, summary, output_dir="tables", label=label)
    diagnostics = make_balance_tables_by_scenario(
        scenarios=("A", "B", "C"),
        n=n,
        tau=args.tau,
        seed=args.seed,
        covariates=("x1", "x2"),
        output_dir="tables",
        suffix=label,
    )
    distribution_paths = plot_estimator_distributions(
        results,
        tau=args.tau,
        output_dir="figures",
        suffix=label,
    )
    support_paths = plot_common_support_by_scenario(
        diagnostics["support_data"],
        output_dir="figures",
        suffix=label,
    )
    balance_path = plot_balance_smd(
        diagnostics["balance"],
        output_dir="figures",
        suffix=label,
    )

    print(summary.to_string(index=False))
    print(f"\n完整结果已保存到 {paths['results']}")
    print(f"汇总结果已保存到 {paths['summary']}")
    print(f"平衡性表已保存到 {diagnostics['balance_path']}")
    print(f"共同支持数据已保存到 {diagnostics['support_data_path']}")
    print(f"共同支持汇总已保存到 {diagnostics['support_summary_path']}")
    for scenario, path in distribution_paths.items():
        print(f"场景 {scenario} 的估计量分布图已保存到 {path}")
    for scenario, path in support_paths.items():
        print(f"场景 {scenario} 的共同支持图已保存到 {path}")
    print(f"平衡性 SMD 图已保存到 {balance_path}")
    if args.mode == "debug":
        print("\n这些只是 debug 结果，不应写入最终报告。")


def _parse_args() -> argparse.Namespace:
    """解析命令行参数。"""

    parser = argparse.ArgumentParser(description="运行 HW1 Monte Carlo 模拟。")
    parser.add_argument(
        "--mode",
        choices=("debug", "final"),
        default="debug",
        help="debug 运行 N=500/R=20；final 运行 N=1000/R=500。",
    )
    parser.add_argument("--tau", type=float, default=2.0, help="真实处理效应。")
    parser.add_argument("--seed", type=int, default=20260501, help="基础随机种子。")
    return parser.parse_args()


if __name__ == "__main__":
    main()
