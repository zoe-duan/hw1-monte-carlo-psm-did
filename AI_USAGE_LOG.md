# AI 使用记录

## 总体说明

本作业使用 AI 工具辅助完成项目规划、DGP 设计讨论、代码框架和实现、调试、Monte Carlo 管线、诊断图表、应用论文筛选、证据提取、文字整理、最终审阅和语言修改。AI 工具没有替代我完成最终判断。所有代码、模拟设定、数值结果、论文评价和最终结论均由我审阅并负责。

本记录分为两部分：前半部分按阶段记录每轮 AI 互动的任务目标、AI 主要输出、我如何审阅和采纳，以及相关文件修改；后半部分以附录形式保存我实际发送给 AI agent 的完整关键 prompt 原文。这样既能快速查看每一阶段的采纳状态，也能满足完整 AI 使用记录的要求。

## 记录 1：项目规划与作业要求拆解

**工具：** AI coding agent / ChatGPT 类工具  
**阶段：** 项目规划  

**我的 提示词摘要：**  
要求 AI agent 阅读仓库中的 `AGENTS.md`、`README.md`、`ASSIGNMENT_CHECKLIST.md` 和作业页面，不要写代码或最终报告，只做作业目标理解、交付物映射、仓库结构检查、阶段性路线图、风险清单和下一步建议。

**AI 主要输出：**  
AI 将作业目标概括为：通过 Monte Carlo 构造可控的因果识别环境，比较 PSM、DID 和 PSM-DID 在不同假设下的表现。AI 还给出交付物映射、阶段性工作计划和识别风险清单。

**我的审阅与修改：**  
我接受该规划作为后续 DGP 设计的项目框架，但并未将其视为最终报告内容。

**涉及文件：**  
`AI_USAGE_LOG.md`

**采纳状态：**  
已由学生审阅，并作为下一步 DGP 设计的项目规划框架。

## 记录 2：DGP 设计讨论

**阶段：** 概念性 DGP 设计  

**我的 提示词摘要：**  
要求 AI agent 设计三个 Monte Carlo 场景：场景 A 使 DID 表现较好，场景 B 使 PSM-DID 优于简单 DID，场景 C 展示 PSM-DID 的失败边界；先写数学思路，不写代码。

**AI 主要输出：**  
AI 建议采用三个场景：

1. 场景 A：无条件平行趋势；
2. 场景 B：由可观测协变量驱动的趋势差异；
3. 场景 C：随时间变化的不可观测混淆。

AI 说明了每个场景中 PSM、DID、带协变量的 DID 和 PSM-DID 的理论预期。

**我的审阅与修改：**  
我接受该三场景框架，并要求后续将其形式化为可实现的数学 DGP。

**涉及文件：**  
`AI_USAGE_LOG.md`

**采纳状态：**  
已由学生审阅，并作为数学 DGP 形式化的概念框架。

## 记录 3：数学 DGP 形式化与参数校准

**阶段：** DGP 代码实现前的定稿  

**我的 提示词摘要：**  
要求 AI agent 以当前三场景框架为基础，明确 `x1`、`x2`、`alpha`、`u`、`treated`、`Y_i0`、`Y_i1(0)`、`Y_i1(1)`、真实处理效应和估计对象，并只实现 `src/dgp.py`。

**AI 主要输出：**  
AI 实现了三个 DGP：

- 场景 A：未处理趋势为共同趋势；
- 场景 B：未处理趋势依赖 `x1` 和 `x2`；
- 场景 C：未处理趋势还依赖不可观测变量 `u`。

AI 还加入了 合理性检查，确认每个个体有两期记录、处理只在 处理后时期生效、处理率处于合理范围。

**我的审阅与修改：**  
我接受常数处理效应 `tau = 2.0`、long format 输出、`alpha` 和 `u` 只用于诊断、匹配变量只使用 `x1` 和 `x2`。

**涉及文件：**  
`src/dgp.py`、`AI_USAGE_LOG.md`

**采纳状态：**  
已由学生审阅，并作为估计器实现的工作 DGP 设计。

## 记录 4：估计器实现

**阶段：** PSM、DID、带协变量的 DID 和 PSM-DID 实现  

**我的 提示词摘要：**  
要求 AI agent 实现四个估计器，禁止使用 `alpha` 和 `u`，禁止使用处理后变量匹配，并强调 带协变量的 DID 应使用差分结果规格，而不是在 长格式 DID 中只加入时间不变协变量主效应。

**AI 主要输出：**  
AI 在 `src/estimators.py` 中实现：

1. `estimate_psm`：处理后结果的匹配比较；
2. `estimate_did`：`Delta Y_i ~ treated`；
3. `estimate_did_with_covariates`：`Delta Y_i ~ treated + x1 + x2`；
4. `estimate_psm_did`：先匹配，再比较匹配个体的 `Delta Y`。

AI 还实现了 forbidden variable 检查，防止估计器使用 `u`、`alpha` 或结果变量。

**我的审阅与修改：**  
我接受结构化 dict 返回格式、默认放回匹配、PSM-DID 的 ATT 风格解释和 forbidden variable 检查。

**涉及文件：**  
`src/estimators.py`、`AI_USAGE_LOG.md`

**采纳状态：**  
已由学生审阅，并作为 Monte Carlo 集成的估计器实现。

## 记录 5：Monte Carlo 管线与 调试运行

**阶段：** Monte Carlo runner 和汇总表实现  

**我的 提示词摘要：**  
要求 AI agent 实现 `run_one_replication`、`run_monte_carlo`、`summarize_results` 和输出保存函数，使其适配估计器的 结构化字典 返回格式。只运行小规模 debug，不运行 final。

**AI 主要输出：**  
AI 实现 Monte Carlo 管线：每次 replication 重新生成数据，运行四个估计器，记录 estimate、bias、metadata、警告 和 failures。汇总表计算 平均估计值、bias、RMSE、标准差、匹配样本信息和失败数量。

**调试设置：**  
`N = 500`，`R = 20`，`tau = 2.0`。

**调试结果摘要：**  
场景 A 中 DID 和 PSM-DID 接近 2；场景 B 中简单 DID 偏高，而 带协变量的 DID 和 PSM-DID 接近 2；场景 C 中 带协变量的 DID 和 PSM-DID 只部分改善但仍有偏。调试结果只用于管线检查。

**我的审阅与修改：**  
我接受 Monte Carlo 管线和 debug pattern，但明确 调试结果不能进入最终报告。

**涉及文件：**  
`src/monte_carlo.py`、`main.py`、`AI_USAGE_LOG.md`、debug 表格输出。

**采纳状态：**  
已由学生审阅，并作为诊断和绘图阶段的 Monte Carlo 管线。

## 记录 6：诊断与绘图

**阶段：** 平衡性、共同支持和估计量分布图  

**我的 提示词摘要：**  
要求 AI agent 实现匹配前后平衡性表、共同支持数据和共同支持图、估计量分布图、SMD 平衡性图，并通过 调试模式检查输出。

**AI 主要输出：**  
AI 实现或确认以下内容：

- `balance_table_debug.csv` 和 `balance_table_final.csv` 的生成逻辑；
- 共同支持数据和汇总表；
- 场景 A/B/C 的估计量分布图；
- 场景 A/B/C 的共同支持图；
- 匹配前后 SMD 图。

**debug 诊断摘要：**  
场景 B 中匹配显著改善 `x1` 和 `x2` 的 SMD；共同支持未崩坏；调试输出均带 `_debug` 后缀。

**我的审阅与修改：**  
我接受诊断和绘图管线作为 正式输出生成基础。

**涉及文件：**  
`src/diagnostics.py`、`src/plots.py`、`main.py`、`AI_USAGE_LOG.md`、debug 图表和表格。

**采纳状态：**  
已由学生审阅，并作为 正式输出 generation 的诊断与绘图管线。

## 记录 7：正式 Monte Carlo 运行与 正式输出生成

**阶段：** final run  

**我的 提示词摘要：**  
要求 AI agent 使用 正式设置运行 `python main.py --mode final`，生成 正式 Monte Carlo 表格、诊断表和图形，并验证行数、成功次数、警告 和数值一致性。

**正式设置：**  

```text
scenarios = A, B, C
N_final = 1000
R_final = 500
tau = 2.0
matching covariates = x1, x2
matching = nearest-neighbor propensity score matching with 放回匹配
seed = 20260501
```

**AI 主要输出：**  
AI 运行 final mode，生成：

- `tables/monte_carlo_results_final.csv`
- `tables/monte_carlo_summary_final.csv`
- `tables/balance_table_final.csv`
- `tables/common_support_data_final.csv`
- `tables/common_support_summary_final.csv`
- final 估计量分布图、共同支持图和 SMD 图。

**验证结果：**  
`monte_carlo_results_final.csv` 有 6000 条结果；`monte_carlo_summary_final.csv` 有 12 行；每个 scenario-estimator 组合有 500 次成功结果；missing、failures 和 警告 均为 0。

**我的审阅与修改：**  
我接受这些 正式输出 作为报告写作基础。

**涉及文件：**  
final 表格、final 图形、`AI_USAGE_LOG.md`。

**采纳状态：**  
已由学生审阅，并作为报告写作的最终模拟结果基础。

## 记录 8：应用 PSM-DID 论文初步筛选

**阶段：** 论文候选筛选  

**我的 提示词摘要：**  
要求 AI agent 搜索真实使用 PSM-DID 的经济学、金融、管理、公共政策、劳动、产业组织、环境经济学或相关领域论文，给出 3 篇候选，并说明处理变量、结果变量、识别优势和风险。

**AI 主要输出：**  
AI 初步给出 Su et al. (2025)、Tian et al. (2024)、Ying et al. (2025) 等候选，并推荐 Su et al. (2025)。

**我的审阅与修改：**  
我认为 PLOS ONE / Heliyon 属于综合性期刊，虽然方法细节较多，但与课程要求中的经济学相关期刊不完全匹配，因此要求 AI agent 补强候选池。

**涉及文件：**  
`references/paper_candidates.md`、`AI_USAGE_LOG.md`

**采纳状态：**  
初步候选仅作为备选，不作为最终选择。

## 记录 9：论文候选补强与领域匹配检查

**阶段：** 重新检索经济学相关候选  

**我的 提示词摘要：**  
要求 AI agent 保留上一轮候选但重新评估期刊领域匹配度，并补充更符合经济学、管理、公共政策、环境经济学等领域的 PSM-DID 论文。

**AI 主要输出：**  
AI 补充了 Jin (2024)、Luo et al. (2023)、Fu et al. (2021)、Huang et al. (2022)、Yuan et al. (2023) 等候选，并将 Jin (2024) 排名第一。

**我的审阅与修改：**  
我选择 Jin (2024) 作为最终应用论文评价对象，因为它属于区域/商业经济学相关领域，处理变量和结果变量清楚，且可以与本项目场景 B 和场景 C 直接联系。

**涉及文件：**  
`references/paper_candidates.md`、`AI_USAGE_LOG.md`

**采纳状态：**  
已由学生审阅。Jin (2024) 被选为应用 PSM-DID 论文评价对象。

## 记录 10：选定论文初步证据提取

**阶段：** Jin (2024) 阅读笔记  

**我的 提示词摘要：**  
要求 AI agent 阅读 Jin (2024) 的 DOI 页面、可访问全文或 PDF，提取引用信息、研究设计、处理变量、结果变量、PSM-DID 细节、DID 诊断和识别风险。不能猜测未核实内容。

**AI 主要输出：**  
AI 提取出论文基本信息、研究问题、高铁可达性处理、企业经营成本结果变量、企业—年份观测、PSM-DID 作用、共同支持和平衡性等信息。AI 同时标注了尚未核实的内容，如精确匹配算法、协变量时间顺序、事件研究规格和 安慰剂 设计。

**我的审阅与修改：**  
我要求进一步核实未确认的方法细节，避免正式报告中过度断言。

**涉及文件：**  
`references/selected_paper_notes.md`、`AI_USAGE_LOG.md`

**采纳状态：**  
初步证据提取已审阅，但由于仍有未核实项，未直接进入最终评价。

## 记录 11：选定论文未核实项补证

**阶段：** Jin (2024) 证据补强  

**我的 提示词摘要：**  
要求 AI agent 重点核实匹配算法、匹配变量及时间、共同支持、平衡性检验、平行趋势 / 事件研究、安慰剂检验、固定效应、标准误聚类和异质性分析。

**AI 主要输出：**  
AI 核实了：

- 倾向得分由 Logit 模型估计；
- 匹配变量包括人均 GDP、第二产业占比、FDI 产出占比、互联网普及率和人口密度；
- 论文检查共同支持并剔除 共同支持之外 样本；
- 平衡性表显示 Pseudo R2、mean bias、median bias 显著下降；
- 论文在较高层面报告平行趋势和 安慰剂 检验；
- 报告区域固定效应、时间固定效应、行业控制和按企业聚类的 t 统计量。

AI 也明确保留了未核实内容：精确匹配算法、卡尺、放回与否、协变量严格处理前时间、事件研究 规格、安慰剂 设计和部分固定效应细节。

**我的审阅与修改：**  
我接受这些笔记作为正式评价的证据基础，并要求最终报告保留谨慎表述。

**涉及文件：**  
`references/selected_paper_notes.md`、`AI_USAGE_LOG.md`

**采纳状态：**  
已由学生审阅，并作为应用论文评价写作的证据基础，未核实项保留为限制。

## 记录 12：报告结构与文字整理

**阶段：** `report.md` 结构组织和文字整理  

**我的 提示词摘要：**  
要求 AI agent 基于 正式输出和选定论文笔记，协助整理中文课程报告的章节结构和表述，包括引言、识别背景、Monte Carlo 设计、估计方法、模拟结果、诊断、解释、应用论文评价、结论、AI 使用说明和参考文献。

**AI 主要输出：**  
AI 协助组织 `report.md` 的结构和文字，纳入 正式 Monte Carlo 数值、final 图表、Jin (2024) 评价，并在论文评价中保留未核实项限制。

**我的审阅与修改：**  
我要求后续进行严格 final review，检查数值、debug/final 文件引用、论文未核实细节、AI 使用说明和复现性。

**涉及文件：**  
`report.md`、`AI_USAGE_LOG.md`

**采纳状态：**  
报告结构和文字整理结果已生成，但需经过最终审查。

## 记录 13：最终审阅与修订

**阶段：** 提交前严格检查  

**我的 提示词摘要：**  
要求 AI agent 按严格助教标准检查整个仓库：作业要求、数值一致性、调试输出与正式输出、论文评价谨慎性、代码复现性、README 和 checklist。

**AI 主要输出：**  
AI 检查了 `report.md`、正式 CSV、图表、代码、README、checklist、AI log 和论文笔记。它确认 final summary 与报告三位小数一致、没有引用 调试结果、final 表图存在且非空、代码可通过轻量检查。

**修订内容：**  
AI 在报告表格中加入 Monte Carlo 标准差，补充 treatment assignment 数学设定，更新 README 为复现说明，更新 checklist，并调整最终责任声明为学生确认前草稿。

**我的审阅与修改：**  
我接受该阶段的技术性检查结果，但随后又要求对报告公式、AI log 状态错位、README 语气和论文评价表达进行进一步清理。

**涉及文件：**  
`report.md`、`README.md`、`ASSIGNMENT_CHECKLIST.md`、`AI_USAGE_LOG.md`

**采纳状态：**  
已由学生审阅，并完成修改。


## 记录 14：提交前事实修订与完整 Prompt 补录

**阶段：** 提交前补充修订  

**我的完整要求：**  
在重新核对作业网页和压缩包后，确认需要完成四项修改：修正 Jin (2024) 结果变量表述、在论文评价中明确 ATT/ATE、清理压缩包中的 macOS 临时文件，并将 AI 使用记录中的 prompt 由摘要改为实际使用的完整 prompt 原文。

**AI 主要输出：**  
AI 根据审阅意见修改 `report.md` 和 `references/selected_paper_notes.md` 中 Jin (2024) 的结果变量表述，将其改为固定成本、可变成本和总经营成本；在 `report.md` 的论文评价部分补充 PSM-DID 更接近匹配后处理组 ATT 而非总体 ATE；更新 `README.md`，说明完整 prompt 原文已记录在 `AI_USAGE_LOG.md` 附录；并在本文件末尾加入完整关键 prompt 原文。

**我的审阅与修改：**  
我要求完整保留 prompt 原文，而不是只保留摘要，以满足课程对完整 AI 使用记录的要求。

**涉及文件：**  
`report.md`、`references/selected_paper_notes.md`、`README.md`、`AI_USAGE_LOG.md`

**采纳状态：**  
已由学生要求执行。

## 附录：完整关键 Prompt 原文

以下为本作业过程中实际用于引导 AI agent 的阶段性关键 prompt 原文。部分日常追问、简短确认或非实质性对话未单独列入，但所有对项目设计、代码、结果、论文评价和报告有实质影响的 prompt 均保留在此处。

### Prompt 1：项目规划与仓库检查

~~~text
请先阅读本仓库根目录下的 `AGENTS.md`、`README.md`、`ASSIGNMENT_CHECKLIST.md` 和 `AI_USAGE_LOG.md`。然后阅读作业页面：  
https://zhiyuanryanchen.github.io/ml-causal-website/Assignments/assignment01_psm_did_monte_carlo.html

现在不要写最终报告，不要实现完整代码，也不要编造任何模拟结果或论文信息。你的第一个任务是帮我做项目规划和仓库检查。

请完成以下内容：

1. 用你自己的话总结这次 HW1 真正考察什么，而不是只复述题目。
2. 把作业要求映射到本仓库应交付的文件，例如 `report.md`、`main.py`、`src/`、`tables/`、`figures/`、`references/`、`AI_USAGE_LOG.md`。
3. 检查当前仓库结构是否适合完成作业。如果有缺失，只提出建议，不要大规模改文件。
4. 给出完成作业的阶段性路线图，至少包括：
   - DGP 设计；
   - PSM、DID、PSM-DID 估计实现；
   - Monte Carlo 运行；
   - 平衡性和共同支持诊断；
   - 结果解释；
   - PSM-DID 论文选择与评价；
   - 报告写作；
   - 最终复核。
5. 明确指出每个阶段哪些判断必须由我自己确认，因为我需要对最终代码、结果解释和论文评价负责。
6. 列出这次作业最容易出错的地方，尤其关注：
   - 是否错误使用处理后变量匹配；
   - 是否把 PSM-DID 误解释成一定估计 ATE；
   - DID 平行趋势假设是否被误用；
   - 共同支持不足如何影响偏误和方差；
   - Monte Carlo bias 和 RMSE 是否正确计算；
   - 是否可能出现看起来结果很好但识别逻辑错误的情况。
7. 最后提出“下一步 DGP 设计阶段”我应该让你做什么，但不要直接进入下一阶段。

文件修改规则：

- 你现在不要修改 `report.md`、`main.py` 或 `src/` 中的代码。
- 如果你能编辑文件，请只更新 `AI_USAGE_LOG.md`，自动添加本次互动的记录草稿。
- 在 `AI_USAGE_LOG.md` 中必须标明：
  - 本次 prompt 的摘要；
  - 你的主要输出摘要；
  - 哪些内容仍然需要我审核；
  - 采纳状态写成 `Pending student review`，不要替我写成“已确认”或“已采纳”。
- 如果你不能编辑文件，请在回复末尾生成一段我可以复制进 `AI_USAGE_LOG.md` 的日志条目。

输出格式请使用：

## 1. Assignment Understanding  
## 2. Deliverables Mapping  
## 3. Repository Check  
## 4. Work Plan  
## 5. Decisions I Must Make  
## 6. Risk List  
## 7. Next Prompt Recommendation  
## 8. AI Usage Log Entry
~~~

### Prompt 2：DGP 设计阶段

~~~text
很好。现在进入 **DGP 设计阶段**。

请先不要写代码，不要修改 `main.py`、`src/` 或 `report.md`。你的任务是帮我设计这次 Monte Carlo 的三个核心场景，并解释每个场景背后的识别逻辑。

请设计 Scenario A、Scenario B、Scenario C，每个场景都必须包含：

1. 场景名称；
2. 这个场景想检验的识别问题；
3. 处理前协变量 \(X_i\) 的生成方式；
4. 是否包含个体固定异质性 \(\alpha_i\)；
5. 是否包含时间冲击或趋势项；
6. 处理变量 \(D_i\) 的生成机制；
7. 处理前结果 \(Y_{i0}\) 的生成方程；
8. 处理后未处理潜在结果 \(Y_{i1}(0)\) 的生成方程；
9. 处理后已处理潜在结果 \(Y_{i1}(1)\) 的生成方程；
10. 真实处理效应 \(\tau\)；
11. 目标估计量更接近 ATT 还是 ATE；
12. 在这个场景下，PSM、DID、DID with covariates、PSM-DID 理论上应该表现如何；
13. 这个场景对应作业中的哪个要求。

三个场景必须满足：

- **Scenario A：DID 表现较好。**  
  这个场景应满足无条件平行趋势，使得简单 DID 应该低偏。PSM-DID 可以接近 DID，但不应该被设计成明显“神奇更好”。

- **Scenario B：PSM-DID 可能优于简单 DID。**  
  这个场景应让处理分配依赖处理前协变量 \(X_i\)，并且 untreated trend 也依赖 \(X_i\)。因此，处理组和控制组因为 \(X_i\) 分布不同而有不同趋势；匹配后再做 DID 应该更合理。

- **Scenario C：PSM-DID 也会失败。**  
  这个场景必须展示 PSM-DID 的边界。你可以选择以下失败机制之一作为主方案：
  - 时间变化的不可观测混淆；
  - 共同支持不足；
  - 错误匹配变量；
  - 同期政策冲击。
  
  请推荐一个最适合作业展示的失败机制，并说明为什么。

额外要求：

1. 请用清楚的数学表达写出每个 DGP，但不要写代码。
2. 不要为了让 PSM-DID 总是最好而设计场景。
3. 请指出每个场景中哪些识别假设成立，哪些不成立。
4. 请说明每个场景最终应画哪些图、报告哪些表。
5. 请指出哪些参数需要我确认，例如 \(N\)、重复次数 \(R\)、\(\tau\)、协变量数量、处理概率强度、噪声大小等。
6. 请给出你推荐的最终三场景组合，但采纳状态仍应是 `Pending student review`。

文件修改规则：

- 现在不要修改代码和报告。
- 只允许更新 `AI_USAGE_LOG.md`，为本次 DGP 设计互动添加一条记录草稿。
- 日志中必须写明：
  - 本次 prompt 摘要；
  - 你提出的 DGP 方案摘要；
  - 哪些参数和设计仍需我确认；
  - 采纳状态写成 `Pending student review`。
- 不要替我写“我已经确认”或“最终采用”。

输出格式请使用：

## 1. Design Goal  
## 2. Scenario A: DID Works  
## 3. Scenario B: PSM-DID Improves DID  
## 4. Scenario C: PSM-DID Fails  
## 5. Comparison Across Estimators  
## 6. Parameters I Need to Confirm  
## 7. Recommended Final Design  
## 8. AI Usage Log Update
~~~

### Prompt 3：DGP 形式化与参数校准

~~~text
很好。你提出的三场景 DGP 逻辑我总体接受，但在进入完整 estimator 实现前，我要先做 **DGP 定稿和参数校准**。

请先阅读当前 `src/dgp.py`、`main.py`、`README.md`、`AGENTS.md` 和 `AI_USAGE_LOG.md`。然后只处理 DGP 部分，不要实现完整 PSM、DID、PSM-DID 估计器，不要写最终报告结果，不要编造模拟结果。

我现在确认采用以下三场景框架：

1. **Scenario A: Unconditional Parallel Trends**  
   treatment selection 可以依赖 \(X_i\) 和 time-invariant \(\alpha_i\)，但 untreated trend 只包含共同趋势 \(\lambda\)。这个场景用于展示 DID 在无条件平行趋势成立时表现好。

2. **Scenario B: Covariate-Driven Trend Differences**  
   treatment selection 依赖 \(X_i\) 和 \(\alpha_i\)，untreated trend 依赖 \(X_i\)。这个场景用于展示 simple DID 因为 \(X_i\) 分布不平衡而有偏，而 PSM-DID 或 DID with covariates 可以改善。

3. **Scenario C: Time-Varying Unobserved Confounding**  
   treatment selection 和 untreated trend 都依赖不可观测变量 \(U_i\)。估计时不能使用 \(U_i\)。这个场景用于展示 observed covariates 平衡之后，PSM-DID 仍可能因为 unobserved time-varying confounding 而失败。

请完成以下任务：

## 1. Formalize the DGP

请把三个场景写成统一、清楚、可实现的数学设定。每个场景都要明确：

- \(X_{i1}\)
- \(X_{i2}\)
- \(\alpha_i\)
- 如果有，\(U_i\)
- \(D_i\)
- \(Y_{i0}\)
- \(Y_{i1}(0)\)
- \(Y_{i1}(1)\)
- observed \(Y_{it}\)
- true treatment effect \(\tau\)
- target estimand 是 ATT 还是 ATE

请注意：因为我们使用 constant treatment effect，所以 ATT 和 ATE 数值相同；但报告中仍应说明 matching-based estimators 在解释上更接近 ATT。

## 2. Confirm Baseline Parameters

请先采用以下 baseline 参数，除非你发现明显问题：

```text
N_debug = 500
N_final = 1000
R_debug = 20 or 50
R_final = 500
tau = 2.0
beta_0 = 1.0
beta_1 = 1.0
beta_2 = 0.5
sigma_alpha = 1.0
sigma_epsilon = 1.0
lambda_time = 1.0
kappa_1 = 0.8
kappa_2 = 0.6
delta_u = 1.0
gamma_0 = -0.3
gamma_1 = 0.8
gamma_2 = 0.6
gamma_alpha = 0.5
gamma_u = 0.8
```

请检查这些参数是否可能导致 treatment rate 太极端。如果 treatment rate 不在大约 30%-70%，请建议如何调整 intercept `gamma_0`，但不要为了让结果好看而过度调参。

## 3. Implement Only `src/dgp.py`

如果当前 `src/dgp.py` 只是骨架，请实现或修改 DGP 生成函数。建议函数接口保持类似：

```python
generate_data(scenario: str, n: int, tau: float, seed: int, params: dict | None = None) -> pandas.DataFrame
```

输出数据至少应包含：

```text
id
scenario
treated
post
time
y
y0
y1_potential
x1
x2
alpha
u
propensity_true
```

但请注意：

- `u` 可以保存在模拟数据里，方便 Monte Carlo 诊断；  
- 估计器默认不能使用 `u`；  
- 估计器也不能使用 `alpha`，除非只是 simulation diagnostic；  
- matching covariates 只能是处理前可观测变量，例如 `x1`, `x2`。

请考虑同时生成 wide-format 和 long-format 是否有必要。如果你只返回 long-format，请保证每个个体有两期记录，并且后续可以方便计算 \(\Delta Y_i = Y_{i1} - Y_{i0}\)。

## 4. Add a Small Sanity Check

请添加或保留一个轻量 sanity check，可以在 debug 模式下检查：

- 每个 scenario 的 treatment rate；
- 每个 scenario 是否每个 id 有两期；
- `x1`, `x2`, `treated` 是否在同一个个体两期内保持不变；
- treatment 只在 post period 生效；
- Scenario A 的 untreated trend 不依赖 \(X_i\)；
- Scenario B 的 untreated trend 依赖 \(X_i\)；
- Scenario C 的 untreated trend 依赖 \(U_i\)，但 `u` 标记为 not allowed for estimation。

不要运行 500 次 Monte Carlo。只做小规模 sanity check。

## 5. Important Estimator Reminder for Later

现在还不要实现 estimator，但请在你的说明里明确记下：

- DID with covariates 不能只是把 time-invariant \(X_i\) 作为普通主效应加入 long-format DID。
- 正确做法应是：
  - 使用 differenced outcome：\(\Delta Y_i = a + \tau D_i + \theta_1 X_{i1} + \theta_2 X_{i2} + e_i\)，或
  - 在 long-format 中加入 \(post \times X_i\) 交互项。
- PSM-DID 应先基于处理前 \(X_i\) 匹配，然后在匹配样本上比较 \(\Delta Y_i\) 或估计 DID。

## 6. File Modification Rules

你现在可以修改：

- `src/dgp.py`
- 如有必要，`main.py` 中的 very small debug call
- `AI_USAGE_LOG.md`

你现在不要修改：

- `src/estimators.py`
- `src/monte_carlo.py`
- `src/diagnostics.py`
- `src/plots.py`
- `report.md` 中的正式结果部分

如果你认为必须修改其他文件，请先说明理由。

## 7. AI Usage Logging

请自动更新 `AI_USAGE_LOG.md`，新增一条本次 DGP formalization / parameter calibration 的记录。

日志中必须包含：

- 本次 prompt 摘要；
- 你实际修改了哪些文件；
- 最终 DGP 方案摘要；
- 参数设置摘要；
- sanity check 结果摘要；
- 哪些内容仍需我审核；
- 采纳状态写成 `Pending student review`，不要替我写“已确认最终采用”。

## 8. Output Format

请按以下格式回复：

### 1. DGP Formalization Summary
### 2. Parameter Choices and Treatment Rate Check
### 3. Files Modified
### 4. Sanity Check Results
### 5. Estimator Warning for Later
### 6. Remaining Student Review Items
### 7. AI Usage Log Update
~~~

### Prompt 4：估计器实现

~~~text
很好。我已经审核并接受当前三场景 DGP 作为后续实现基础：

- Scenario A: Unconditional Parallel Trends
- Scenario B: Covariate-Driven Trend Differences
- Scenario C: Time-Varying Unobserved Confounding

我接受以下设计选择：

1. 使用 constant treatment effect，\(\tau = 2.0\)；
2. 当前 treatment rates 在合理范围内，不调整 `gamma_0`；
3. 保留 long-format 数据结构；
4. 保留 `alpha` 和 `u` 作为 simulation diagnostics，但估计器不能使用它们；
5. 后续 matching covariates 只能使用处理前可观测变量 `x1` 和 `x2`；
6. Scenario C 中 untreated trend 同时依赖 observed \(X_i\) 和 unobserved \(U_i\)。这可以展示 DID with covariates 可能部分改善，但 PSM-DID 仍会因为不可观测 time-varying confounding 而失败。

现在进入 **estimator implementation 阶段**。

请先阅读：

- `src/dgp.py`
- `src/estimators.py`
- `AGENTS.md`
- `AI_USAGE_LOG.md`

本阶段请只实现或修改 estimator 相关逻辑，不要运行 500 次 Monte Carlo，不要写最终报告结果，不要编造任何模拟结果。

## 1. Update Previous AI Log Status

请先在 `AI_USAGE_LOG.md` 中把上一条 DGP formalization 记录的采纳状态从 `Pending student review` 更新为类似：

```text
Reviewed by student and accepted as the working DGP design for estimator implementation.
```

不要写成“最终论文已确认”，只表示我接受它作为下一步代码实现基础。

## 2. Implement Estimators in `src/estimators.py`

请实现以下四类 estimator。所有 estimator 都应只使用允许的变量，不得使用 `alpha` 或 `u`，不得使用处理后变量做 propensity score matching。

### Estimator 1: PSM-only

定义：

- 使用处理前可观测变量 `x1`, `x2` 估计 propensity score；
- 对 treated units 匹配 control units；
- 使用 post-period outcome \(Y_{i1}\) 比较 treated 和 matched controls；
- 返回 matched treated-control post outcome difference。

请明确说明：这个 estimator 是 cross-sectional matching estimator，不使用 DID，因此在存在未观测 time-invariant heterogeneity \(\alpha_i\) 时可能有偏。

### Estimator 2: Simple DID

使用个体层面的差分结果：

\[
\Delta Y_i = Y_{i1} - Y_{i0}
\]

估计：

\[
\Delta Y_i = a + \tau D_i + e_i
\]

返回 \(D_i\) 的系数。

### Estimator 3: DID with Covariates

请不要犯下面这个错误：

```text
long-format DID 回归里只加入 time-invariant x1, x2 主效应
```

正确做法使用 differenced outcome：

\[
\Delta Y_i = a + \tau D_i + \theta_1 X_{i1} + \theta_2 X_{i2} + e_i
\]

或者等价地，在 long-format DID 中加入 `post × x1` 和 `post × x2`。本项目优先使用 differenced outcome 版本，代码更清楚。

返回 \(D_i\) 的系数。

### Estimator 4: PSM-DID

步骤：

1. 使用处理前可观测变量 `x1`, `x2` 估计 propensity score；
2. 对 treated units 匹配 control units；
3. 在 matched sample 或 matched pairs 上计算：

\[
\widehat{ATT}_{PSM-DID}
=
\frac{1}{N_T}
\sum_{i:D_i=1}
\left[
\Delta Y_i -
\Delta Y_{m(i)}
\right]
\]

其中 \(m(i)\) 是 matched control unit。

返回 matched pair difference 的平均值。

请说明：这个 estimator 在解释上更接近 ATT。

## 3. Matching Implementation Requirements

请使用清楚、可复现的 nearest-neighbor matching。

要求：

- propensity score model 使用 logistic regression；
- covariates 默认为 `["x1", "x2"]`；
- matching 默认可以使用 replacement；
- 可以支持 optional caliper，但如果实现 caliper，请清楚返回被保留的 treated 数量；
- 不要使用 `alpha`、`u`、`y`、`y0`、`y1_potential`、`untreated_trend` 等变量估计 propensity score；
- 如果 overlap 极差，函数要给出清楚 warning 或返回 diagnostic metadata，而不是静默失败。

## 4. Helper Functions

请根据需要实现辅助函数，例如：

```python
make_wide_panel(data)
estimate_propensity_scores(wide_data, covariates)
nearest_neighbor_match(wide_data, propensity_col="propensity_score", replacement=True, caliper=None)
estimate_psm(data, covariates=("x1", "x2"), ...)
estimate_did(data)
estimate_did_with_covariates(data, covariates=("x1", "x2"))
estimate_psm_did(data, covariates=("x1", "x2"), ...)
estimate_all(data, covariates=("x1", "x2"))
```

每个函数需要有 docstring，说明：

- 输入；
- 输出；
- 是否使用 long format 或 wide format；
- 是否返回 ATT；
- 哪些变量禁止用于估计。

## 5. Return Format

每个 estimator 不要只返回一个数字。请返回结构化结果，例如 dict：

```python
{
    "estimator": "psm_did",
    "estimate": ...,
    "n_total": ...,
    "n_treated": ...,
    "n_control": ...,
    "n_matched_treated": ...,
    "n_unique_matched_controls": ...,
    "covariates": ["x1", "x2"],
    "uses_matching": True,
    "estimand": "ATT"
}
```

Simple DID 和 DID with covariates 也可以返回类似结构。

## 6. Add Small Estimator Sanity Check

请添加轻量 sanity check，不是最终 Monte Carlo。

可以使用当前 `generate_data()` 对每个 scenario 生成 `n=500` 的单次数据，然后运行四个 estimators，输出：

- estimate；
- n_treated；
- n_control；
- n_matched_treated；
- 是否使用 forbidden variables；
- 是否所有 estimator 正常运行。

请注意：这个 sanity check 结果不能写进最终报告，只用于代码检查。

## 7. File Modification Rules

你现在可以修改：

- `src/estimators.py`
- 如有必要，可以对 `main.py` 加一个 very small debug call，但不要运行完整 Monte Carlo；
- `AI_USAGE_LOG.md`

不要修改：

- `src/dgp.py`，除非发现 estimator 无法读取 DGP 输出；
- `src/monte_carlo.py`
- `src/diagnostics.py`
- `src/plots.py`
- `report.md`

如果必须修改其他文件，请先说明理由。

## 8. AI Usage Logging

请自动更新 `AI_USAGE_LOG.md`，新增一条 estimator implementation 的记录。

日志中必须包含：

- 本次 prompt 摘要；
- 你修改了哪些文件；
- 实现了哪些 estimator；
- sanity check 结果摘要；
- 哪些内容仍需我审核；
- 采纳状态写成 `Pending student review`。

## 9. Output Format

请按以下格式回复：

### 1. Estimators Implemented
### 2. Matching Design
### 3. DID Specification Check
### 4. Files Modified
### 5. Sanity Check Results
### 6. Forbidden Variable Check
### 7. Remaining Student Review Items
### 8. AI Usage Log Update
~~~

### Prompt 5：Monte Carlo 管线实现

~~~text
很好。我已经审核 estimator implementation，并接受它作为 Monte Carlo 阶段的工作基础。

我接受以下设计：

1. 四个 estimator 返回 structured dict；
2. PSM-only 是 post-period matched outcome difference，解释为 ATT-style cross-sectional matching estimator；
3. Simple DID 使用 `delta_y ~ treated`；
4. DID with covariates 使用 `delta_y ~ treated + x1 + x2`，而不是错误地只在 long-format DID 中加入 time-invariant covariate main effects；
5. PSM-DID 使用基于 `x1`, `x2` 的 nearest-neighbor matching，然后计算 matched pair 的 \(\Delta Y\) difference；
6. 默认允许 replacement matching；
7. `alpha` 和 `u` 只能用于 simulation diagnostics，不能用于估计器。

现在进入 **Monte Carlo implementation 阶段**。

请先阅读：

- `src/dgp.py`
- `src/estimators.py`
- `src/monte_carlo.py`
- `main.py`
- `AGENTS.md`
- `AI_USAGE_LOG.md`

本阶段目标是实现可复现的 Monte Carlo runner 和 summary table。不要写最终报告解释，不要编造结果，不要运行耗时的 500 次最终模拟，除非我之后明确要求。

## 1. Update Previous AI Log Status

请先在 `AI_USAGE_LOG.md` 中把上一条 estimator implementation 记录的采纳状态从 `Pending student review` 更新为类似：

```text
Reviewed by student and accepted as the working estimator implementation for Monte Carlo integration.
```

不要写成最终论文结果已确认，只表示我接受它作为下一步 Monte Carlo 实现基础。

## 2. Implement `src/monte_carlo.py`

请实现或修改 Monte Carlo 逻辑，使其适配 estimator 返回的 structured dict。

建议包含以下函数：

```python
run_one_replication(
    scenario: str,
    n: int,
    tau: float,
    seed: int,
    covariates=("x1", "x2"),
    params: dict | None = None,
    matching_options: dict | None = None,
) -> pandas.DataFrame
```

该函数应：

- 使用 `generate_data()` 生成一个新的 dataset；
- 运行 `estimate_all()`；
- 从每个 estimator 的 dict 中提取 `estimate` 和 metadata；
- 返回 tidy format，每行是一个 estimator 在一次 replication 中的结果；
- 保留 scenario、replication seed、tau、estimate、estimator name、bias、n_treated、n_control、n_matched_treated、warnings 等信息。

再实现：

```python
run_monte_carlo(
    scenarios=("A", "B", "C"),
    n: int = 1000,
    tau: float = 2.0,
    r: int = 500,
    seed: int = 12345,
    covariates=("x1", "x2"),
    params: dict | None = None,
    matching_options: dict | None = None,
) -> pandas.DataFrame
```

要求：

- 每个 scenario 至少运行 r 次；
- 每次 replication 必须使用不同 seed；
- 不要重复使用同一个 dataset；
- 如果某个 estimator 在某次 replication 失败，要记录 error message，而不是让整个 Monte Carlo 静默失败；
- 最终返回 tidy DataFrame。

再实现：

```python
summarize_results(results: pandas.DataFrame, tau: float) -> pandas.DataFrame
```

summary 至少包含：

- scenario；
- estimator；
- n_replications_successful；
- mean_estimate；
- bias = mean(estimate) - tau；
- rmse = sqrt(mean((estimate - tau)^2))；
- sd = standard deviation of estimates；
- mean_n_matched_treated；
- mean_n_unique_matched_controls；
- failure_count；
- warning_count。

请特别注意：

- Bias 和 RMSE 必须相对 true treatment effect `tau` 计算；
- 不要把单次 replication 的 estimate 当作最终结果；
- 不要把 debug run 的结果写进 report。

## 3. Save Outputs

请添加保存函数，例如：

```python
save_monte_carlo_outputs(results, summary, output_dir="tables")
```

要求：

- 保存 full results，例如 `tables/monte_carlo_results_debug.csv`；
- 保存 summary，例如 `tables/monte_carlo_summary_debug.csv`；
- 为 final run 预留文件名，例如 `monte_carlo_summary_final.csv`，但现在不要生成 final 结果。

## 4. Update `main.py` Lightly

可以轻量修改 `main.py`，让它支持 debug mode，例如：

```bash
python main.py --mode debug
```

debug mode 可以运行：

```text
N = 500
R = 20
```

final mode 预留：

```text
N = 1000
R = 500
```

但请不要自动运行 final mode。`main.py` 应清楚打印：debug outputs are not final report results。

## 5. Run a Small Debug Monte Carlo

请运行一个小规模 debug Monte Carlo：

```text
scenarios = A, B, C
N = 500
R = 20
tau = 2.0
```

输出 debug summary，确认 pipeline 正常。

请明确标注：

```text
These are debug results only and should not be used in the final report.
```

## 6. Expected Pattern Check

请不要强行调参，但请检查 debug results 的方向是否大致符合 DGP 逻辑：

- Scenario A：DID 应大致接近 2；
- Scenario B：simple DID 应比 DID with covariates / PSM-DID 更偏；
- Scenario C：DID with covariates 可能部分改善，但 PSM-DID 仍应有明显偏误；
- PSM-only 可能在 A/B/C 都不如 DID 类 estimator 稳定。

如果 R=20 的 debug results 噪声较大，请说明这是 debug run 的局限，不要过度解释。

## 7. File Modification Rules

你现在可以修改：

- `src/monte_carlo.py`
- `main.py`
- `AI_USAGE_LOG.md`

如有必要，也可以对 `src/estimators.py` 做极小兼容性修复，但必须说明原因。

不要修改：

- `src/dgp.py`，除非发现 DGP 输出结构阻碍 Monte Carlo；
- `report.md` 的正式结果部分；
- `src/diagnostics.py`
- `src/plots.py`

## 8. AI Usage Logging

请自动更新 `AI_USAGE_LOG.md`，新增一条 Monte Carlo implementation 记录。

日志中必须包含：

- 本次 prompt 摘要；
- 修改了哪些文件；
- Monte Carlo 函数摘要；
- debug run 设置；
- debug summary 摘要；
- 哪些内容仍需我审核；
- 采纳状态写成 `Pending student review`。

## 9. Output Format

请按以下格式回复：

### 1. Monte Carlo Functions Implemented
### 2. Main Script Changes
### 3. Debug Run Settings
### 4. Debug Summary Results
### 5. Expected Pattern Check
### 6. Files Modified
### 7. Remaining Student Review Items
### 8. AI Usage Log Update
~~~

### Prompt 6：诊断与绘图

~~~text
很好。我已经审核 Monte Carlo implementation 和 debug run，并接受它作为 diagnostics / plotting 阶段的工作基础。

我接受以下内容：

1. `run_one_replication()` 会为每次 replication 生成新数据；
2. `run_monte_carlo()` 会为每个 scenario 使用不同 seed；
3. `summarize_results()` 正确计算 mean estimate、bias、RMSE、SD；
4. debug run 只用于 pipeline 检查，不能写进最终报告；
5. 当前 debug pattern 符合 DGP 预期：
   - Scenario A 中 DID 和 PSM-DID 接近 \(\tau=2\)；
   - Scenario B 中 simple DID 明显偏高，DID with covariates 和 PSM-DID 更接近 2；
   - Scenario C 中 DID with covariates 和 PSM-DID 只能部分改善，仍有明显偏误。

现在进入 **diagnostics and plots 阶段**。

请先阅读：

- `src/dgp.py`
- `src/estimators.py`
- `src/monte_carlo.py`
- `src/diagnostics.py`
- `src/plots.py`
- `main.py`
- `AGENTS.md`
- `AI_USAGE_LOG.md`

本阶段目标是实现作业要求中的诊断表和图。不要运行 final Monte Carlo，不要写最终报告解释，不要编造最终结果。

## 1. Update Previous AI Log Status

请先在 `AI_USAGE_LOG.md` 中把上一条 Monte Carlo implementation 记录的采纳状态从 `Pending student review` 更新为类似：

```text
Reviewed by student and accepted as the working Monte Carlo pipeline for diagnostics and plotting.
```

不要写成最终结果已确认，只表示我接受它作为下一阶段基础。

## 2. Implement Balance Diagnostics in `src/diagnostics.py`

请实现匹配前后协变量平衡性检查。

需要支持的函数建议如下：

```python
standardized_mean_difference(x_treated, x_control) -> float
make_balance_table(
    data,
    covariates=("x1", "x2"),
    matched_pairs=None,
    matching_options=None,
) -> pandas.DataFrame
make_balance_tables_by_scenario(
    scenarios=("A", "B", "C"),
    n=1000,
    tau=2.0,
    seed=12345,
    covariates=("x1", "x2"),
    output_dir="tables",
    suffix="debug",
)
```

平衡性表至少包含：

- scenario；
- covariate；
- treated_mean_before；
- control_mean_before；
- smd_before；
- treated_mean_after；
- control_mean_after；
- smd_after；
- n_treated_before；
- n_control_before；
- n_treated_after；
- n_control_after；
- matching method；
- whether replacement is used。

请注意：

- 匹配只能使用处理前可观测变量 `x1`, `x2`；
- 不能使用 `alpha`、`u`、`y`、`untreated_trend`、`propensity_true` 做匹配；
- 如果当前 `src/estimators.py` 的 matching 函数没有返回 matched pairs，请做最小兼容性修改，让 diagnostics 能获得 matched treated-control pair ids；
- 如果做了 estimator 小修改，请说明原因，不能改变 estimator 的核心定义。

## 3. Implement Common Support Diagnostics

请实现 common support 数据生成函数，例如：

```python
make_common_support_data(
    data,
    covariates=("x1", "x2"),
) -> pandas.DataFrame
```

输出至少包含：

- id / unit_id；
- treated；
- propensity_score；
- scenario；
- in_common_support；
- min_control_score；
- max_control_score；
- min_treated_score；
- max_treated_score。

同时给出 overlap summary，例如：

- treated outside control support count；
- control outside treated support count；
- min / max propensity score by group；
- number of treated and control units。

请注意：用于 common support 的 propensity score 应来自估计模型，即用 `x1`, `x2` 估计，而不是直接使用 DGP 里的 `propensity_true`。

## 4. Implement Plots in `src/plots.py`

请实现以下图：

### Plot 1: Estimator distribution plots

基于 Monte Carlo results table，画 estimator estimates 的分布。

函数建议：

```python
plot_estimator_distributions(
    results,
    tau=2.0,
    output_dir="figures",
    suffix="debug",
)
```

要求：

- 每个 scenario 一张图，或一个清晰的 combined plot；
- x 轴是 estimate；
- 按 estimator 区分；
- 加上 true effect \(\tau=2.0\) 的竖线；
- 保存为例如：
  - `figures/scenario_A_estimator_distributions_debug.png`
  - `figures/scenario_B_estimator_distributions_debug.png`
  - `figures/scenario_C_estimator_distributions_debug.png`

### Plot 2: Common support plots

基于每个 scenario 的单次样本或诊断样本，画 treated/control 的 estimated propensity score 分布。

函数建议：

```python
plot_common_support(
    support_data,
    scenario,
    output_dir="figures",
    suffix="debug",
)
```

要求：

- treated 和 control 分布要清楚区分；
- x 轴是 estimated propensity score；
- 标题中包含 scenario；
- 保存为例如：
  - `figures/scenario_A_common_support_debug.png`
  - `figures/scenario_B_common_support_debug.png`
  - `figures/scenario_C_common_support_debug.png`

### Optional Plot 3: Balance improvement plot

如果实现简单，可以画 before/after SMD bar plot。不是必须，但有助于报告。

保存为：

```text
figures/balance_smd_debug.png
```

## 5. Update `main.py` Debug Mode

轻量更新 `main.py --mode debug`，让 debug mode 除了 Monte Carlo summary 之外，也能生成：

- debug Monte Carlo results；
- debug Monte Carlo summary；
- debug balance tables；
- debug common support summaries；
- debug estimator distribution plots；
- debug common support plots。

请明确打印：

```text
Debug outputs are for pipeline checking only and should not be used as final report results.
```

不要自动运行 final mode。

## 6. Run Debug Diagnostics

请运行：

```bash
python main.py --mode debug
```

或者等价 debug command。

debug 设置保持：

```text
N = 500
R = 20
tau = 2.0
scenarios = A, B, C
```

请报告生成了哪些文件，并给出简短 sanity check：

- balance table 是否显示 Scenario B 匹配后 `x1`, `x2` SMD 明显下降；
- common support 是否没有完全崩坏；
- estimator distribution plots 是否成功生成；
- debug outputs 是否都带 `_debug` 后缀。

不要把 debug 图表或 debug summary 当作最终结论。

## 7. File Modification Rules

你现在可以修改：

- `src/diagnostics.py`
- `src/plots.py`
- `main.py`
- `AI_USAGE_LOG.md`

如有必要，可以对 `src/estimators.py` 做极小兼容性修改，例如返回 matched pair ids，但必须说明原因。

不要修改：

- `src/dgp.py`
- `src/monte_carlo.py`，除非发现 output format 无法支持 plotting；
- `report.md` 的正式结果部分。

## 8. AI Usage Logging

请自动更新 `AI_USAGE_LOG.md`，新增 diagnostics and plots 记录。

日志中必须包含：

- 本次 prompt 摘要；
- 修改了哪些文件；
- 实现了哪些 diagnostics；
- 实现了哪些 plots；
- debug run 生成了哪些文件；
- 哪些内容仍需我审核；
- 采纳状态写成 `Pending student review`。

## 9. Output Format

请按以下格式回复：

### 1. Diagnostics Implemented
### 2. Plots Implemented
### 3. Matching Compatibility Changes
### 4. Debug Command Run
### 5. Generated Debug Files
### 6. Diagnostic Sanity Check
### 7. Files Modified
### 8. Remaining Student Review Items
### 9. AI Usage Log Update
~~~

### Prompt 7：正式 Monte Carlo 运行

~~~text
很好。我已经审核 diagnostics and plots 阶段，并接受它作为 final run 的工作基础。

我接受以下内容：

1. 已有匹配前后 balance table；
2. common support 使用基于 `x1`, `x2` 估计的 propensity score，而不是 DGP 的 `propensity_true`；
3. Scenario B 的 debug balance 显示匹配后 `x1`, `x2` 的 SMD 明显下降；
4. debug common support 没有完全崩坏；
5. estimator distribution plots、common support plots、balance SMD plot 都已成功生成；
6. 所有 debug outputs 都带 `_debug` 后缀，不作为最终报告结果。

现在进入 **final Monte Carlo run 阶段**。

本阶段允许运行最终模拟，但仍然不要写最终报告正文，不要编造解释，不要选择或评价论文。

请先阅读：

- `main.py`
- `src/dgp.py`
- `src/estimators.py`
- `src/monte_carlo.py`
- `src/diagnostics.py`
- `src/plots.py`
- `AGENTS.md`
- `AI_USAGE_LOG.md`

## 1. Update Previous AI Log Status

请先在 `AI_USAGE_LOG.md` 中把上一条 diagnostics and plots 记录的采纳状态从 `Pending student review` 更新为类似：

```text
Reviewed by student and accepted as the working diagnostics and plotting pipeline for final output generation.
```

不要写成最终报告已完成，只表示我接受它作为 final output generation 的基础。

## 2. Confirm Final Run Settings

请确认 final run 使用以下设置：

```text
scenarios = A, B, C
N_final = 1000
R_final = 500
tau = 2.0
covariates = x1, x2
matching = nearest-neighbor propensity score matching with replacement
seed = 20260501 或当前 main.py 中固定的 final seed
```

请在输出中明确写出最终设置。

## 3. Run Final Monte Carlo

请运行 final mode，例如：

```bash
python main.py --mode final
```

或者等价命令。

final Monte Carlo 应生成：

```text
tables/monte_carlo_results_final.csv
tables/monte_carlo_summary_final.csv
```

要求：

- 每个 scenario 应有 500 次 successful replications；
- 每个 scenario-estimator 组合应该有 500 个成功 estimate；
- 总 estimator-result rows 理论上应为：

```text
3 scenarios × 4 estimators × 500 replications = 6000 rows
```

如果有 failures 或 warnings，请不要隐藏。请汇总失败数量、warning 数量和原因。

## 4. Generate Final Diagnostics and Plots

请同时生成 final suffix 的诊断表和图。

Final tables 应包括：

```text
tables/balance_table_final.csv
tables/common_support_data_final.csv
tables/common_support_summary_final.csv
```

Final figures 应包括：

```text
figures/scenario_A_estimator_distributions_final.png
figures/scenario_B_estimator_distributions_final.png
figures/scenario_C_estimator_distributions_final.png
figures/scenario_A_common_support_final.png
figures/scenario_B_common_support_final.png
figures/scenario_C_common_support_final.png
figures/balance_smd_final.png
```

请确保：

- final estimator distribution plots 使用 final Monte Carlo results；
- final common support plots 使用 final diagnostic sample；
- final balance table 使用 final diagnostic sample；
- 不要把 debug 文件复制重命名成 final 文件；
- debug outputs 和 final outputs 都保留，但报告只能引用 final outputs。

## 5. Validate Final Results

请做最终结果 sanity check，但不要写成完整报告解释。

请检查：

1. `monte_carlo_results_final.csv` 是否有 6000 行，或者解释为何不是；
2. `monte_carlo_summary_final.csv` 是否有 12 行，即 3 scenarios × 4 estimators；
3. 每个 scenario-estimator 是否有 500 successful replications；
4. Bias 是否等于 `mean_estimate - tau`；
5. RMSE 是否等于 `sqrt(mean((estimate - tau)^2))`；
6. 是否有 missing estimates；
7. 是否有 failed replications；
8. 是否有 warnings；
9. final figure 文件是否存在且非空；
10. final table 文件是否存在且非空。

## 6. Expected Final Pattern Check

请检查最终结果是否大体符合设计逻辑：

- Scenario A:
  - DID 应接近 2；
  - PSM-DID 应接近 2；
  - PSM-only 可能偏，因为它不能去除未观测 time-invariant heterogeneity。
- Scenario B:
  - simple DID 应偏；
  - DID with covariates 和 PSM-DID 应更接近 2；
  - balance table 应显示 matching 后 `x1`, `x2` 更平衡。
- Scenario C:
  - simple DID 应偏；
  - DID with covariates 和 PSM-DID 可以部分改善；
  - 但因为有 unobserved time-varying confounding，PSM-DID 仍应有明显偏误。
  
如果 final pattern 和预期不一致，请不要强行解释。请指出可能原因，例如参数强度、matching 质量、Monte Carlo noise、代码问题或 DGP 设定问题。

## 7. File Modification Rules

本阶段可以修改：

- `main.py`，如果 final mode 有路径或命名问题；
- `src/monte_carlo.py`，如果发现 summary 或 saving 有 bug；
- `src/diagnostics.py` 或 `src/plots.py`，如果 final output generation 有小 bug；
- `AI_USAGE_LOG.md`。

不要修改：

- `src/dgp.py`，除非发现严重 DGP bug；
- `src/estimators.py`，除非发现严重 estimator bug；
- `report.md` 的正式结果解释部分。

如果必须修改 DGP 或 estimator，请先说明问题，不要静默修改，因为这会影响之前已经审核过的设计。

## 8. AI Usage Logging

请自动更新 `AI_USAGE_LOG.md`，新增 final Monte Carlo run 记录。

日志中必须包含：

- 本次 prompt 摘要；
- final run 设置；
- 运行命令；
- 修改了哪些文件；
- 生成了哪些 final outputs；
- final summary 的主要数值摘要；
- validation checks；
- 哪些内容仍需我审核；
- 采纳状态写成 `Pending student review`。

## 9. Output Format

请按以下格式回复：

### 1. Final Run Settings
### 2. Command Run
### 3. Files Modified
### 4. Final Tables Generated
### 5. Final Figures Generated
### 6. Final Monte Carlo Summary
### 7. Validation Checks
### 8. Expected Pattern Check
### 9. Remaining Student Review Items
### 10. AI Usage Log Update
~~~

### Prompt 8：应用论文初步筛选

~~~text
很好。我已经审核 final Monte Carlo run，并接受它作为最终模拟结果基础。

我接受以下 final outputs 作为后续报告写作基础：

1. `tables/monte_carlo_results_final.csv` 有 6000 行；
2. `tables/monte_carlo_summary_final.csv` 有 12 行；
3. 每个 scenario-estimator 组合都有 500 次成功 replication；
4. 没有 missing estimates、failed replications 或 warnings；
5. final results 的方向符合 DGP 设计：
   - Scenario A: DID 和 PSM-DID 接近 \(\tau=2\)；
   - Scenario B: simple DID 明显偏高，DID with covariates 和 PSM-DID 接近 2；
   - Scenario C: DID with covariates 和 PSM-DID 只能部分改善，但仍明显偏误；
   - PSM-only 在多个场景中偏误较大；
6. final balance 和 common support outputs 可以用于报告诊断部分。

现在进入 **PSM-DID applied paper selection 阶段**。

请先阅读：

- `AGENTS.md`
- `AI_USAGE_LOG.md`
- `report.md`
- `references/`
- 作业页面要求，尤其是关于论文评价的部分

本阶段目标是帮我筛选一篇真实使用 PSM-DID 的应用经济学论文。请注意：**不要编造论文，不要编造 DOI，不要编造平衡性检验或平行趋势检验内容。**

## 1. Update Previous AI Log Status

请先在 `AI_USAGE_LOG.md` 中把上一条 final Monte Carlo run 记录的采纳状态从 `Pending student review` 更新为类似：

```text
Reviewed by student and accepted as the final Monte Carlo output basis for report writing.
```

不要写成最终报告已完成，只表示我接受 final simulation outputs 作为报告基础。

## 2. Search for Candidate Papers

请寻找 3 篇真实使用 PSM-DID 或 PSM combined with DID 的应用论文。

论文范围可以包括：

- economics；
- finance；
- public policy；
- labor economics；
- environmental economics；
- development economics；
- industrial organization；
- management or business economics；
- Chinese applied economics journals, if verifiable；
- English peer-reviewed journals, if verifiable。

优先选择满足以下条件的论文：

1. 明确使用 PSM-DID；
2. 研究问题和处理变量清楚；
3. 有政策或项目冲击；
4. 有处理组和控制组；
5. 有匹配变量说明；
6. 有平衡性检验；
7. 有共同支持或 overlap 说明；
8. 有 DID / 平行趋势相关检验；
9. 论文容易获得稳定链接、DOI 或期刊页面；
10. 适合和我的 Monte Carlo 结果联系起来评价。

如果你有 web access，请务必在线核实论文信息。  
如果你没有 web access，请明确说明，并只基于本地已有文件或让我提供论文 PDF，不要凭记忆编造。

## 3. Candidate Paper Table

请输出一个候选论文表，每篇包含：

- paper title；
- authors；
- year；
- journal / working paper source；
- DOI or stable link；
- research question；
- treatment variable；
- outcome variable；
- why it is suitable for this HW1；
- likely strengths for identification；
- likely weaknesses / risks；
- whether it reports matching variables；
- whether it reports balance test；
- whether it reports common support；
- whether it reports parallel trends or pre-trend test；
- how it connects to Scenario A/B/C from my simulation。

如果某项信息暂时没确认，请写 `Not verified yet`，不要猜。

## 4. Recommendation

请在 3 篇候选中推荐 1 篇最适合用于本作业的论文，并说明理由。

推荐标准：

- 最适合评价 PSM-DID 的识别假设；
- 最容易和我的 Monte Carlo 三个场景联系起来；
- 不需要过多额外背景就能解释清楚；
- 论文信息可靠、可核实；
- 有足够方法细节可评价。

## 5. Do Not Write Final Evaluation Yet

本阶段不要写最终论文评价正文。只做候选筛选和推荐。

下一阶段我会选择其中一篇，然后再让你写正式评价框架。

## 6. File Modification Rules

你现在可以修改：

- `AI_USAGE_LOG.md`
- 如有必要，可以在 `references/` 下新增一个简短文件，例如：
  - `references/paper_candidates.md`

不要修改：

- `report.md` 的论文评价正文；
- `src/`；
- `main.py`；
- final result tables 或 figures。

如果创建 `references/paper_candidates.md`，里面只记录候选论文信息和核实状态，不要写成最终报告。

## 7. AI Usage Logging

请自动更新 `AI_USAGE_LOG.md`，新增 applied paper search / candidate selection 记录。

日志中必须包含：

- 本次 prompt 摘要；
- 是否使用 web access 或本地资料；
- 找到的候选论文摘要；
- 推荐论文；
- 哪些信息仍需我核实；
- 采纳状态写成 `Pending student review`。

## 8. Output Format

请按以下格式回复：

### 1. Search Method and Verification Status
### 2. Candidate Paper Table
### 3. Recommended Paper
### 4. How the Recommended Paper Connects to My Simulations
### 5. Files Modified
### 6. Remaining Student Review Items
### 7. AI Usage Log Update
~~~

### Prompt 8B：论文候选补强

~~~text
你的上一轮候选论文筛选有用，但我注意到一个风险：Su et al. (2025) 虽然真实、开放获取、方法细节较多，但 PLOS ONE 是综合性期刊，不是典型经济学、管理、公共政策或环境经济学期刊。作业要求我选择一篇使用 PSM-DID 的中文或英文经济学相关学术期刊论文，所以我希望你进一步补强候选论文池。

请不要删除上一轮结果，但请重新搜索并补充更符合以下领域的候选论文：

- economics；
- finance；
- management；
- public policy；
- labor economics；
- industrial organization；
- environmental economics；
- regional economics；
- development economics；
- business / corporate economics。

优先考虑这些类型的期刊或类似期刊：

- China Economic Review；
- Economic Analysis and Policy；
- Energy Economics；
- Journal of Environmental Management；
- Technological Forecasting and Social Change；
- Regional Studies；
- Journal of Development Studies；
- Managerial and Decision Economics；
- Finance Research Letters；
- Emerging Markets Finance and Trade；
- 中文 CSSCI / 北大核心经济管理类期刊，如果信息可核实。

## 1. Keep Previous Candidates but Reassess Fit

请先重新评估上一轮 3 篇候选：

1. Su et al. (2025), PLOS ONE；
2. Tian et al. (2024), Heliyon；
3. Ying et al. (2025), PLOS ONE。

对每篇明确说明：

- 是否真实可核实；
- 是否明确使用 PSM-DID；
- 是否属于经济学相关主流期刊；
- 是否适合作业；
- 主要风险是什么。

请特别注意：不要因为论文容易获得就忽略“期刊领域匹配度”。

## 2. Find Stronger Economics-Related Candidates

请重新搜索至少 3 篇更符合经济学 / 管理 / 公共政策 / 环境经济学期刊范围的 PSM-DID 论文。

每篇必须给出：

- title；
- authors；
- year；
- journal；
- DOI or stable link；
- research question；
- treatment variable；
- outcome variable；
- whether PSM-DID is core method or robustness check；
- whether matching variables are reported；
- whether balance test is reported；
- whether common support is reported；
- whether parallel trend / pre-trend is reported；
- why it is suitable for this HW1；
- identification risks；
- connection to my Scenario A/B/C。

如果某项没有从原文或可靠页面确认，请写 `Not verified yet`，不要猜。

## 3. Rank All Candidates

请把上一轮 3 篇和新找到的候选放在一起排名。

排名标准：

1. 是否真实可核实；
2. 是否明确使用 PSM-DID；
3. 是否属于经济学相关领域期刊；
4. 方法细节是否足够评价；
5. 是否有平衡性、共同支持、平行趋势信息；
6. 是否容易和我的 Monte Carlo 三个场景联系；
7. 是否适合 3000-5000 字课程报告，不需要太多额外背景。

## 4. Recommendation

请最后推荐 1 篇最适合作业的论文。

如果你仍然推荐 Su et al. (2025)，请明确说明：

- 为什么虽然它在 PLOS ONE，但仍然适合作业；
- 这个选择可能被老师质疑的风险；
- 有没有更稳妥的经济学期刊替代方案。

如果你推荐新的经济学相关期刊论文，请说明为什么它比 Su et al. 更稳妥。

## 5. File Rules

你可以修改：

- `references/paper_candidates.md`
- `AI_USAGE_LOG.md`

不要修改：

- `report.md`
- `src/`
- `main.py`
- final tables or figures。

## 6. AI Usage Logging

请自动更新 `AI_USAGE_LOG.md`，新增一条 paper candidate strengthening 记录。

日志中必须包含：

- 本次 prompt 摘要；
- 为什么重新检索；
- 新增候选论文；
- 最终推荐；
- 仍需我核实的信息；
- 采纳状态写成 `Pending student review`。

## 7. Output Format

请按以下格式回复：

### 1. Reassessment of Previous Candidates
### 2. New Economics-Related Candidate Papers
### 3. Full Candidate Ranking
### 4. Recommended Paper and Rationale
### 5. Risk of Using Non-Economics Journals
### 6. Files Modified
### 7. Remaining Student Review Items
### 8. AI Usage Log Update
~~~

### Prompt 9：选定论文证据提取

~~~text
很好。我已经审核候选论文补强结果，并决定选用以下论文作为 HW1 的 PSM-DID 应用论文评价对象：

**Jin, Nuo. 2024. “Analysing firm-level impacts of high-speed railways on reducing business costs: evidence from China.” Regional Studies, Regional Science, 11(1): 22–37. DOI: 10.1080/21681376.2024.2305946.**

我选择它的原因是：

1. 它属于 regional/business economics 相关领域；
2. 它明确使用 DID 和 PSM-DID；
3. 处理变量是高铁开通 / HSR access，比较容易解释；
4. 结果变量是 firm-level business costs，和企业经济行为相关；
5. 它比 PLOS ONE / Heliyon 候选更符合本作业对经济学相关论文的要求；
6. 它可以很好连接我的 Scenario B 和 Scenario C。

现在进入 **selected paper evidence extraction 阶段**。

请先阅读：

- `references/paper_candidates.md`
- `AI_USAGE_LOG.md`
- `report.md`
- AGENTS.md
- 论文原文或可访问页面：
  - https://doi.org/10.1080/21681376.2024.2305946

如果可以访问 PDF 或 full text，请优先核对原文。不要凭摘要猜测。

## 1. Update Previous AI Log Status

请先在 `AI_USAGE_LOG.md` 中把上一条 paper candidate strengthening 记录的采纳状态从 `Pending student review` 更新为类似：

```text
Reviewed by student. Jin (2024) selected as the applied PSM-DID paper for evaluation.
```

不要写成最终论文评价已完成，只表示我已选择该论文作为评价对象。

## 2. Extract Verifiable Paper Information

请从论文原文或可靠页面提取以下信息。每一项都要标明是否 verified。

### Basic citation

- title；
- author；
- year；
- journal；
- volume / issue / pages；
- DOI；
- stable link。

### Research design

- research question；
- treatment / policy variable；
- treatment group；
- control group；
- outcome variable；
- sample period；
- data source；
- unit of observation；
- baseline DID specification；
- where PSM-DID enters the paper: main method or robustness / supplementary method。

### PSM details

- matching variables；
- matching method；
- whether matching uses only pre-treatment covariates；
- whether common support is checked；
- whether observations outside common support are dropped；
- whether balance tests are reported；
- what balance tests show。

### DID details

- whether the paper discusses parallel trends；
- whether the paper uses event-study / pre-trend test；
- whether placebo test is reported；
- whether fixed effects are used；
- whether heterogeneous effects are reported；
- whether standard errors are clustered or otherwise adjusted。

### Identification risks

Please identify potential risks, especially:

- treatment timing may be non-random;
- HSR placement may target faster-growing or strategically important cities;
- city-level economic trends may differ even after matching;
- unobserved time-varying local policies may coincide with HSR opening;
- firms may anticipate HSR opening;
- PSM may change the target population toward matched treated firms;
- common support restrictions may affect external validity.

## 3. Connect to My Monte Carlo Scenarios

请明确把这篇论文和我的三个模拟场景联系起来：

- Scenario A: When would a simple DID interpretation be credible?
- Scenario B: How does PSM-DID help if observed covariates predict both HSR access and firm cost trends?
- Scenario C: What unobserved time-varying confounders could still make PSM-DID fail?

请使用我的 final Monte Carlo 结果作为参考：

```text
Scenario A:
DID bias ≈ -0.002
PSM-DID bias ≈ -0.013
PSM-only bias ≈ 0.476

Scenario B:
DID bias ≈ 0.602
DID with covariates bias ≈ -0.007
PSM-DID bias ≈ -0.001
PSM-only bias ≈ 0.483

Scenario C:
DID bias ≈ 1.164
DID with covariates bias ≈ 0.683
PSM-DID bias ≈ 0.693
PSM-only bias ≈ 1.123
```

要求：

- 不要机械套用我的结果；
- 要说明这些模拟结果如何帮助评价 Jin (2024) 的识别策略；
- 不要说“论文一定正确”或“论文一定错误”；
- 要写成“在什么条件下可信，在什么条件下脆弱”。

## 4. Create Notes File

请创建或更新：

```text
references/selected_paper_notes.md
```

该文件只做阅读笔记，不是最终报告正文。

文件应包含：

1. full citation；
2. verified research design summary；
3. verified PSM-DID details；
4. verified diagnostics；
5. identification strengths；
6. identification weaknesses；
7. connection to my Monte Carlo scenarios；
8. items still requiring student verification。

凡是没在原文中核实的内容，必须写：

```text
Not verified yet
```

不要编造。

## 5. Do Not Write Final Report Yet

现在不要修改 `report.md` 的正式论文评价部分。  
下一步我会让你根据 `selected_paper_notes.md` 写正式评价草稿。

## 6. File Modification Rules

你可以修改：

- `references/selected_paper_notes.md`
- `AI_USAGE_LOG.md`

你不要修改：

- `report.md`
- `src/`
- `main.py`
- final tables or figures。

## 7. AI Usage Logging

请自动更新 `AI_USAGE_LOG.md`，新增 selected paper evidence extraction 记录。

日志中必须包含：

- 本次 prompt 摘要；
- 选定论文；
- 是否访问了 full text / PDF；
- 提取了哪些 verified 信息；
- 哪些内容仍需我核实；
- 创建或修改了哪些文件；
- 采纳状态写成 `Pending student review`。

## 8. Output Format

请按以下格式回复：

### 1. Selected Paper Citation
### 2. Verification Source
### 3. Research Design Summary
### 4. PSM-DID Details
### 5. DID and Diagnostic Evidence
### 6. Identification Strengths
### 7. Identification Risks
### 8. Connection to My Monte Carlo Scenarios
### 9. Files Modified
### 10. Remaining Student Review Items
### 11. AI Usage Log Update
~~~

### Prompt 9B：选定论文未核实项补证

~~~text
很好。你已经完成了 Jin (2024) 的初步 evidence extraction，但还有几个关键识别细节被标为 `Not verified yet`。在写正式论文评价之前，请先做一次 **remaining evidence verification**。

本阶段目标：尽量核实上一步未确认的信息；如果无法核实，必须明确保留 `Not verified yet`，不要猜测、不要补写。

请重新阅读：

- `references/selected_paper_notes.md`
- `references/paper_candidates.md`
- `AI_USAGE_LOG.md`
- Jin (2024) 的 full text / PDF / supplementary materials，如可访问：
  - DOI: `10.1080/21681376.2024.2305946`
  - Cardiff ORCA record: `https://orca.cardiff.ac.uk/id/eprint/166454/`

## 1. Update Previous AI Log Status

请先不要把上一条 selected paper evidence extraction 记录改成 fully accepted。  
因为仍有未核实项，请只补充一句：

```text
Student reviewed the initial evidence extraction and requested additional verification of unresolved methodological details before drafting the final paper evaluation.
```

## 2. Verify Remaining Method Details

请重点核实以下内容：

### A. Matching algorithm

请确认 Jin (2024) 使用的具体匹配方法：

- nearest-neighbor matching?
- radius matching?
- kernel matching?
- caliper?
- one-to-one or many-to-one?
- with replacement or without replacement?
- 是否使用 logit / probit 估计 propensity score?

如果原文没有说明，请写：

```text
Not verified in accessible text.
```

不要猜。

### B. Matching covariates and timing

请确认匹配变量是否都是处理前或政策前变量。

对每个 matching variable 列表说明：

- variable name；
- variable meaning；
- whether it appears pre-treatment；
- whether timing is clearly stated；
- risk if timing is unclear。

如果原文只列变量但没有说明年份或 treatment 前后，请写：

```text
Timing not fully verified.
```

### C. Common support

请确认：

- 是否画 propensity score 分布图；
- 是否删除 common support 之外的样本；
- 删除了多少 observations / firms / cities；
- 处理组和控制组 common support 是否足够；
- 是否可能改变 estimand 或外部有效性。

### D. Balance test

请确认：

- 是否有 balance table；
- balance statistic 是 standardized bias / t-test / variance ratio / other；
- 匹配后哪些变量平衡改善；
- 是否仍有变量未完全平衡；
- 上一轮提到 passenger traffic volume 仍超过 10% threshold，这一点是否准确。

### E. Parallel trend / event study

请确认：

- 是否有 parallel trend 图或 event-study 回归；
- pre-treatment coefficients 是否接近 0；
- 论文如何解释；
- 是否有足够 pre-treatment periods；
- 这项证据是否支持 DID / PSM-DID。

### F. Placebo test

请确认：

- placebo test 的具体设计；
- placebo 是随机处理组、随机时间、替代 outcome，还是其他；
- 结果如何；
- 它能排除什么，不能排除什么。

### G. Fixed effects and standard errors

请确认：

- 是否使用 firm fixed effects；
- 是否使用 city fixed effects；
- 是否使用 year fixed effects；
- 是否使用 industry fixed effects；
- standard errors clustered at what level；
- 这个 clustering level 是否合理。

### H. Heterogeneity analysis

请确认是否报告异质性结果，例如：

- ownership；
- industry；
- region；
- firm size；
- city characteristics。

如果有，请说明它对识别评价是否重要。  
如果没有或未核实，请写 `Not verified yet`。

## 3. Update `selected_paper_notes.md`

请更新：

```text
references/selected_paper_notes.md
```

要求：

- 保留原有结构；
- 把已核实的信息补进去；
- 对仍无法核实的内容保留 `Not verified yet`；
- 不要把阅读笔记写成最终报告正文；
- 明确区分：
  - verified facts；
  - interpretation；
  - my possible critique；
  - items requiring student verification。

## 4. Prepare for Final Evaluation, But Do Not Draft It Yet

请在回复最后给出一个“正式评价写作提纲”，但不要写完整正文。

提纲应包括：

1. Paper summary；
2. Why PSM-DID is used；
3. Matching quality；
4. DID validity；
5. Connection to my Scenario B；
6. Connection to my Scenario C；
7. Overall assessment。

## 5. File Modification Rules

你可以修改：

- `references/selected_paper_notes.md`
- `AI_USAGE_LOG.md`

不要修改：

- `report.md`
- `src/`
- `main.py`
- final tables or figures。

## 6. AI Usage Logging

请自动更新 `AI_USAGE_LOG.md`，新增 selected paper remaining verification 记录。

日志中必须包含：

- 本次 prompt 摘要；
- 你访问了哪些资料；
- 哪些未核实项被成功核实；
- 哪些仍然无法核实；
- 修改了哪些文件；
- 是否准备进入正式评价写作；
- 采纳状态写成 `Pending student review`。

## 7. Output Format

请按以下格式回复：

### 1. Verification Sources Used
### 2. Matching Algorithm Verification
### 3. Matching Covariates and Timing
### 4. Common Support Evidence
### 5. Balance Test Evidence
### 6. Parallel Trend / Event Study Evidence
### 7. Placebo Test Evidence
### 8. Fixed Effects and Standard Errors
### 9. Heterogeneity Evidence
### 10. Remaining Unverified Items
### 11. Updates to selected_paper_notes.md
### 12. Proposed Final Evaluation Outline
### 13. AI Usage Log Update
~~~

### Prompt 10：报告结构与文字整理

~~~text
很好。我已经审核 Jin (2024) 的 remaining evidence verification。现在可以进入 **report organization and revision 阶段**。

请先阅读：

- `report.md`
- `tables/monte_carlo_summary_final.csv`
- `tables/balance_table_final.csv`
- `tables/common_support_summary_final.csv`
- final figures in `figures/`
- `references/selected_paper_notes.md`
- `references/paper_candidates.md`
- `AI_USAGE_LOG.md`
- `AGENTS.md`

现在请基于已经生成的 final outputs 和 selected paper notes，协助整理和修改 `report.md` 的章节结构与文字表述。

## 1. Update Previous AI Log Status

请先在 `AI_USAGE_LOG.md` 中把上一条 selected paper remaining verification 记录的采纳状态从 `Pending student review` 更新为类似：

```text
Reviewed by student and accepted as the working evidence base for drafting the applied paper evaluation, with unresolved items kept as limitations.
```

不要写成论文评价最终完成，只表示我接受它作为文字整理基础。

## 2. Report Structure

请把 `report.md` 我撰写的草稿整理成一篇课程报告，建议结构如下：

```text
# HW1: Understanding PSM-DID through Monte Carlo Simulation

1. Introduction
2. Identification Background: PSM, DID, and PSM-DID
3. Monte Carlo Design
4. Estimation Methods
5. Simulation Results
6. Diagnostics: Balance and Common Support
7. Interpretation of Results
8. Evaluation of an Applied PSM-DID Paper
9. Conclusion
10. AI Usage Disclosure
11. References
```

## 3. Use Final Results Only

报告中的数值只能来自 final outputs，不要使用 debug outputs。

请使用以下 final Monte Carlo summary：

```text
Scenario A:
DID mean 1.998, bias -0.002, RMSE 0.089
DID with covariates mean 1.996, bias -0.004, RMSE 0.097
PSM mean 2.476, bias 0.476, RMSE 0.494
PSM-DID mean 1.987, bias -0.013, RMSE 0.134

Scenario B:
DID mean 2.602, bias 0.602, RMSE 0.611
DID with covariates mean 1.993, bias -0.007, RMSE 0.097
PSM mean 2.483, bias 0.483, RMSE 0.500
PSM-DID mean 1.999, bias -0.001, RMSE 0.137

Scenario C:
DID mean 3.164, bias 1.164, RMSE 1.170
DID with covariates mean 2.683, bias 0.683, RMSE 0.692
PSM mean 3.123, bias 1.123, RMSE 1.134
PSM-DID mean 2.693, bias 0.693, RMSE 0.710
```

Also mention:

```text
N = 1000
R = 500
tau = 2.0
scenarios = A, B, C
matching covariates = x1, x2
matching method = nearest-neighbor propensity score matching with replacement
```

## 4. Required Figures and Tables

Please reference final files, not debug files.

Tables to reference:

```text
tables/monte_carlo_summary_final.csv
tables/balance_table_final.csv
tables/common_support_summary_final.csv
```

Figures to reference:

```text
figures/scenario_A_estimator_distributions_final.png
figures/scenario_B_estimator_distributions_final.png
figures/scenario_C_estimator_distributions_final.png
figures/scenario_A_common_support_final.png
figures/scenario_B_common_support_final.png
figures/scenario_C_common_support_final.png
figures/balance_smd_final.png
```

Use Markdown image links where appropriate.

## 5. Monte Carlo Design Section

For each scenario, explain:

### Scenario A: Unconditional Parallel Trends

- treatment selection can depend on \(X_i\) and \(\alpha_i\);
- untreated trend is common;
- unconditional parallel trends holds;
- DID should work;
- PSM-only may fail because it does not difference out \(\alpha_i\).

### Scenario B: Covariate-Driven Trend Differences

- treatment selection depends on \(X_i\);
- untreated trend also depends on \(X_i\);
- unconditional DID fails;
- DID with covariates and PSM-DID should improve;
- this is the main scenario showing why PSM-DID can help.

### Scenario C: Time-Varying Unobserved Confounding

- treatment and untreated trend depend on unobserved \(U_i\);
- estimators are not allowed to use \(U_i\);
- observed matching can improve \(X_i\) balance but cannot remove \(U_i\)-driven trend bias;
- this is the scenario showing the limitation of PSM-DID.

## 6. Estimation Methods Section

Define four estimators clearly:

1. PSM-only;
2. Simple DID;
3. DID with covariates;
4. PSM-DID.

Important:

- Explain that DID with covariates uses differenced outcome:

```text
Delta Y_i = a + tau D_i + theta_1 X_i1 + theta_2 X_i2 + e_i
```

- Do not incorrectly say that time-invariant covariates are only added as main effects in long-format DID.
- Explain that PSM-DID is ATT-style because it matches treated units to control units.
- Explain that constant treatment effect means ATT and ATE equal 2.0 in this simulation, but matching-based interpretation is still closer to ATT.

## 7. Results Interpretation Requirements

Please write interpretation carefully:

- Scenario A:
  - DID bias is nearly zero;
  - PSM-DID is also close to true effect;
  - PSM-only is biased upward;
  - interpretation: differencing removes time-invariant heterogeneity, while PSM-only cannot.

- Scenario B:
  - simple DID bias is large and positive;
  - DID with covariates and PSM-DID nearly eliminate bias;
  - interpretation: observed \(X_i\) drives both treatment selection and untreated trends, so controlling/matching on \(X_i\) restores comparability.

- Scenario C:
  - all methods except perhaps partial adjustment remain biased;
  - DID with covariates and PSM-DID improve relative to simple DID but remain far from 2;
  - interpretation: unobserved \(U_i\) creates time-varying confounding that observed matching cannot solve.

Please avoid saying “PSM-DID is always best.” The conclusion should be conditional.

## 8. Diagnostics Section

Use final balance and common support outputs.

Mention specifically:

- Scenario B final balance improved after matching:
  - x1 SMD: approximately 0.684 to 0.033;
  - x2 SMD: approximately 0.333 to -0.051.

Explain:

- better balance supports the Scenario B interpretation;
- common support is necessary because poor overlap changes the matched population and can increase variance;
- balance on observed variables does not prove conditional parallel trends.

## 9. Applied Paper Evaluation Section

Use Jin (2024):

```text
Jin, Nuo. 2024. “Analysing firm-level impacts of high-speed railways on reducing business costs: evidence from China.” Regional Studies, Regional Science, 11(1): 22–37. DOI: 10.1080/21681376.2024.2305946.
```

Please evaluate it using the notes in `references/selected_paper_notes.md`.

Include:

1. research question;
2. treatment: HSR access / opening;
3. outcome: firm business cost ratios;
4. data and unit: firm-year data;
5. why PSM-DID is used;
6. matching variables verified:
   - GDP per capita;
   - secondary-industry share;
   - FDI output share;
   - internet penetration;
   - population density;
7. common support evidence;
8. balance evidence:
   - Pseudo R2 falls from about 0.110 to 0.002;
   - mean bias falls from about 32.6 to 3.6;
   - median bias falls from about 31.7 to 2.7;
9. DID evidence:
   - paper reports parallel trend and placebo tests, but exact event-study and placebo designs are not fully verified in my notes;
10. fixed effects / controls:
   - region fixed effects;
   - time fixed effects;
   - industry controls;
   - t-statistics clustered by firm;
   - firm or city fixed effects not fully verified in my notes;
11. identification strengths;
12. identification risks.

Important cautious wording:

- Do not claim the matching covariates are definitely all pre-treatment unless the notes verify timing.
- Do not claim the exact matching algorithm is known if notes say it is not verified.
- Do not claim the event-study specification or placebo design is fully verified.
- Say that the paper is most similar to Scenario B if observed city covariates explain both HSR access and firm cost trends.
- Say that it would resemble Scenario C if unobserved time-varying city policies, logistics investment, growth shocks, or anticipation effects also affect firm costs.

## 10. AI Usage Disclosure

Add a clear AI usage disclosure near the end.

It should say:

- I used AI tools for project planning, DGP design discussion, code implementation assistance, debugging, plotting, paper selection, evidence extraction, and writing assistance.
- I maintained `AI_USAGE_LOG.md`.
- I reviewed and accepted or revised AI outputs.
- I am responsible for the final code, results interpretation, and paper evaluation.

Do not overclaim that every AI output was automatically correct.

## 11. Writing Style

Use clear academic English.

Avoid:

- vague claims like “PSM-DID is better” without specifying scenario;
- unsupported claims about Jin (2024);
- saying matching proves parallel trends;
- saying PSM-DID solves all endogeneity;
- using debug results;
- writing too casually.

If a result or paper detail is not verified, write that clearly.

## 12. File Modification Rules

You may modify:

- `report.md`
- `AI_USAGE_LOG.md`

Do not modify:

- `src/`
- `main.py`
- final tables;
- final figures;
- `references/selected_paper_notes.md`, unless you find a small typo.

## 13. AI Usage Logging

Please automatically update `AI_USAGE_LOG.md` with a report drafting record.

The log must include:

- prompt summary;
- files modified;
- report sections drafted;
- final results used;
- Jin (2024) evidence used;
- limitations retained;
- items requiring my review;
- adoption status: `Pending student review`.

## 14. Output Format

Please respond with:

### 1. Report Sections Drafted
### 2. Final Results Used
### 3. Applied Paper Evaluation Included
### 4. Cautious / Unverified Claims Preserved
### 5. Files Modified
### 6. Remaining Student Review Items
### 7. AI Usage Log Update
~~~

### Prompt 11：最终审阅与小修

~~~text
我已经完成了 `report.md` 初稿。现在请进入 **final review and revision 阶段**。

请你以严格助教的标准检查整个仓库。目标不是大改报告，而是发现并修正会导致扣分的问题。

请先阅读：

- `report.md`
- `AI_USAGE_LOG.md`
- `AGENTS.md`
- `ASSIGNMENT_CHECKLIST.md`
- `README.md`
- `main.py`
- `src/dgp.py`
- `src/estimators.py`
- `src/monte_carlo.py`
- `src/diagnostics.py`
- `src/plots.py`
- `tables/monte_carlo_summary_final.csv`
- `tables/balance_table_final.csv`
- `tables/common_support_summary_final.csv`
- `references/selected_paper_notes.md`
- `references/paper_candidates.md`

同时检查 `figures/` 和 `tables/` 中 final outputs 是否存在。

## 1. Do Not Assume the Draft Is Correct

我还没有最终接受 `report.md`。  
请把当前报告当作一个需要严格审查的初稿。

你需要作为一个独立审阅者帮我检查并进行修改润色：

1. 报告是否满足作业要求；
2. 报告中的数值是否和 final CSV 一致；
3. 报告是否错误引用 debug outputs；
4. 图表路径是否有效；
5. 论文评价是否把未核实信息说得过于确定；
6. AI 使用说明是否符合课程要求；
7. `AI_USAGE_LOG.md` 是否足够完整；
8. 仓库是否能复现结果。

## 2. Assignment Requirement Check

请根据作业要求逐项检查：

- 是否至少有 3 个 Monte Carlo 场景；
- 是否每个 final scenario 有 500 次 simulation；
- 是否比较了 PSM、DID、DID with covariates、PSM-DID；
- 是否报告 mean estimate、bias、RMSE、SD；
- 是否有 estimator distribution plots；
- 是否有 matching 前后 balance diagnostics；
- 是否有 common support plots；
- 是否解释了 PSM、DID、PSM-DID 的识别条件；
- 是否解释了 PSM-DID 什么时候有效、什么时候失败；
- 是否评价了一篇真实 PSM-DID 应用论文；
- 是否有 AI usage disclosure；
- 是否有完整 AI usage log。

## 3. Numerical Consistency Check

请从 `tables/monte_carlo_summary_final.csv` 重新读取数值，检查 `report.md` 中所有 Monte Carlo 数字是否一致。

特别检查：

```text
Scenario A:
DID mean 1.998, bias -0.002, RMSE 0.089
DID with covariates mean 1.996, bias -0.004, RMSE 0.097
PSM mean 2.476, bias 0.476, RMSE 0.494
PSM-DID mean 1.987, bias -0.013, RMSE 0.134

Scenario B:
DID mean 2.602, bias 0.602, RMSE 0.611
DID with covariates mean 1.993, bias -0.007, RMSE 0.097
PSM mean 2.483, bias 0.483, RMSE 0.500
PSM-DID mean 1.999, bias -0.001, RMSE 0.137

Scenario C:
DID mean 3.164, bias 1.164, RMSE 1.170
DID with covariates mean 2.683, bias 0.683, RMSE 0.692
PSM mean 3.123, bias 1.123, RMSE 1.134
PSM-DID mean 2.693, bias 0.693, RMSE 0.710
```

如果 CSV 中有更精确数值，报告可以四舍五入到三位小数，但不能改变结论。

## 4. Debug vs Final Output Check

请确认 `report.md` 中没有引用：

- `_debug.csv`
- `_debug.png`
- debug run 的 R=20 结果

报告只能引用 `_final.csv` 和 `_final.png`。

## 5. Applied Paper Evaluation Check

请用 `references/selected_paper_notes.md` 检查 Jin (2024) 部分。

必须确保报告中：

- 没有把 exact matching algorithm 写成已知，除非 notes 已核实；
- 没有把 caliper / replacement / one-to-one matching 写成已知，除非 notes 已核实；
- 没有把 matching covariates 的 timing 写成 definitely pre-treatment，除非 notes 已核实；
- 没有把 event-study specification 写成完全核实；
- 没有把 placebo design 写成完全核实；
- 没有把 firm fixed effects 或 city fixed effects 写成已核实，除非 notes 已核实；
- 保留了 identification risks，包括 unobserved time-varying confounding、anticipation、concurrent local policies、external validity changes from common support restrictions。

如果发现表述太强，请直接改成谨慎表述。

## 6. Code and Reproducibility Check

请检查：

- `main.py --mode debug` 可运行；
- `main.py --mode final` 有明确 final 设置；
- final mode 不会引用 debug 文件作为 final；
- `requirements.txt` 包含必要依赖；
- README 是否说明如何复现；
- relative paths 是否合理；
- final outputs 是否可以从代码重新生成；
- estimators 是否没有使用 forbidden variables `alpha` 和 `u`。

不要重新运行完整 final Monte Carlo，除非有必要。  
可以运行轻量检查命令，例如：

```bash
python -m compileall src
python main.py --mode debug
```

如果运行 debug，会重新生成 debug 文件，这是可以的，但不要覆盖 final 文件。

## 7. Make Minimal Fixes

你可以直接做小修，例如：

- 修正数值不一致；
- 修正图表路径；
- 删除 debug 引用；
- 把过强论文评价改成谨慎语言；
- 补充遗漏的 AI usage disclosure；
- 更新 README 的复现说明；
- 修正错别字或格式问题；
- 更新 checklist 状态。

不要大改 DGP、estimator 或 final results。  
如果发现需要改代码核心逻辑，先停下来说明原因，不要静默修改。

## 8. Update AI Usage Log

请自动更新 `AI_USAGE_LOG.md`，新增 final review and revision 记录。

日志中必须包含：

- 本次 prompt 摘要；
- 你检查了哪些文件；
- 发现了哪些问题；
- 修改了哪些文件；
- 哪些问题仍需我人工确认；
- 采纳状态写成 `Pending student review`。

如果你修改了之前记录的状态，请说明原因。

## 9. Output Format

请按以下格式回复：

### 1. Assignment Requirement Check
### 2. Numerical Consistency Check
### 3. Debug vs Final Output Check
### 4. Applied Paper Evaluation Check
### 5. Code and Reproducibility Check
### 6. Fixes Made
### 7. Files Modified
### 8. Remaining Issues for Student Review
### 9. Submission Readiness Assessment
### 10. AI Usage Log Update
~~~

## 最终责任声明

我确认，本作业的 DGP 设计、代码运行、final 表格和图形、结果解释、Jin (2024) 的应用论文评价，以及 AI 使用说明均经过我审阅。AI 工具仅用于辅助规划、实现、调试、证据整理、写作和审查。所有最终提交内容由我负责。
