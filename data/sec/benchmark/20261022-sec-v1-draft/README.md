# SEC benchmark v1 草稿：待人工复核

本目录是来源驱动的标注草稿，全部 `annotation_status=pending_review`，审核通过数为 0。
未运行 embedding、检索评分、重排或生成评测；正式 loader 应拒绝运行该草稿。

## 范围与文件

| 集合 | 总数 | 可回答 | 待核查不可回答 | 用途 |
| --- | ---: | ---: | ---: | --- |
| dev | 30 | 24 | 6 | 标注复核、开发和后续调参 |
| test | 10 | 8 | 2 | 标注复核后保留，方案冻结后最终检查 |

绑定 3091 个 chunk 和 384 维 SEC IndexFlatIP，来自 Microsoft FY2025/FY2026、
NVIDIA FY2025/FY2026、Alphabet FY2024/FY2025 的 Item 1、1A、7。
问题和参考答案采用英文，与当前语料和模型链路保持一致。

- `dev_queries.jsonl` / `test_queries.jsonl`：逐题问题、答案、证据与标注状态。
- `dev_absence_evidence.json` / `test_absence_evidence.json`：负例的完整核查范围、
  搜索词、近似证据和待复核理由，范围使用 `scope_chunk_ids`。
- `dev_manifest.json` / `test_manifest.json`：分别绑定各自题集、absence 文件、
  chunks、索引、模型 snapshot、权重/配置指纹与索引构建记录。
- `dev_review.md` / `test_review.md`：集中复核阅读版，JSONL 是标注数据源。
- `validation.json`：结构检查结果，不是语义审核或模型准确率。
- `bundle_manifest.json`：本草稿文件的最终指纹和状态。

这是同一小型 corpus 上的保留问题集，不是跨公司或跨报告的未见语料泛化评测。
两个集合的事实分组及正例证据 chunk 分开，改写/相关事实按人工 fact_group 归组。
这些结构检查不自动证明所有题目的语义独立，也不保证相关文段标注已经穷尽。
测试集仅 8 道正例、2 道负例，最终必须同时报告分子/分母，不能外推总体可靠性。

## 标注格式与证据规则

每题含 `query_id`、`query`、`split`、`category`、`fact_group`、`reference_answer`、
`answerable`、`annotation_status`、`relevant_chunk_ids`、`evidence`、`evidence_groups`、
`documents`、`constraints`、`calculations`、`review_notes`。

`documents` 明确保留公司、ticker、报告财年、期末、原文件、来源 URL、accession 和
source hash。`constraints.fiscal_years` 是**报告的财年**，不是表中所有比较列的年份。
例如 FY2025 报告同时展示 FY2024 数值，来源约束仍指向 FY2025 报告。
跨公司、跨报告问题用 document_ids 精确列出来源组合，避免 ticker/year 的笛卡尔积歧义。

`constraints` 记录问题明确要求的来源范围；当前评测入口不会自动把它用于过滤。
后续过滤应从问题或显式用户参数取得约束，并单独报告过滤实验，不能从参考答案
偷偷获得比问题更具体的路由条件。

每条证据 quote 都是实际 chunk.text 的精确子串，含原始来源定位信息；正文块 HTML
仍保留在 sections.jsonl。若同一 quote 出现在同报告/同章节的多个窗口中，已列入
该组 acceptable_chunk_ids；其他措辞不同但有效的证据仍需人工补充。

部分 Alphabet 表格的单位位于相邻文字块，因此同时标注数字和单位说明。
evidence_groups 描述最小证据组成；涉及多个事实、来源或单位时，完整支持要求每组
至少命中一个可接受文段。现有 Recall/MRR 使用扁平 relevant_chunk_ids，HitRate 仅表示
至少命中一条相关文段，不表示所有事实都已齐备。完整证据覆盖尚未增加自动评分代码。

## 评分口径

1. 检索：按既有 Recall@1/3/5、HitRate@5、MRR@20，负例不计入这些指标。
   保持候选预算和重排设置一致，记录配置；多证据任务另需检查各组覆盖。
2. 回答：包含问题要求的事实，报告/期间正确，数值及单位正确；允许等价表达和
   明确标注单位后的等值换算。计算题需以证据中的操作数为基础，百分比差值区分
   percentage points 与相对百分比变化。
3. 引用：引用 ID 必须存在，引用内容实际支持对应事实；只引用单位标题不足以支持金额。
4. 不可回答：仅针对给定报告中纳入 corpus 的三个章节，不能声称整个原始 10-K 或
   外部世界没有该信息。不得将汇总值冒充单产品值、将匿名客户猜成某家公司，或
   将模糊数量改成精确数字。若复核发现确切答案，应重标或替换该题。

以上是后续评分契约，本轮没有产生任何检索或回答分数。

## 集中复核与冻结

先阅读 `dev_review.md`，统一确认：答案是否成立、期间/单位是否正确、证据是否充分、
是否还有等价的相关 chunk，以及负例范围内是否确实没有精确答案。
负例文件的搜索词和候选上下文用于缩小复核工作量，关键词没有命中不等于事实不存在；
完整 scope 列出了需要负责的核查范围。

测试集复核通过后保留为最终检查集；开发和提示/召回调参只使用 dev。
同一事实或相关改写不能在开发和测试间重复。若看过测试结果后改进方案，应记录测试
集暴露，不再把同一批题的下一轮成绩称为首次独立测试。

完成逐题复核后，记录实际决定、修改数据并生成新的 reviewed 版本，再更新题集及
absence 的 SHA256、题数、审核计数和状态。草稿保留为历史记录，不覆盖冻结资产。
之后将 SEC 配置的三个 benchmark 路径一起指向**同一 reviewed 集合**。
当前 `SEC_v1.yaml` 尚未指向这些待复核文件，本轮未修改用户配置。
