# RAG Agent System

基于本地 Qwen 的 TinyStories RAG Agent。手写工具调用循环，结合 FAISS 检索、可选
CrossEncoder 重排、固定证据回答回放，以及 FastAPI / Docker 最小服务。

项目关注检索证据、模型回答和引用之间的关系，并保留可检查的请求、工具结果和实验记录。
当前提供本地与单进程容器演示；问答仍存在幻觉、错误拒答和引用遗漏，不作为生产可靠性证明。

SEC 迁移进度（2026-10-22）：六份报告的目标章节已生成 3091 个统一 chunk，完成
MiniLM embedding 与 384 维 IndexFlatIP 的保存、重载和现有检索器兼容验收。
当前服务仍使用 TinyStories；检索评测入口已支持动态题数、模式配置及可选重排，
不可回答证据范围已通用化；SEC benchmark 经用户复核确认后冻结为 reviewed 版本：
开发集 30 题、测试集 10 题，SEC_v1.yaml 仅绑定开发集。尚无正式 SEC 指标，
公司/财年过滤仍待完成。
资产与复现入口见 [SEC 数据说明](data/sec/README.md)。

## 当前能力与架构

```text
POST /query: question
    -> 校验输入、使用已有 TinyStories 问答提示
    -> 取得共享 Agent 的进程内锁
    -> 本地 Qwen 生成工具调用
    -> Registry 校验参数并执行工具
       search_documents -> FAISS -> 可选 CrossEncoder -> 原文片段
       calculator / time -> 计算或时间结果
    -> observation 写回消息历史 -> Qwen 继续回答
    -> status / answer / trace / error
```

- Agent 支持工具调用、observation 回传、重复调用与最大步数终止保护。
- 工具参数由手写 schema 与校验器检查，工具失败保留为结构化 observation。
- 检索资产使用故事边界和 token 窗口切分，业务 chunk_id 与 FAISS ID 映射分开管理。
- 评估区分证据命中、答案正确、引用支持与不可回答题拒答，记录资产指纹。
- FastAPI 启动时创建共享 Agent；模型和检索资源在首次使用时加载并复用。
- 服务串行执行 Agent，请求日志记录随机 request_id、任务状态及含排队时间的耗时。

`/query` 当前面向 TinyStories 问答。计算、时间及多工具的通用 Agent 演示使用 CLI 场景入口。

## 已验证的范围

2026-10-19 已完成 Windows 本地服务与 Linux CPU 容器的代表性问答验收。
容器使用 Python 3.11.17、PyTorch 2.11.0+cpu，端口为宿主机 8001 -> 容器 8000。
Lily / needle 问题返回正确人物和支持引用 `story_000000_chunk_000`。
健康检查及缺字段、空字符串、纯空白输入检查通过。

资源只读挂载、并发串行保护、模型异常后的恢复及验证局限见
[服务验收记录](docs/service-acceptance-2026-10-19.md)。
这次验收是一条真实容器问答及关键服务行为检查，不是重新运行整个质量基准。

## 资源与配置

服务当前读取 [configs/chunking_v2.yaml](configs/chunking_v2.yaml)：

| 项目 | 当前配置 |
| --- | --- |
| 生成模型 | Qwen/Qwen2.5-1.5B-Instruct |
| 生成设置 | max_new_tokens=256，客户端 do_sample=False |
| Embedding | sentence-transformers/all-MiniLM-L6-v2 |
| 索引 | IndexFlatIP，384 维 |
| 重排 | 当前服务配置 `enabled: false` |
| 数据目录 | `data/chunking_v2/20261013-141109-775427-qwen128-overlap32-story-boundaries/` |

这个 bundle 在迁移核验中包含 5092 篇保留故事和 11303 个文段。完整历史 bundle 已被 Git
跟踪；请确认所选配置对应的索引、chunks、题集和 manifest 同时存在，勿混用旧版资产。
模型权重不在仓库和镜像中。数据保留边界见 [data/README.md](data/README.md)。

## 本机安装与模型准备

以下命令在仓库根目录、Python 3.11 环境中执行。已有 `hf_llm` 环境和模型缓存时，
可以直接使用已有环境，不必重新创建或下载。

新的 CPU 本地环境可按下面的入口准备；完整安装与 wheel 来源说明见
[运行环境说明](docs/runtime-environment.md)。

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install torch==2.11.0+cpu --index-url https://download.pytorch.org/whl/cpu
python -m pip install -r requirements.txt
```

`requirements.txt` 引用 pyproject 的 `service` 额外依赖和直接运行依赖约束。
它不是完整传递依赖锁文件；本机 CUDA 环境与容器 CPU 环境分别记录。

在能够联网的本机环境中，使用 Hugging Face 缓存准备所需模型：

```powershell
python -c "from huggingface_hub import snapshot_download; snapshot_download('Qwen/Qwen2.5-1.5B-Instruct', allow_patterns=['*.json','*.safetensors','*.txt','*.model']); snapshot_download('sentence-transformers/all-MiniLM-L6-v2', allow_patterns=['*.json','*.safetensors','*.txt','*.model'])"
```

这是基于官方 [snapshot_download / 文件过滤接口](https://huggingface.co/docs/huggingface_hub/guides/download)
提供的资源准备方式。本轮验证使用已有缓存，没有重复验证空缓存下载。
默认 Hub 缓存位于 `$env:USERPROFILE\.cache\huggingface\hub`；自定义 HF_HOME / HF_HUB_CACHE
时，运行容器的 source 应改为实际缓存目录。
开启重排时还需准备 `cross-encoder/ms-marco-MiniLM-L6-v2`。
模型准备命令默认读取 main 分支，不锁定权重版本；本次观察到的缓存 revision 记在服务验收记录中。

启动本地开发服务：

```powershell
python -m uvicorn rag_agent_system.api:app --app-dir src --host 127.0.0.1 --port 8000 --reload
```

本地调试入口：[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)。

## Docker CPU 演示

需要 Docker 引擎可用，并且已经准备好上述数据和模型缓存。
镜像包含代码和 Python 依赖；数据及模型缓存通过只读目录挂载提供。
本轮实际完成了镜像依赖安装与离线缓存推理，但没有从空模型缓存重新下载权重。

从项目根目录构建：

```powershell
docker build -t rag-agent:local .
```

在 PowerShell 中解析本机目录，再启动容器：

```powershell
$ragDataPath = (Resolve-Path .\data).Path
$ragHubPath = (Resolve-Path "$env:USERPROFILE\.cache\huggingface\hub").Path

docker run --rm --name rag-agent-demo `
  -p 127.0.0.1:8001:8000 `
  --mount "type=bind,source=$ragDataPath,target=/app/data,readonly" `
  --mount "type=bind,source=$ragHubPath,target=/models/huggingface/hub,readonly" `
  rag-agent:local
```

这些是 Windows PowerShell 命令。在其他宿主系统运行时，需要按对应 shell 调整路径和续行语法。
挂载方式参见 [Docker bind mounts](https://docs.docker.com/engine/storage/bind-mounts/)。

- 健康检查：[http://127.0.0.1:8001/health](http://127.0.0.1:8001/health)。
- 接口调试：[http://127.0.0.1:8001/docs](http://127.0.0.1:8001/docs)。
- 在 POST /query 中发送下一节的 JSON；第一条问答会加载模型，CPU 耗时不能与本机 GPU 直接比较。
- 容器内监听 `0.0.0.0:8000`，`-p` 发布到宿主机 `127.0.0.1:8001`；EXPOSE 本身不建立映射。
- Dockerfile 使用单个 worker，不启用 reload。此服务的锁只约束同一个进程。
- 保持启动终端打开；在该终端按 Ctrl+C 停止，`--rm` 删除演示容器，镜像与挂载源目录保留。

Dockerfile 设置 `HF_HOME=/models/huggingface` 和 `HF_HUB_OFFLINE=1`。
因此挂载的是 **hub 目录 -> /models/huggingface/hub**，模型缺失时需先准备缓存。

## API 契约

| 接口 | 用途 |
| --- | --- |
| GET /health | 返回 `{"status":"ok"}`，表示应用能响应；不会触发模型加载或检查全部资源 |
| POST /query | 接收 `question`，执行 TinyStories Agent，返回四字段结果 |

请求：

```json
{
  "question": "Who found a needle in her room and wanted her mother to sew a button on her shirt?"
}
```

结果顶层包含：

| 字段 | 含义 |
| --- | --- |
| status | completed / model_error / repeated_tool_call / max_steps_reached |
| answer | 最终文本；completed 表示取得合法文本，不自动证明答案正确 |
| trace | 本次消息历史；工具 observation 是 role=tool 的 content 中的 JSON 字符串 |
| error | 无任务级错误时为 null，否则为错误描述 |

question 会去掉首尾空白。缺字段、空字符串与纯空白返回 HTTP 422，进入 Agent 前终止。
得到 AgentResult 时 HTTP 返回 200；调用方仍需检查业务 status，包括 model_error。
模型调用中的 ValueError、OSError、RuntimeError 进入该结果；其他未处理的程序错误仍可能返回 500。
日志编号和耗时保留在接口层，不加入 AgentResult，也不会自动把全部检索结果当作答案引用。

## 实验与证据

历史纯检索对照使用同一组 40 道可回答题（另排除 5 道不可回答题），结果如下：

| 指标 | 无重排 | 有重排 |
| --- | ---: | ---: |
| HitRate@5 | 27/40 | 38/40 |
| MRR@20 | 0.5844 | 0.9250 |

来源：[原始 summary](data/evaluation/stage2/20261012-111210-861047-retrieval-v1/summary.json)。
这些是旧分段、固定题集的检索指标，不是当前服务的回答准确率。

新分段 Agent 评估与阶段三固定证据 A/B 回放另有独立目录：

- [阶段二协议](docs/stage2-evaluation-protocol.md)：指标口径、资产与运行记录要求。
- [Agent 人工复核](docs/stage2-agent-review.md)：答案、证据、引用与拒答的分别判定。
- [阶段三回放复核](data/evaluation/stage3/20261018-103123-691887-answer-replay-v1/review.md)：
  A/B 各 12 条固定证据请求。原消息、工具结果和模型设置保持一致，B 只增加末尾回答约束。
  当前没有采用这条通用后置指令；复核仍部分待确认，不发布最终整组严格通过率。

12 道 Agent 开发题被反复用于调试，不能称为独立测试集。文段命中、completed 和引用 ID 存在
都不能替代对答案和原文支持关系的人工检查。

运行入口：

```powershell
# 仅校验配置、题集与资产绑定，不加载模型或新建实验目录
python scripts/eval_agent.py --config configs/chunking_v2.yaml --check-only
python scripts/eval_retrieval.py --config configs/chunking_v2.yaml --check-only

# 实际运行会加载模型并创建新的实验记录
python scripts/eval_agent.py --config configs/chunking_v2.yaml
python scripts/eval_retrieval.py --config configs/chunking_v2.yaml
python scripts/replay_answers.py
```

Agent 评估按配置选择是否重排；纯检索入口固定比较无重排和有重排两组，需额外缓存重排模型。
回放脚本当前固定父运行和 12 道开发题，不是通用评测服务。需要保存新结果，不能覆盖旧运行。

## 开发检查与代码入口

安装开发依赖：

```powershell
python -m pip install -c constraints/runtime-py311.txt -e ".[service,dev]"
```

无模型生成检查可排除两个真实模型测试：

```powershell
python -m pytest --ignore=tests/test_generator.py -k "not test_local_model_emits_calculator_tool_call" -q -p no:cacheprovider
```

完整 `python -m pytest` 包含真实模型测试，需要相应缓存和内存。本轮没有重跑全套质量实验或全部测试；
实际执行范围见服务验收记录，历史测试数量不相加作为当前总数。

| 文件 | 职责 |
| --- | --- |
| src/rag_agent_system/api.py | 生命周期、HTTP 校验、锁和请求日志 |
| src/rag_agent_system/agents/factory.py | 服务与通用 CLI 复用的 Agent 装配 |
| src/rag_agent_system/agents/loop.py | 手写工具循环、结果检查和终止保护 |
| src/rag_agent_system/agents/llm_client.py | 本地 Qwen 的聊天与工具调用适配 |
| src/rag_agent_system/agents/prompts.py | TinyStories Agent 问答提示 |
| src/rag_agent_system/tools/ | 工具 schema、校验、执行与 observation |
| src/rag_agent_system/retrieval/ | FAISS 检索与 CrossEncoder 重排 |
| scripts/run_agent.py | 计算、时间、检索等真实 Agent 演示 |
| scripts/eval_*.py / replay_answers.py | 分层评估和固定证据对照 |

```powershell
python scripts/run_agent.py --config configs/chunking_v2.yaml --scenario calculator
```

早期固定 RAGPipeline 与 CLI 仍保留，历史学习记录见 [docs/learning-log](docs/learning-log/)。

## 局限与项目边界

- 使用 TinyStories 与较小的固定开发题集，尚不能推出企业知识库或未见问题的泛化表现。
- 检索正确后仍可能幻觉、错误拒答或漏引用；当前没有程序化保证整句引用成立。
- 单进程内加锁串行推理，尚未验证负载、排队上限、请求取消或多 worker 部署。
- health 是存活检查；缺模型或索引可能到首次问答才暴露。尚未设置完整输入 token 预算。
- 工具线程超时不保证正在执行的函数停止，不能视为硬隔离。
- 模型缓存 main 分支、基础镜像标签和传递依赖未完全固定，不宣称逐位复现。

本轮完成最小服务与容器演示范围。后续扩展应由实际需求决定，保留失败案例和验证口径。
