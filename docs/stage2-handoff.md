# 阶段二新对话交接

> 2026-10-13 更新：本文保留为进入阶段二前的历史交接。阶段二基线、后续实验及进入阶段三的当前指令见 [stage3-handoff.md](C:/Users/admin/PycharmProjects/Deeplearning_Study/rag_agent_system/docs/stage3-handoff.md)。请勿按本文的旧代码状态重新实现已有评估入口。

日期：2026-10-12。项目根目录：`C:\Users\admin\PycharmProjects\Deeplearning_Study\rag_agent_system`。

## 当前状态

阶段一已收尾，目标是证明真实链路可运行，不是证明稳定成功率。本地 `Qwen/Qwen2.5-1.5B-Instruct` 通过 `LocalLLMClient.chat()` 输出工具请求；`Agent.run()` 执行 `calculator`、`time`、`search_documents`，将 observation 回送模型，并返回统一的 `status / answer / trace / error`。`trace` 是完整消息历史，包含 user、assistant 工具请求、tool observation 和最终 assistant 回答。搜索工具使用真实 FAISS，可选 CrossEncoder 重排；返回 `chunk_id / text / score / source / rerank_score / rerank_rank`。

阶段一的七条真实记录位于 `data/agent_runs/stage1-2026-10-12/`；详细结果和复现命令见 `docs/learning-log/2026-10-12.md`。直接问答、强制检索、自动检索、计算、时间、双工具和工具失败回传均走通。自动检索案例答对 Lily，但最终文本漏写 `chunk_id`；这是阶段二“答案正确”和“引用正确”必须分开计分的真实例子。工具失败时，observation 的 `ok=false` 可以对应任务 `status=completed`，因为模型已解释错误。

阶段一记录保存完整配置、工具 schemas、每轮模型输入快照和 Agent 结果；**没有**保存 tokenizer 渲染的完整 prompt、token 序列、索引哈希或每轮耗时。相关检查曾通过 43 项，但这不是全项目测试或成组模型评估。原 `README.md` 的 Day 22 内容仍描述旧演示接口，理解当前实现以代码及最新学习日志为准。

## 阶段二目标与路径

详细任务和验收条件见 `docs/stage2-evaluation-plan.md`。本阶段先固定协议，再用正式 TinyStories 题集测检索与 Agent 端到端表现，比较有/无重排，保存逐题记录和错误分析；后端服务化与针对性优化在基线之后。不要把七条演示场景汇总为成功率，也不要在运行中不断替换问题来提高数字。

关键资产：

- 正式题集：`data/benchmark/tinystories_queries.jsonl`，45 条已复核题，40 条可回答、5 条故事范围内不可回答；版本与已知局限见 `data/benchmark/tinystories_benchmark_manifest.json`。旧 `data/evaluation/tinystories_queries_draft.jsonl` 不用于正式评分。
- 现有检索指标：`src/rag_agent_system/evaluation/metrics.py`；旧检索评估：`scripts/eval_retrieval.py`，目前硬编码绝对路径并读取草稿，需要整理后再用于新实验。
- 旧 RAG 评估：`scripts/eval_rag.py`，只跑 5 题，输出目录也硬编码；可参考结果结构，但不能直接当阶段二 Agent 基线。
- Agent 装配与保存记录：`scripts/run_agent.py`；Loop：`src/rag_agent_system/agents/loop.py`；模型适配器：`src/rag_agent_system/agents/llm_client.py`；工具包装：`src/rag_agent_system/tools/search_docments.py`（沿用当前文件拼写）。
- 当前默认配置：`configs/default.yaml`；本地模型、FAISS 索引和文段数据须在机器上已可用。`run_agent.py --all` 是七个阶段一演示场景，尚无正式 12 题批量 Agent 评估入口。

## 给新对话的工作指令

请先阅读项目根目录 `AGENTS.md`、`docs/stage2-evaluation-plan.md`、`docs/learning-log/2026-10-12.md` 和上述关键代码。**第一步只完成阶段二任务 1：固定正式题集、12 题子集、提示词、指标分母、判定规则及运行参数，并检查它们与现有代码是否一致。** 然后按“原理 → 核心实现 → 一组验收 → 复盘”推进，不要一开始就扩展框架或大量新增测试。用户求职导向，核心评估设计和实现优先由用户动手；如果用户明确要求代做，则按要求完成。每次回答给出明确的下一步。Git 提交和推送由用户完成。

可先从这条已验证的阶段一命令理解记录结构（它会重跑并覆盖目标目录同名文件；需要保留旧记录时换一个目录）：

```powershell
python scripts/run_agent.py --all --record-dir data/agent_runs/stage1-2026-10-12
```

新评估的输出请使用独立运行目录，保存正式题集版本、配置、逐题结果与耗时；不要覆盖阶段一记录。
