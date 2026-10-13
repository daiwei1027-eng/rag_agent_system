# 阶段二运行协议 v1

固定日期：2026-10-12（Asia/Shanghai）。本次仅完成任务 1：固定评估口径并核对代码；未运行新基线、未修改核心实现。后续核心实现和人工评分由用户完成，助手负责审查与机械性整理。运行前如修改本协议，应递增协议版本并说明原因；看到结果后不调整题目、提示词或评分口径来改善指标。

## 原理与范围

检索评估回答“标注证据是否进入候选并排在前面”；Agent 评估回答“是否自主检索、利用证据、正确回答并引用”。两者分开，才能区分候选遗漏、排序问题与回答问题。任务级 `completed` 仅表示流程结束。

## 1. 正式资产与版本

唯一正式题集：`data/benchmark/tinystories_queries.jsonl`。版本 `day21-stage1-v1.2`，来源 manifest 为 `data/benchmark/tinystories_benchmark_manifest.json`。

| 资产 | 当前 SHA256（2026-10-12 实际读取） |
|---|---|
| 正式题集 | `9a32ae2cc858007084b0bc79e002850ea15c355259d09f788e530e08badf2acf` |
| benchmark manifest | `2361d8e5486677707f3647b586e723fa3c4a8bee1bb90c6ab6722cadfdd11b41` |
| `data/tinystories_chunks.json` | `79c755c56d0c05482e8c497f503173c91b46e124216c6f44b91a7c505bd0b5eb` |
| `data/tinystories.faiss` | `8fc8edd5547a6b8fe7828ceac7b1f82a5a96bf9697f4f7bc7e9cb77057194a2d` |

已检查：45 条、45 个唯一 ID；40 条可回答、5 条不可回答；全部 reviewed；相关 ID 均为字符串且存在于 10417 条文段中；`answerable` 与相关 ID 是否非空一致。题集 hash 与 manifest 的 `dataset_sha256` 一致。manifest 的 `files` 中草稿路径是来源追溯，不是正式实验输入，不据此加载草稿。

负例 q041–q045 限于指定故事；保留 `tinystories_absence_evidence.json` 供人工审查。空相关 ID 代表故事没有请求的答案，不代表检索不到该故事。

模型名称固定如下；名称不等于权重版本。运行前须记录实际本地 snapshot commit 或权重文件 hash、tokenizer 版本，不能只保存模型名。

- Embedding：`sentence-transformers/all-MiniLM-L6-v2`。
- CrossEncoder：`cross-encoder/ms-marco-MiniLM-L6-v2`。
- Agent：`Qwen/Qwen2.5-1.5B-Instruct`。

## 2. 检索协议

输入使用正式题目的原始 `query`。每题只召回一份 FAISS top-20 候选；基线保留原排序，对照用 CrossEncoder 对这同一份候选排序，保留完整 20 条。报告前 1/3/5 条指标及 RR@20，不用 YAML 中 `reranker.top_k=5` 截断评估排序。候选不足 20 时保存实际数量，不填充重复文段。分数只用于各自排序，不比较 FAISS 与 CrossEncoder 分数大小。

令 R 为该题去重后的标注相关 ID 集合，L 为排序结果：

| 指标 | 逐题定义 | 汇总分母 |
|---|---|---|
| Recall@1/3/5 | `len(set(L[:k]) & R) / len(R)` | 40 题宏平均；每题内部的分母是该题相关 ID 数 |
| HitRate@5 | 前 5 条至少一个相关 ID 为 1，否则 0 | 命中题数 / 40 |
| MRR@20 | 前 20 条首个相关 ID 的名次倒数，无命中为 0 | 40 个 RR@20 的均值 |

q041–q045 保存排除记录，原因 `unanswerable_no_relevant_ids`，不调用要求非空 R 的指标函数，也不以 0 混入平均。重复召回 ID 不增加 Recall 命中数。`reciprocal_rank` 不接收 k，调用方必须先截断到 20。

## 3. Agent 固定子集与提示词

按下表顺序运行，两组均为同样 12 题，每题使用新的消息历史，不输入 expected_answer、相关 ID 或标注证据。

| ID | 类型 | 可回答 | 标注相关 ID |
|---|---|---|---|
| q001 | fact | 是 | 0 |
| q003 | cause | 是 | 500 |
| q005 | paraphrase | 是 | 1000, 1001 |
| q006 | multi_condition | 是 | 1250 |
| q007 | fact | 是 | 1500 |
| q015 | fact | 是 | 3500 |
| q022 | fact | 是 | 5250 |
| q038 | paraphrase | 是 | 9250 |
| q040 | paraphrase | 是 | 9750 |
| q041 | unanswerable_control | 否 | 无 |
| q042 | unanswerable_control | 否 | 无 |
| q045 | unanswerable_control | 否 | 无 |

统一 user 消息模板（`{query}` 原样替换，UTF-8 保存）：

```text
请回答 TinyStories 资料库中的问题。仅根据工具返回的原文片段回答，并给出直接支持答案的 chunk_id；编号必须来自工具结果。
如需检索，请只提出一次简短的英文查询，返回 5 条文段，然后根据返回的文段回答。
如果没有直接证据，请明确说明“证据不足”，不要猜测；不可回答时无需编造引用。
问题：{query}
```

模板不点名工具、不强制指定工具调用。沿用现有 search_documents、time、calculator schema 及注册顺序，不修改现有工具描述。当前检索工具描述本身要求 TinyStories 问题先检索，因此“自主选择”指在此提示与 schema 条件下自主生成调用，不代表无提示的工具选择能力。模板中的“一次”是指令，不是执行限制；实际多次调用须如实记录。

## 4. 运行参数与公平性

| 参数 | 固定值/规则 |
|---|---|
| 检索候选数 | 20 |
| Agent 每次搜索返回数 | 5；未来评估装配层明确固定，保存模型请求值与实际值 |
| Embedding normalize_embeddings | true |
| CrossEncoder max_length / batch_size | 512 / 8 |
| Agent max_new_tokens | 256（每次模型调用） |
| Agent 解码 | `do_sample=False`；generation.temperature 不参与 Agent 推理 |
| Agent max_steps / max_repeated_calls | 5 / 2；前者是模型轮次，后者是连续相同调用签名允许次数 |
| tool_timeout_seconds | null（当前默认，无工具超时） |
| 重排对照 | baseline=false，with_rerank=true；其余参数相同 |
| 正式运行次数 | 每组一次，固定顺序 baseline → with_rerank；失败题保留、不挑选重跑结果替换 |
| 离线与环境 | hf_llm，HF_HUB_OFFLINE=1，TRANSFORMERS_OFFLINE=1 |

Agent 搜索的预期路径是两组均召回 20，基线取前 5，对照重排后取前 5。当前无重排工具路径只召回模型请求的 top_k，尚未实现此规则。固定返回数须在评估装配层实现，不能仅假设模型遵守提示词；不用修改全局工具 schema 来达到此目的。

检索实验使用完全相同候选。Agent 实验只固定输入、工具与检索策略；模型改写查询或后续调用可能因 observation 改变，不声称两组每轮候选完全相同。保留这些差异作为端到端行为证据。

预热题固定 q002，不参与正式评分。两组正式运行前均完成相同预热，保存预热记录；模型加载和预热分别计时，不进入稳定逐题耗时。资源当前是惰性加载，不能仅计构造对象时间作为模型加载耗时。逐题计时范围为整个 `Agent.run`，不含 JSON 写盘和人工评分，使用单调时钟；CUDA 下在计时边界同步。分别报告每题秒数与每组 12 题耗时中位数（含失败题），不报告 p95。检索实验另保存每题 FAISS 和重排耗时。不得把不同组或不同加载口径的耗时合并。

当前核对环境：Python 3.11.16，解释器 `C:\Users\admin\anaconda3\envs\hf_llm\python.exe`，Windows 10 build 19045。实际运行前补充 Git commit 与工作区状态、依赖版本、CPU/GPU、各模型实际 device/dtype、模型 snapshot 标识及加载耗时；本轮未加载模型，未验证这些运行时信息。

## 5. 人工判定表与分母

每题两组分别填写：`status`、`search_called`、`relevant_returned`、`answer_correct`、`evidence_supported`、`citation_present`、`citation_correct`、`insufficient_information`、`strict_pass`、`failure_reasons`、`review_reason`。适用性不同的字段填写 N/A，不能将 N/A 当成失败混入专项分母。

- 自主检索：trace 中 assistant 发出 search_documents 调用即为是；成功返回另查 observation.ok，不混同调用与成功。
- 标注证据返回：只检查成功 search observation 返回给模型的文段，不用模型未看到的候选。可回答题与相关 ID 有交集为是；负例填 N/A，可额外检查是否返回指定故事范围文段。
- 答案正确：人工对照原题与 expected_answer 的语义，要求覆盖题目全部条件，接受等义措辞；不使用字符串相等代替评分。可回答题错误拒答为否。
- 直接证据：成功 observation 中的原文实际支持最终答案；答对但工具没有返回支持文段仍为否。不是看到相关 ID 就自动判是。
- 引用正确：可回答题必须有引用；引用须存在于成功 observation，且语义上直接支持相应答案、对应标注证据。有正确引用但同时夹带虚假或无关引用仍判否。无引用单列 `missing_citation`，即使答对也严格失败。
- 标注外文段可能有真实证据：记录原文和人工理由，但 v1 严格“标注一致引用”指标判否并标记 `unlabeled_support`；不在同一次运行中悄悄扩充相关 ID。它不同于编造引用。
- 负例正确拒答：明确表示该故事/现有证据未给出所问信息，不编造厂商、药名、剂量或克数。负例的正例引用指标填 N/A；`依据：无` 可以接受，不能要求引用空相关集合。额外引用如有，仍须来自工具且不歪曲原文。
- 负例证据审查：能返回指定故事范围原文、结合 absence_evidence 解释信息缺失，才记为证据支持的拒答；只说无法访问资料库或未检索就说证据不足，单独记录，不计严格通过。检索 top-5 不能证明全库不存在答案，不把它当作缺失证明。
- 严格通过：正例须 completed、答案正确、直接证据支持、引用正确；负例须 completed、正确拒答、返回指定故事证据且没有虚假陈述/引用。非 completed 的终止结果严格失败，仍保留已发生的检索证据。

| 汇总项（每组分别统计分子/分母） | 分母 |
|---|---|
| completed、自主检索、严格通过率 | 12 |
| 可回答题答案准确率、标注证据返回率、直接证据支持率、引用正确率、缺引用率 | 9 |
| 负例正确拒答率、证据支持的拒答率 | 3 |

错误原因允许多标签：未调用检索、工具失败、标注证据未返回、有证据但答案错误、缺引用、引用不在结果中、引用不支持答案、标注外支持、编造信息、错误拒答、非 completed。不同原因比例不可相加当成总失败率。

## 6. 独立输出与复现记录

下一次实验创建 `data/evaluation/stage2/<run_id>/`，run_id 用 Asia/Shanghai 日期时间，如 `20261012-HHMMSS-v1`；目录存在即报错，重跑使用新 ID。不写入阶段一目录，不复用旧脚本固定输出位置。

同一 run 保存：本协议与提示词快照、正式题集与 manifest 快照、absence_evidence、资产 hashes、配置与实际生效参数、运行环境与模型版本、预热与加载耗时、检索逐题排序及指标/排除记录、Agent 两组每题完整 AgentResult/工具 schemas/模型请求/observation/耗时、人工判定表与汇总。模型调用失败时也需保存发起但未获成功响应的请求，不能仅依靠 trace 中 assistant 条目重建。不要求保存模型原始 token 序列。

## 7. 与当前代码的核对结果

| 代码 | 一致之处 | 后续核心实现差异（本轮不修改） |
|---|---|---|
| eval_retrieval.py | 同份 20 候选做重排、相关 ID 用集合、已有逐题与汇总 | 改正式输入；排除 5 负例；独立目录、版本快照与耗时；RR 显式截断 |
| evaluation/metrics.py | Recall 去重、Hit、RR 定义一致；空相关集合报错 | 分母筛选由脚本负责；不需本轮扩展指标框架 |
| run_agent.py | 真实装配、完整结果、配置、schemas 与成功响应前的请求可参考 | --all 只有七个演示；无 12 题入口/耗时；同名记录会覆盖；无失败模型请求快照 |
| search_docments.py | 重排开启时用 candidate_top_k=20；输出 ID 为字符串 | 无重排时只召回 top_k；两组返回数目前由模型决定；评估装配层需固定 20→5 |
| default.yaml / LocalLLMClient | 模型、候选数、重排 max_length/batch_size、Agent token 上限一致 | Agent 不用 generation.temperature、context.top_k 或 reranker.top_k 控制返回条数；不把这些配置当成已生效 |
| eval_rag.py | 已使用正式题集，已有计时示例 | 仅五题 RAGPipeline，候选 50；不用于正式 Agent 基线 |

## 一组验收与复盘

本轮已完成静态源码核对、资产 SHA256 核对、题集数量/唯一性/状态/ID 类型/文段存在性核对；12 个子集 ID 均存在，9 正例、3 负例。没有执行模型推理或 pytest，没有产生阶段二效果指标。模型 snapshot、FAISS 运行时结构与硬件状态仍需在实验预检中记录和校验。

本任务收尾条件：以上单一协议固定题集、子集、模板、参数、分母与人工规则，并明确现有实现差异。核心学习点：Recall 的题内分母与宏平均分母不同；负例评估拒答而非 Recall；正确答案、来源支持与流程结束需要分别测量。局限：标注可能不完整，45 题未拆分，12 题是固定小样本，不能外推线上效果。

下一步由用户动手完成任务 2 的最小实现：只整理 eval_retrieval.py 的正式输入、正负例筛选与独立输出，保留现有指标和候选比较逻辑。助手审查后统一验收：40 条评分 + 5 条排除、两排序同候选集合、汇总分母为 40、输出不覆盖旧记录。此时不实现 Agent 批跑或扩展评估框架。
