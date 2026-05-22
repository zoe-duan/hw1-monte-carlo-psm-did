# HW1：PSM-DID Monte Carlo 模拟作业

本仓库是 HW1 的完整提交材料。作业主题是通过 Monte Carlo 模拟比较 PSM、DID、带协变量的 DID 和 PSM-DID，并评价一篇真实使用 PSM-DID 的应用论文。

本仓库保留 `AGENTS.md`，用于说明我如何要求 AI agent 协助项目。阶段性 prompt 没有单独放入 `prompts/` 文件夹，而是以完整原文形式记录在 `AI_USAGE_LOG.md` 的附录中。这样既保留了完整 AI 使用记录，也体现了本项目中的 AI 使用过程是逐步互动、审阅和修改的过程，而不是直接套用预制 prompt 库。

## 仓库结构

```text
.
├── AGENTS.md                         # AI agent 协作规则
├── AI_USAGE_LOG.md                   # 完整 AI 使用记录
├── ASSIGNMENT_CHECKLIST.md           # 作业要求自查清单
├── README.md                         # 复现说明
├── report.md                         # 最终报告
├── main.py                           # 运行入口
├── requirements.txt                  # Python 依赖
├── src/                              # DGP、估计器、Monte Carlo、诊断和绘图代码
├── tables/                           # final 和 debug 表格输出
├── figures/                          # final 和 debug 图形输出
├── references/                       # 论文候选和选定论文阅读笔记
└── logs/                             # 运行日志预留目录
```

## 环境安装

建议使用 Python 3.10 或更高版本。

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Windows 用户可以使用：

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## 运行 调试模式

调试模式用于快速检查代码管线，不用于最终报告。

```bash
python main.py --mode debug
```

调试设置为：

```text
N = 500
R = 20
```

生成的 调试输出带有 `_debug` 后缀。

## 运行 正式模式

正式模式用于复现报告中的正式结果。

```bash
python main.py --mode final
```

正式设置为：

```text
N = 1000
R = 500
tau = 2.0
scenarios = A, B, C
```

正式输出会保存在：

```text
tables/monte_carlo_results_final.csv
tables/monte_carlo_summary_final.csv
tables/balance_table_final.csv
tables/common_support_data_final.csv
tables/common_support_summary_final.csv
```

final 图形会保存在：

```text
figures/scenario_A_estimator_distributions_final.png
figures/scenario_B_estimator_distributions_final.png
figures/scenario_C_estimator_distributions_final.png
figures/scenario_A_common_support_final.png
figures/scenario_B_common_support_final.png
figures/scenario_C_common_support_final.png
figures/balance_smd_final.png
```

## 报告与 AI 使用说明

最终报告是：

```text
report.md
```

AI 使用记录是：

```text
AI_USAGE_LOG.md
```

报告中的数值来自 正式输出，不使用 调试结果。`AI_USAGE_LOG.md` 记录了项目规划、DGP 设计、代码实现、调试、论文筛选、证据提取、文字整理和最终审阅等阶段的 AI 辅助过程，以及我如何审阅和采纳这些输出。
