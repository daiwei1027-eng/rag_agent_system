# 阶段三交接：证据约束回答与 Agent 可靠性

交接日期：2026-10-13。项目根目录：`C:\Users\admin\PycharmProjects\Deeplearning_Study\rag_agent_system`。

## 接续结论

阶段一完成真实模型、Agent Loop、多工具和失败回传链路。阶段二已具备固定协议、正式检索基线、两组 Agent 基线、人工评分和可回溯的错误分析；随后还完成提示诊断、候选扩展、故事边界分段及数据版本迁移。用户现要求进入阶段三。

阶段三先解决当前有证据仍编造、引用不能支持整句、不可回答题不正确拒答的问题，再依据验收结果安排服务化。进入新阶段不要求先达到某个准确率门槛，也不继续无限追加阶段二调参。最新 v2 分段实验的人工终评尚未冻结，作为第一项简短收尾任务保留；不能将用户要求交接理解为确认所有待判答案。

## 新对话先读什么

按下列顺序阅读，不需要重新逐本审查所有旧 Notebook：

1. [AGENTS.md](C:/Users/admin/PycharmProjects/Deeplearning_Study/rag_agent_system/AGENTS.md)：学习优先，核心实现与取舍默认由用户完成；用户明确要求代做时遵从。Git 提交和推送由用户完成。
2. [阶段二计划](C:/Users/admin/PycharmProjects/Deeplearning_Study/rag_agent_system/docs/stage2-evaluation-plan.md)及[运行协议](C:/Users/admin/PycharmProjects/Deeplearning_Study/rag_agent_system/docs/stage2-evaluation-protocol.md)：理解分母、正负例与评分规则；其中旧参数描述须结合后续运行快照阅读。
3. [最新学习日志](C:/Users/admin/PycharmProjects/Deeplearning_Study/rag_agent_system/docs/learning-log/2026-10-13.md)：按追加时间阅读，较早的“未完成”可能已被后文更新。
4. [Agent 人工复核](C:/Users/admin/PycharmProjects/Deeplearning_Study/rag_agent_system/docs/stage2-agent-review.md)：区分已确认评分与末节 v2 待确认初评。
5. [数据迁移审查](C:/Users/admin/PycharmProjects/Deeplearning_Study/rag_agent_system/docs/chunking-v2-migration-audit.md)：理解来源范围、编号迁移及已验证/未验证部分。

旧 [stage2-handoff.md](C:/Users/admin/PycharmProjects/Deeplearning_Study/rag_agent_system/docs/stage2-handoff.md)是进入阶段二前的历史交接，不代表当前评估脚本还未实现。

## 当前代码入口和契约

| 文件 | 用途与接续注意点 |
|---|---|
| [agents/loop.py](C:/Users/admin/PycharmProjects/Deeplearning_Study/rag_agent_system/src/rag_agent_system/agents/loop.py) | 手写 Agent；模型请求、执行工具、回传 observation、步数与重复调用保护。非空最终文本可成为 completed，未进行答案语义验收。 |
| [agents/models.py](C:/Users/admin/PycharmProjects/Deeplearning_Study/rag_agent_system/src/rag_agent_system/agents/models.py) | AgentResult 为 status / answer / trace / error；保持当前四字段契约。 |
| [agents/llm_client.py](C:/Users/admin/PycharmProjects/Deeplearning_Study/rag_agent_system/src/rag_agent_system/agents/llm_client.py) | 本地 Qwen 工具调用适配器，chat(messages, tools)；阶段三可复用，先不换模型。 |
| [agents/prompts.py](C:/Users/admin/PycharmProjects/Deeplearning_Study/rag_agent_system/src/rag_agent_system/agents/prompts.py) | 当前短提示及 build_agent_prompt；注释中的长提示是失败实验，不是当前模板。 |
| [scripts/eval_agent.py](C:/Users/admin/PycharmProjects/Deeplearning_Study/rag_agent_system/scripts/eval_agent.py) | 固定 12 题、装配工具、HistoryClient、run_case、加载/预热/逐题记录；不是服务入口。 |
| [scripts/eval_retrieval.py](C:/Users/admin/PycharmProjects/Deeplearning_Study/rag_agent_system/scripts/eval_retrieval.py) | 正式 40 正例的纯检索评估；当前仍固定候选 20，不因 YAML top_k=50 自动变成 50。 |
| [evaluation/benchmark.py](C:/Users/admin/PycharmProjects/Deeplearning_Study/rag_agent_system/src/rag_agent_system/evaluation/benchmark.py) | 推理前校验题集、manifest、索引、文段、负例故事范围与模型设置的版本绑定。 |
| [ingestion/story_chunking.py](C:/Users/admin/PycharmProjects/Deeplearning_Study/rag_agent_system/src/rag_agent_system/ingestion/story_chunking.py) | 统一短长故事输出、故事内 token 窗口、原文字符区间及连续 faiss_id。 |
| [tools/search_docments.py](C:/Users/admin/PycharmProjects/Deeplearning_Study/rag_agent_system/src/rag_agent_system/tools/search_docments.py) | 真实检索工具；保留当前文件拼写。eval_agent 中还有自己的 handler，修改时先查实际调用入口。 |

工具返回统一六字段：chunk_id、text、score、source、rerank_score、rerank_rank。未重排时后两项为 null。调用方 top_k 是请求返回数量，通常至多返回该数量；当前正式实验每次请求并得到 5 条。不要把评估提示要求 5 条改成所有场景都硬编码 5 条。

HistoryClient 在 chat 前 deepcopy(messages/tools)，记录失败请求也不改变原异常路径。run_case 每题清空 history，返回 query_id、question、prompt、elapsed_seconds、result、model_requests。耗时围绕 agent.run，写盘在计时外；加载和 q002 预热另记。模型请求快照不等于 tokenizer 渲染后的完整 prompt 或原始 token 输出。

## 成套数据与当前配置

旧资产 `data/tinystories.faiss`、`data/tinystories_chunks.json`、备份及旧题集、旧记录全部保留。不要覆盖旧目录，也不能给新索引配旧 chunk ID 标注。

新正式 bundle：

```text
data/chunking_v2/20261013-141109-775427-qwen128-overlap32-story-boundaries/
```

该目录中的 tinystories_chunks.json、tinystories.faiss、tinystories_queries.jsonl、tinystories_benchmark_manifest.json、tinystories_absence_evidence.json 成套使用。版本为 `stage2-story-boundaries-qwen128-overlap32-v2-reviewed`。

- 来源保持旧前 100 万 Qwen 正文 token：5092 篇保留故事，前 5091 篇完整，最后一篇只保留原来的 209-token 前缀。不得自行补齐或删除最后一篇。
- 切分仍用 Qwen/Qwen2.5-0.5B-Instruct tokenizer，正文窗口 128、overlap 32；唯一分段策略变化是窗口不再跨故事。MiniLM tokenizer 只负责 Embedding 输入长度检查。
- 旧 10417 块变成 11303 块，来源没有扩容。IndexFlatIP，384 维，MiniLM 归一化向量；metadata.faiss_id 连续对应索引行，业务 chunk_id 为 story_XXXXXX_chunk_XXX。
- 所有 45 条迁移标注由用户确认 reviewed；40 正例、5 条指定故事范围内的信息缺失负例。题目、答案与语义条件不改，只迁移证据编号和范围。
- 原文区间、统一字典结构、向量顺序、索引保存重载、实际检索器加载以及版本绑定均已验收；新数据也已完成两组真实 Agent 运行。尚未单独完成新数据 RAG CLI 生成和正式 40 题纯检索运行。

新 profile 为 [configs/chunking_v2.yaml](C:/Users/admin/PycharmProjects/Deeplearning_Study/rag_agent_system/configs/chunking_v2.yaml)。**交接时该文件 reranker.enabled=false**，因为用户最后运行了无重排组；它不是有重排运行当时的配置快照。默认 [configs/default.yaml](C:/Users/admin/PycharmProjects/Deeplearning_Study/rag_agent_system/configs/default.yaml)仍指向旧数据。复跑新数据必须显式指定 --config；两组模式以运行目录 config.json 为准。

两个真实新运行的共同参数：候选 50、工具返回 5；Embedding 为 sentence-transformers/all-MiniLM-L6-v2，normalize_embeddings=true；CrossEncoder 为 cross-encoder/ms-marco-MiniLM-L6-v2，max_length=512、batch_size=8；Agent 为 Qwen/Qwen2.5-1.5B-Instruct，max_new_tokens=256，实际 do_sample=false。generation.temperature=0.2 不能理解为这两次 Agent 使用了随机采样。

正式 manifest、build_manifest 中某些“尚未真实运行”文字是构建时状态。不要为更新叙述直接改冻结的 benchmark manifest：其 hash 已绑定并保存到运行目录。当前运行状态以审查记录、本交接和学习日志为准。

## 可复现入口

在项目根目录、hf_llm 环境中运行。校验不加载模型、不创建评估目录：

```powershell
python scripts/eval_agent.py --config configs/chunking_v2.yaml --check-only
python scripts/eval_retrieval.py --config configs/chunking_v2.yaml --check-only
```

仅在需要正式端到端验收时运行：

```powershell
python scripts/eval_agent.py --config configs/chunking_v2.yaml
```

现有入口自动创建新的阶段二目录，也支持 --run-dir；阶段三运行应显式给新的 `data/evaluation/stage3/<时间戳-实验名>`。目录存在则不复用。上述 Agent 命令按当前 profile 运行无重排，不能不改开关就声称重跑了有重排组。

如果需要有/无重排正式对照，各保存独立配置和独立运行目录，除开关外其他参数固定；不要反复手改 YAML 后仅靠记忆说明运行模式。离线环境只在本地模型缓存完备时设置，按实际执行情况记入新记录。

## 已有结果：确认状态必须区分

### 已冻结的检索与 Agent 结果

旧切分正式检索基线位于 `data/evaluation/stage2/20261012-111210-861047-retrieval-v1/`。40 正例、同一份 top-20 候选：HitRate@5 无重排 27/40、有重排 38/40；MRR@20 为 0.584391 / 0.925000。q007、q038 的证据在候选 20 中缺失，重排不能补回。

最初 Agent v1 已确认：无重排严格通过 1/12、有重排 0/12。后续句末引用实验的全部 24 条评分也已确认：无重排严格通过 3/12、有重排 5/12，分别位于 `20261013-095427-474647-agent-improved_v1_citation)` 与 `20261013-095327-737486-agent-improved_v1_citation)`。相关目录有 manual_review.json。提示调整同时改变了部分实际查询，不能说是固定 observation 的纯回答实验。

长提示 v2/v3 曾使正式检索调用从 12/12 降至 3/12、0/12；同一客户端首次调用诊断证实旧短提示调用工具、长提示直接回答。保留失败实验，不再从头堆叠长规则。提示长度、示例和具体措辞的贡献仍未完全分离。

### 最新新分段结果：事实已核验，终评待确认

两个目录均位于 `data/evaluation/stage2/`：

| 模式 | 新运行目录 | 旧切分候选 50 对照目录 |
|---|---|---|
| 有重排 | 20261013-143642-156957-agent-stage2-story-boundaries-qwen128-overlap32-v2-reviewed | 20261013-100316-593488-agent-improved_v1_retrieval_top_k) |
| 无重排 | 20261013-143834-593213-agent-stage2-story-boundaries-qwen128-overlap32-v2-reviewed | 20261013-100217-139317-agent-improved_v1_retrieval_top_k) |

同模式新旧对照的模型、提示、工具 schema、每题实际 query/top_k 和生成参数相同。新资产指纹及请求快照核验通过。新两组均 12/12 completed、12/12 成功检索、每题返回 5 条，q002 也完成真实检索预热。

| 已核验事实 | 旧无重排 | 新无重排 | 旧有重排 | 新有重排 |
|---|---:|---:|---:|---:|
| 正例标注证据返回 | 3/9 | 5/9 | 7/9 | 9/9 |
| 新运行正例出现 chunk_id | — | 7/9 | — | 9/9 |
| 新运行负例目标故事返回 | — | 3/3 | — | 3/3 |

新有重排 q007 正确回答 Ben 和 Lily；q038 核心答案改为 owl。错误仍存在：有重排 q003 加入已经想念；q042 编造药名和剂量；q045 编造重量；无重排 q015 答对三岁却引用另一个故事。有重排全命中只说明检索层改善，不代表全部答案正确。

新两组中位耗时为有重排 2.1916 秒、无重排 2.0164 秒，属于单次本机观测。各目录 comparison_audit.json 保存客观核验，semantic_review_status=pending；尚无确认版 manual_review.json，不发布最终严格通过数。

## 首项收尾：批量确认最新评分

复用 Agent 复核文档末节 24 条初评，只补必要上下文并集中确认，不重新逐题布置整组审查。三处主要边界如下：

1. **无重排 q003（已确认通过）**：回答 Tim 希望即使分开友谊仍持续，引用 story_000256_chunk_001。原文 Tim 说将要分开、自己不愿意这样，随后 Jack 保证保持联系。用户于 2026-10-13 确认分离与希望维持友谊已揭露悲伤原因，接受因果概括；答案、支持、引用与严格判定通过。
2. **有重排 q038（已确认严格不通过）**：回答猫把鸟带给猫头鹰，猫头鹰检查翅膀并给药；仅引用 story_004500_chunk_001。该块从“ to a wise owl…”开始，检查给药完整，但猫带鸟的主体动作在 chunk_000 才完整。用户确认核心答案及其证据支持通过，整句引用与严格判定不通过，保持“单个所引文段支持该句全部事实”的当前要求。
3. **有重排 q040（已确认通过）**：回答 cherry 吸引 Sarah 注意，引用 story_004763_chunk_000。原文是看到结满鲜红樱桃的大树而停下指给妈妈看。用户接受 cherry 为可接受的简略表达；没有再编造接住樱桃，答案、支持、引用与严格判定通过。

上述三个边界已记录到复核文档；其余 21 条仍为初评，用户尚未明确整组确认。整组确认后才写各目录 manual_review.json，按逐题判定重新聚合。无需重复询问这三个边界；评分记录的未完成状态不影响先设计阶段三回放输入，但不得宣称最新整组评分已冻结。

## 阶段三的工作顺序

### 任务 1：隔离回答阶段，固定证据做一次对照

原理：自主工具选择、查询生成、召回、排序和最终回答都可能影响总指标。当前有重排正例已 9/9 返回证据，优先隔离最后的证据使用问题。

冻结最新有重排运行的 12 题 model_requests 中取得 observation 后、生成最终答案前的请求。保留原问题、工具结果、顺序、模型和参数；只对回答阶段增加一项约束。建议首个假设是：让回答只包含所引原文直接支持的所问事实，遇到所问的名称、剂量、重量等未说明内容就明确拒答，能否减少无依据细节，同时保住可回答题。

先由用户说明实验变量、请求构造和验收分母，助手提供接口骨架与审查。复用 HistoryClient/LocalLLMClient，不新建评估框架。回放输入不注入 expected_answer、answerable、relevant_chunk_ids 或人工判定；这些字段仅用于评分。保存父运行目录、父文件 hash、实际请求、响应和耗时，原快照不原地修改。若模型再次请求工具，应记录为回放未得到最终回答，不编造新的 observation 或默默多跑不同条件。

一组验收覆盖固定 12 题，集中复核答案、证据与引用；特别关注 q003、q038、q042、q045，并检查原先正确的题目是否退步。这测量的是给定已保存证据后的回答表现，不是新的自主检索率或完整 Agent 成功率。

**收尾条件：**一组可审查的受控结果、同口径评分、改善与退步列表以及是否采用该策略的决定。无收益也完成这次实验，不继续追加近似提示试验。

### 任务 2：有证据支持后再接入实际链路

若回答阶段对照支持该策略，用户实现最小接入：保留已验证的首次工具选择行为，在读取 observation 后施加回答约束。不要同时改首轮提示、Embedding、候选数、分段、模型或题目。若无改善，先复盘是否需要不同的回答机制，而不是直接接受一个更长模板。

引用 ID 是否属于工具返回集合可用程序检查；文段是否在语义上支持整句仍须单独判定。即使提取了原文短句，也不能据此自动认证整个答案正确。不能通过强行给所有题拒答提升负例数字。

保持 AgentResult 现有契约，质量判定先独立保存在评估记录中。只有真实缺陷或新行为才补必要测试，集中验证一次；随后跑新有重排完整 12 题，与父运行对照工具选择、证据返回、答案及引用，保存阶段三独立目录。

**收尾条件：**真实 Agent 没有丢失工具选择，收益能够从回答回放延续到完整链路；或明确记录不能延续的原因。不要把 completed 当作质量验收。

### 任务 3：冻结方案，再安排服务化

记录最终选择、适用范围、失败样例及本机成本；对未用于提示调试的题目另做一次固定检查，并如实说明并非严格独立测试集。现有 12 题已反复调试，45 题也未正式拆分，不能宣传为泛化准确率。

之后再设计最小服务接口，复用稳定的装配与结果契约。服务化的入口、资源只加载一次、请求隔离及错误响应需要另定一组验收；本交接未实施服务端。Docker 与部署技术可结合用户后续实习项目复现安排，不作为现在判断核心项目价值的门槛。

## 固定评分与工程边界

- Agent 子集仍为 q001、q003、q005、q006、q007、q015、q022、q038、q040、q041、q042、q045：9 正例、3 负例。答案正确、核心证据支持、引用正确分别报告 /9；负例正确拒答及证据支持的拒答分别报告 /3；严格通过报告 /12。
- 不可回答只针对指定故事缺失信息，不代表整个语料库无信息。未说明不等于不存在，正确拒答也需核对目标故事范围。
- 题内相关块数量随迁移变化，不能将 Recall 变化全当作检索能力变化；原评分边界保留，不按新输出放宽。
- 最新兼容验收历史记录为 38 passed；更早的 18、17、43 项是各自不同范围，不相加作全套测试数。本次交接只审查并撰写文档，未重跑测试或模型。
- 已实现快照和 SHA256 绑定，但未固定所有模型权重文件、运行依赖、硬件及渲染输入，不能声称跨机器逐位复现。
- 交接时工作区有较多未提交/部分暂存修改；用户随后自行提交，严格审查开始时 main 为 868828e549dd254f394d780025886851eab9e9f7、工作区干净。审查新增报告及学习记录尚未代用户提交。不重置、不代用户提交或推送。历史记录里的运行时绝对路径保留；配置使用项目相对路径。

2026-10-13 后续严格审查见 [项目进度审查](C:/Users/admin/PycharmProjects/Deeplearning_Study/rag_agent_system/docs/project-progress-audit-2026-10-13.md)。现有测试分两批 144 + 1 通过，但已验证环境与依赖声明不一致；模型运行异常、阶段二批量结果保留和 RAG 入口重排开关等问题尚未修复。这次审查时阶段三回放尚未实现，不把这次审查当作新的质量实验。

2026-10-18 接续：用户已完成 scripts/replay_answers.py 的三个核心函数及 main，并通过固定 12 题的假客户端编排验收，包括 24 次 A/B 调用、调用前请求保存、逐次结果保存、模拟工具请求及异常，以及第 8 次调用中断后的已保存记录。当前逐题循环结构符合约定，无需改成先准备全部请求的两段循环。

同日真实运行已完成，目录为 data/evaluation/stage3/20261018-103123-691887-answer-replay-v1。两组各 12/12 completed，父文件指纹与固定证据 A/B 变量核验通过；A 的 12 个答案也与父运行逐字一致。用户随后回复“003可以接受”，确认本次 B 组 q003 通过；包含此确认的当前初评 A/B 严格通过均为 8/12。q003/q042 改善，但 q007 错误拒答、q015 漏引用，q038 引用及 q045 重量幻觉未修复。其余 23 条仍待用户整组确认，未生成确认版 manual_review.json；当前无总体严格通过收益证据，建议不直接采用该后置指令。具体逐题依据见运行目录新增 review.md、review_draft.json、comparison_audit.json 及 [最新回放学习日志](C:/Users/admin/PycharmProjects/Deeplearning_Study/rag_agent_system/docs/learning-log/2026-10-14.md) 末节。

## 历史接续指令（已由文末最新状态取代）

请按 docs/stage3-handoff.md 接续。先读 AGENTS.md、最新学习日志、Agent 复核文档与交接中的关键代码。阶段二基线已完成，新分段两组真实运行已核验。无重排 q003 已确认通过，有重排 q038 已确认核心答案通过但引用及严格判定不通过，有重排 q040 已确认通过；其余 21 条初评尚未明确确认，不重复询问三个已确认边界，不发布整组最终分数。下一步只推进阶段三任务 1：固定已有 observation 的回答阶段对照，明确它与修改首次 PROMPT_TEMPLATE 后重跑 Agent 的区别。请按“原理 → 核心实现 → 一组验收 → 复盘”推进，核心设计与实现先让用户动手；用户明确要求代做时执行。不要再从头扩提示、换模型、扩语料或搭服务框架。新实验保存独立目录，每次回答给明确下一步，Git 提交和推送由用户完成。

## 最新状态：2026-10-19 最小服务收尾

用户已完成共享 Agent 装配、FastAPI 生命周期、输入校验、串行锁、模型异常返回、请求日志与 Dockerfile。
依赖声明、版本约束、requirements、Git / Docker 忽略规则已统一，安装元数据刷新后 pip check 通过。
用户已构建并启动 Linux CPU 镜像，从宿主机 8001 调用真实检索问答，回答 Lily 并给出支持它的 chunk_id。
容器健康检查和三种无效输入检查通过；README 已更新，具体范围见
[服务验收记录](service-acceptance-2026-10-19.md) 和 [运行环境说明](runtime-environment.md)。

当前已完成约定的最小服务化、容器演示与说明文档范围。继续协作时先读上述最新记录，
不要按历史指令重新布置回放实现、提示试验或服务搭建。阶段三其余 23 条人工评分仍待确认，
这是一项已披露的结论局限，不将初评发布成最终分数。Git 提交和推送由用户完成。
