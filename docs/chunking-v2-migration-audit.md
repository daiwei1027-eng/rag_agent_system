# 逐故事切分 v2：兼容性审查与替换条件

日期：2026-10-13。结论：**当前 notebook 产物不能直接替换现有数据。** 核心接口支持新的字符串 chunk ID；生产数据、索引、标注和选择入口尚未成套迁移，未验收前不得切换默认配置。

本次审查不生成正式 v2 数据或索引、不改现有题集、不切换默认配置，也没有修改用户正在编写的 notebook。这里的“兼容替换”是接口、数据关联、评估与回退均经过验证，不承诺新数据必然使每题答案或所有指标更好。

## 范围与实际证据

- 静态扫描当前项目 58 个 Python 文件，包括 src、scripts 与 tests；逐项核对 ingestion → FAISS → reranker → context/tool observation → RAG/Agent → evaluation 的数据依赖。
- 读取当前三个 notebook 的代码单元。重点审查 split_tinystory.ipynb；check_faiss_chunks.ipynb 中有覆盖旧 chunks 文件的转换单元，不能用于生成 v2。
- 扫描用户提供的早期 17 个 notebook 的代码单元，完整追溯 16/17 中的分段与索引链路。Alpaca/LoRA adapter 与训练 checkpoint 不是 TinyStories 文段索引的生成依赖；当前项目也没有加载这些 adapter。
- 旧 indexes/tinystories.faiss 与当前 data/tinystories.faiss 哈希完全一致。旧 chunks 为 list[str]，当前为 list[dict]，10417 条文本和顺序一致。
- 读取正式 45 题、manifest、5 条 absence evidence 的字段与引用关系，以及阶段二评估协议。
- 现有 models/context/metrics/pipeline/search_documents/reranker/CLI/config/prompt 相关检查：**27 passed**。首次沙箱运行在 pytest 临时目录遇到权限错误，获准在沙箱外重跑通过。
- 单独执行一次接口诊断：真实的两向量内存 IndexFlatIP，加假 encoder/reranker/LLM，验证字符串 ID 在映射、检索、工具、Agent 和 RAG 中完整保留。没有加载 Qwen 或生成真实 v2 索引。结果：data/archive/evaluation/historical/stage2/migration-audit-20261013/contract_checks.json。

这些证据证明部分接口能力，**不是尚不存在的完整 v2 数据集已经验收通过**。未执行全项目测试或新数据上的真实端到端实验。

## 已确认的旧生产链路

hf-llm-playground/notebooks/17.ipynb：

1. load_dataset("roneneldan/TinyStories", split="train")，没有记录 revision。
2. 用 Qwen/Qwen2.5-0.5B-Instruct tokenizer 对每篇故事编码，add_special_tokens=False。
3. 将每篇 token ID 直接拼接，累计达到 100 万后取 all_token_ids[:1_000_000]。没有保留故事边界；最后一篇可能只保留前缀。
4. 按 128 token、32 overlap 切成 10417 块，再 decode。
5. SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")，batch_size=64、normalize_embeddings=True。
6. 按 chunks 列表顺序生成 float32、384 维向量，依同一顺序加入 IndexFlatIP。
7. 保存索引和 list[str]；当前项目后来将文本包装为带 metadata.faiss_id 的对象。

新方案使用故事边界、MiniLM token 长度、256 上限与 16 overlap，属于一组预处理变化；不能称为只改变某一个 separator。若需要单项因果结论，需另设计消融。

## 必须处理的迁移问题

| 编号 | 当前事实与位置 | 替换前必须完成 |
|---|---|---|
| M1 | split_tinystory.ipynb 没有 faiss_id。FaissRetriever._build_id_mapping 在 faiss_retriever.py:40 强制读取整数 metadata.faiss_id。本次真实复现 Invalid faiss_id for chunk story_000000_chunk_000。 | 汇总全部生产 chunks 后，按最终建索引顺序赋 0…N-1 的唯一整数 faiss_id。测试用 test_long 等记录不得混入生产语料。 |
| M2 | 检索器检查数量、映射范围和维度，但不能发现同数量的错误文本/向量配对；也不校验索引类型、归一化或构建模型版本。 | 新文本必须重新生成整套向量和独立索引；采用相同 MiniLM、归一化、float32、IndexFlatIP。用同一个有序列表保存 JSON、生成向量及 index.add；记录各文件 hash、模型/tokenizer revision 与顺序。不能复用旧索引配新文本。 |
| M3 | 旧语料按 Qwen 前 100 万 token 截断；当前 notebook 尚无批量来源范围与 revision 固定。 | 先固定原始数据 revision/本地指纹、顺序、每篇 source_index 和边界故事保留范围。核对新来源覆盖与旧语料；若补齐末尾整篇或改选取范围，记录并明确属于语料变化，不能声称同语料分段对照。 |
| M4 | 短故事保留原文，长故事 decode() 后大小写与空格改变；本次诊断确认长故事输出转小写。WordPiece 边界也可能切进单词。 | 用 fast tokenizer 的 offset_mapping 取原始 story 的字符片段，保存 start_char/end_char 与原始故事快照，再编码片段确认 token 数合规；窗口边界优先落在词边界。不要把 decode 的规范化文本当逐字原文引用。 |
| M5 | 40 条正例 relevant_chunk_ids、evidence[].chunk_id 是旧编号；5 条负例的 absence_evidence.story_chunk_ids 和外部 absence JSON 中的故事 ID 也属于旧索引。 | 保留 query_id、问题、预期答案和语义标准，另建 v2 标注文件。用原故事及支持答案的证据区间映射新 chunk；验证每个正例相关块足以支持完整所问内容。迁移所有负例故事范围与辅助证据；负例的 relevant_chunk_ids 仍为空。 |
| M6 | eval_agent.py:189/193、eval_retrieval.py:40/89、eval_rag.py:24 固定旧题集/manifest。前两者只比较 queries hash，虽记录索引和文段 hash，却没有与预期语料绑定校验。 | 增加明确的评估配置/题集/manifest 选择入口，并绑定成套资产。启动前检查所有正例及负例故事 ID 存在、题集和语料版本匹配、hash 正确；混用 v1/v2 必须直接报错，不能输出全零或看似有效的分数。 |
| M7 | diagnose_retrieval.py 固定旧 target IDs、旧 source run，并核对旧资产 hash；evaluation_data_creating.ipynb 同样写死 1500/9250。 | 历史诊断保留给 v1。v2 诊断从选定新标注读取目标；不要修改历史运行文件来通过旧 hash 校验。check_faiss_chunks.ipynb 的覆盖式转换单元不应重新执行在生产文件上。 |
| M8 | 新 chunk 长度与数量改变，现有 ContextBuilder 没有整体 token budget；当前 RAG 引用 [rank]，Agent 引用 chunk_id。 | 在新数据实际 RAG/Agent smoke 中检查上下文长度及引用解析/人工判断；保持原来的两套引用契约和评分。长字符串 ID 能在代码中传递，不代表真实模型一定遵守；必须看新数据上的真实结果。 |

补充限制：eval_retrieval 的候选/重排排序固定 20；eval_rag 固定候选 50、重排 20、context 5，并总是装配重排。它们不会因为改 YAML 而全部同步。迁移对照必须记录实际运行参数；这与数据读取兼容性分开处理。

## 已兼容的部分

- DocumentChunk.chunk_id 是字符串，load_chunks 保留 metadata；没有要求业务 chunk_id 必须为整数。
- CrossEncoderReranker 使用 dataclasses.replace 保留 chunk 与 metadata；不依赖旧故事编号。
- ContextBuilder、search_documents、eval_agent 的工具结果、Agent Loop 与 RAGResult 能保留 story_000001_chunk_000 这样的 ID。
- metrics 用字符串集合比较 ID，不要求数值格式；有正确的新标注即可使用。
- calculator、time、工具 schema 参数、模型适配器不需要因切分迁移而重写。
- 不存在把向量标签与业务 chunk_id 绑定为同一个字符串的要求；faiss_id 是顺序整数，chunk_id 可以带 story 前缀。

不能因此省略标签迁移：新旧 ID 不相同，拿旧 relevant_chunk_ids 与新检索结果比较会产生错误评分。把新块强行改名为旧数字也不能解决证据含义变化。

## 生产 chunk 的完整契约

```json
{
  "chunk_id": "story_000001_chunk_000",
  "text": "原始故事中的连续片段，保留原文",
  "source": "tinystories",
  "metadata": {
    "faiss_id": 0,
    "story_id": "story_000001",
    "source_index": 1,
    "chunk_index": 0,
    "start_char": 0,
    "end_char": 20,
    "token_count": 10
  }
}
```

数字仅示意，不是可直接使用的数据。要求 text == raw_story[start_char:end_char]；end_char 为不包含边界。token_count 以实际 MiniLM tokenizer 包含特殊 token、不开截断重新计算。faiss_id 在最终列表确定后赋值，不在单故事函数中硬编码为 0。

保存原始故事快照使 quote、offset、story_id 可追溯；如果仅保留末篇前缀，应记录原篇文本与 retained_end，不能将未纳入的尾部误计为已检索语料。

## 成套产物与入口

建议单独目录 data/chunking_v2/，保存：

- 原始故事快照与来源范围记录。
- tinystories_chunks.json 和 tinystories.faiss。
- tinystories_queries.jsonl、tinystories_absence_evidence.json、v2 benchmark manifest。
- 构建记录/manifest：语料版本、来源 revision、chunking 参数、Embedding/tokenizer 参数、模型版本、数量及文件 SHA256。
- 旧证据 → 原故事/证据区间 → 新证据 ID 的迁移审查表。

新配置 profile 可命名 configs/chunking_v2.yaml。RAG CLI 已支持 --config；eval_agent/eval_retrieval/run_agent 等尚未提供同样选择能力，必须实际增加并验收，不能仅创建 YAML 后假定读取生效。

旧 benchmark manifest 的 files 包含草稿与日志的来源记录；不能直接把整个 files 数组当作“本次必需资产”逐一强制匹配。v2 应单独声明权威运行资产，而不混淆 provenance 与输入。

内存中的 Retriever 资源有缓存。切换 profile 后要新建组件/新进程；改磁盘路径或 YAML 不会让已加载对象自动换索引。

## 证据迁移与指标口径

旧 ID 到新 ID 可能一对多、多对一，且旧块可跨两个故事；不能只凭编号、近邻或文本局部相似做一对一替换。应先把题目定位到原故事和证据区间，再审查新块是否真正支持该题。

同一个故事的所有新块不都属于正例相关证据。多个词相似、只有答案词却缺少人物关系/限定条件的块不能简单标成 relevant。若所需证据被拆到多个块而没有单块充分支持，当前 any_sufficient_chunk 口径不能直接沿用：先调整合理边界使该题证据完整，或者明确另立多块证据协议；不能悄悄改评分规则。

负例 story_chunk_ids 是指定故事的返回证据范围，不是答案相关集合。迁移后仍检查整篇故事未说明所问信息，并保留 paired_with 与拒答理由；不能因完整故事补齐而默认负例仍有效。

保留 45/40/5、Agent 12/9/3 的题目与分母。Recall 的题内分母随标注相关块数量可能改变，不能将变化全部归为检索能力提高。对照同时报告 Hit@5/MRR、逐题证据与端到端严格通过，并披露分段/标注变化。

## 切换前的一组验收

1. **来源与文段**：确认来源覆盖；每块确为一篇故事的原文连续片段，无空块、重复 ID、跨故事重叠或未解释的丢失区间；实际 token 长度合规；faiss_id 覆盖 0…N-1。
2. **索引配对**：新 IndexFlatIP 的 N/d 与文段/模型匹配；Embedding、归一化、顺序和 hash 成套；确定性取首、中、末及 q007/q038 证据块重算向量，与对应 index.reconstruct(faiss_id) 比较，排除文本向量错位。发现异常再扩大检查。
3. **标注绑定**：45 题所有正例相关 ID、evidence quote 和 5 条负例故事范围在 v2 中正确存在且可追溯；40 正例都有充分证据；所有 12 题保留语义标准，旧标签/新索引混用启动即失败。
4. **真实运行**：按选定新 profile 跑一次检索检查、一题 RAG、一题 Agent，检查 observation/text/引用。随后正式 40 题检索与 12 题 Agent 按冻结参数、独立运行目录对照；人工评分未确认前不宣称严格通过率。
5. **回退**：分别通过 v1/v2 profile 选择到正确成套文件，v1 原始 hash 与历史结果保留。旧 profile 的代表性检索能够复跑；不要复用阶段一或任意旧输出目录。

这些是一组替换验收，不要求大量追加相似单元测试。通过之后才能说实际 v2 产物能够兼容替换；目前状态仍是未完成。

## 下一步范围

先修订 notebook 输出契约与原文保留：明确来源范围、保存原始故事及字符区间、生产汇总后分配 faiss_id。核心切分与技术取舍由用户动手；助手可审查并完成机械性版本记录与迁移准备。完成前不生成全量正式替换或改默认路径。新索引和标注迁移安排在同一迁移任务中，不能留到默认切换后补。

## 追加：受控版本实现与局部验收

后续用户明确要求保持变量控制，因此当前实验恢复 Qwen/Qwen2.5-0.5B-Instruct 的正文窗口 128、overlap 32，仅将窗口限制在单故事内。MiniLM tokenizer 用于输入长度检查，Embedding 模型保持不变；此前 MiniLM 256/16 是另一组预处理方案，不作为本轮单变量设置。

按用户明确要求，完整代码已实现于 src/rag_agent_system/ingestion/story_chunking.py。chunk_story 的短长故事共用同一构造路径，顶层严格为 chunk_id/text/source/metadata；metadata 均包含 faiss_id、story_id、source_index、chunk_index、start_char/end_char、window_token_count、token_count、embedding_token_count 与 legacy_decode_matches_original。build_story_chunks 按最终顺序连续分配 faiss_id，避免逐篇从零拼接导致冲突。字符片段保留原文；默认若与相同 Qwen token 窗口的旧 decode 不一致，明确报错要求检查；若 MiniLM 输入超限则报错，不静默截断或改变窗口。

metadata.token_count 当前明确为 Qwen 正文重新编码数；embedding_token_count 才是 MiniLM 包含特殊 token 的数。此前契约示例 token_count 的 MiniLM 定义由此更新，使用明确字段区分两种 tokenizer 口径。旧核心加载器不依赖这两个附加计数字段，仍要求 faiss_id 为整数。

一组验收：新函数边界/格式检查及已有 models/context/metrics/pipeline/search_documents 检查共 **18 passed**（6 项新检查）；另外使用本地 Qwen 与 MiniLM tokenizer 检查原始来源前 100 篇真实故事，生成 202 块，字典字段统一、faiss_id 连续、原文片段对应、全部与旧 decode 一致、MiniLM 输入均不超限。来源 0、41 的实际输出也单独核对。此为局部真实 tokenizer 与格式检查，尚未构建正式新索引、完成全量来源范围/证据迁移或跑真实新数据 Agent。默认配置与旧资产仍未切换。


## 追加：当前迁移状态——全量文段通过，索引与标注待完成

当前正式来源快照已验证与旧 100 万 Qwen token 完全一致；基于该快照的全部 5092 篇保留文本生成 11303 块。输出目录 data/chunking_v2/20261013-141109-775427-qwen128-overlap32-story-boundaries/ 的 build_manifest.json 记录全量验收和哈希。M1 的 faiss_id 输出、M3 的来源范围、M4 的原文/旧 decode 一致性已在这份实际产物上验证；长短故事所有字段一致，源字符区间覆盖无缺口，MiniLM 输入最大 152 token。新数据可被既有 load_chunks 与 _build_id_mapping 加载。

M2 的新向量/索引配对、M5 正负例证据迁移、M6 资产绑定入口及 M8 的真实 RAG/Agent 验收仍未完成；完整替换状态仍不通过。默认配置与旧数据不变。文段数量增加由故事内窗口重新开始产生，不能与旧索引 10417 条配对。


## 追加：实际新索引配对通过

同一版本目录已生成 tinystories.faiss（IndexFlatIP、11303 条、384 维），记录 index_build.json；新资产 hash 已写入 build_manifest.json。全量向量顺序、有限值、归一化、序列化重载检查通过，首中末独立编码样本匹配；全新现有 FaissRetriever 从磁盘加载新配对并真实检索通过。MiniLM 本地 snapshot commit 已记录。M2 实际新索引配对验收完成；M5/M6/M8 仍待完成，当前不切换正式使用。


## 追加：M5 自动源位置迁移完成，语义确认待完成

prepare_benchmark_migration.py 已生成受 bundle/旧题集哈希校验的 45 题迁移草稿。40 正例均定位原 quote 的同故事新候选，5 负例定位同一完整故事并与原 absence 文本忽略空白匹配；题目与语义字段不变，新 ID 和 quote 存在性检查通过。草稿及带所有目标故事上下文的复核表保存于新版本目录 benchmark_migration_draft/。全部标注状态仍为 pending_migration_review，不能直接进入正式评分。M5 的充分证据语义审查、M6 的入口绑定与 M8 的真实端到端验收仍待完成。


## 追加：用户确认标注，M5/M6 已完成

用户明确确认迁移复核完成，正式 v2 JSONL、负例证据与 benchmark manifest 已冻结。configs/chunking_v2.yaml 绑定五份版本文件，旧默认配置保留。统一 benchmark 预检阻止新旧数据混用，并检查实际 ID/quote 与 reviewed 状态。eval_agent/eval_retrieval/eval_rag/run_agent 接受 --config；前两者 --check-only 的 v1/v2 校验通过。38 项相关检查通过。

M5 正负例标注迁移与 M6 选择/绑定入口验收完成。M8 新数据的真实 RAG/Agent 模型调用、引用行为和质量评估仍需执行；当前状态不能称为所有行为已完美替换。下一步按新 profile 跑真实评估，用旧版本同参数结果对照。profile 选择改变后新进程会实例化新检索器，避免复用旧资源缓存。


## 追加：真实 Agent 链路已跑通，质量评分待确认

用户在新 profile 下完成有/无重排各 12 题真实 Agent 运行，全部 completed、成功检索并正常读取新编号；无接口、数据映射或标签版本错误，哈希与请求快照核验通过。有重排标注证据返回 9/9，无重排 5/9。说明实际新数据已通过 Agent 使用链路验收；结果仍包含错误答案、错误引用和编造，不能把数据兼容替换理解为回答全正确。人工质量评分待用户确认；未单独重跑 RAG CLI 模型生成验收。
