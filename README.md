# RAG Agent System

基于本地 Qwen 的 RAG Agent，API 支持选择 TinyStories 或 SEC。手写工具调用循环，结合三种检索模式、可选
CrossEncoder 重排、固定证据回答回放，以及 FastAPI / Docker 最小服务。

项目关注检索证据、模型回答和引用之间的关系，并保留可检查的请求、工具结果和实验记录。
当前提供本地与单进程容器演示；问答仍存在幻觉、错误拒答和引用遗漏，不作为生产可靠性证明。

SEC 迁移：六份报告的目标章节已生成 3091 个统一 chunk，完成
MiniLM embedding 与 384 维 IndexFlatIP 的保存、重载和现有检索器兼容验收。
API 已按 dataset 选择配置、Agent prompt 和搜索 schema，并按数据集缓存 Agent；
该接线通过替代组件的 HTTP 验收；真实 TinyStories 问答取得正确答案与引用，SEC 问答仍有引用遗漏。
检索评测入口支持动态题数、模式配置及可选重排，
不可回答证据范围已通用化；SEC benchmark 经用户复核确认后冻结为 reviewed 版本：
开发集 30 题、测试集 10 题。三种检索模式在开发集、测试集上的重排前后对照均已完成，
SEC_v1.yaml 当前绑定测试集。公司/财年硬过滤尚未实现，候选仍可能混入其他报告年份。
最终指标及局限见 [检索实验报告](docs/retrieval-experiments.md)，原始记录见
[实验索引](data/evaluation/README.md)，资产与复现入口见 [SEC 数据说明](data/sec/README.md)。

## 复现路线

以下命令均在仓库根目录的 PowerShell 中执行，使用 Python 3.11。

| 步骤 | 入口 | 完成标准 |
| --- | --- | --- |
| 1. 安装环境 | [本机安装与模型准备](#本机安装与模型准备) | 安装项目、服务依赖及所需模型缓存 |
| 2. 准备数据 | [资源与配置](#资源与配置) | 所选 YAML 的 Chunks、索引和 Benchmark 属于同一版本 |
| 3. 预检与评测 | [复现检索实验](#复现检索实验) | 预检通过；正式运行生成 complete 状态和逐题结果 |
| 4. 运行问答 | [启动本地服务](#启动本地服务) / [API 契约](#api-契约) | 能按 dataset 选择资料库，检查答案与实际引用 |

先复现 TinyStories 可使用已跟踪的历史数据 bundle。SEC 原始 HTML、章节、Chunks 和索引未随 Git 分发，
需要准备对应本地资产或重建，单独克隆仓库不能直接复现 SEC 历史成绩。
只运行检索评测不需要 Qwen；Dense 需要 MiniLM，重排需要 CrossEncoder，Agent 问答还需要 Qwen。

## 当前能力与架构

```text
POST /query: question + dataset（默认 tinystories）
    -> 校验输入、选择对应数据集的 YAML 与 Agent 提示词
    -> 取得进程内锁、创建或复用该数据集的 Agent
    -> 本地 Qwen 生成工具调用
    -> Registry 校验参数并执行工具
       search_documents -> Dense / BM25 / Hybrid -> 可选 CrossEncoder -> 原文片段
       calculator / time -> 计算或时间结果
    -> observation 写回消息历史 -> Qwen 继续回答
    -> status / answer / trace / error
```

- Agent 支持工具调用、observation 回传、重复调用与最大步数终止保护。
- 工具参数由手写 schema 与校验器检查，工具失败保留为结构化 observation。
- 检索资产使用故事边界和 token 窗口切分，业务 chunk_id 与 FAISS ID 映射分开管理。
- 评估区分证据命中、答案正确、引用支持与不可回答题拒答，记录资产指纹。
- FastAPI 启动时初始化 Agent 缓存；首次请求某个数据集时创建其 Agent，模型与检索资源按需加载。
- 服务串行执行 Agent，请求日志记录随机 request_id、dataset、任务状态及含排队时间的耗时。

`/query` 接受 TinyStories 或 SEC 的资料库问答。计算、时间及多工具的通用 Agent 演示使用 CLI 场景入口。

## 已验证的范围

已完成 Windows 本地服务与 Linux CPU 容器的代表性问答验收。
容器使用 Python 3.11.17、PyTorch 2.11.0+cpu，端口为宿主机 8001 -> 容器 8000。
Lily / needle 问题返回正确人物和支持引用 `story_000000_chunk_000`。
健康检查及缺字段、空字符串、纯空白输入检查通过。

资源只读挂载、并发串行保护、模型异常后的恢复及验证局限见
[服务验收记录](docs/service-acceptance-2026-10-19.md)。
这次验收是一条真实容器问答及关键服务行为检查，不是重新运行整个质量基准。

## 资源与配置

API 按 dataset 选择配置；命令行评测应显式传入 `--config`：

| 资料库 | 配置 | 当前 Benchmark | 计分 / 排除 |
| --- | --- | --- | --- |
| TinyStories | [configs/chunking_v2.yaml](configs/chunking_v2.yaml) | 已复核、未独立拆分的题集 | 40 / 5 |
| SEC | [configs/SEC_v1.yaml](configs/SEC_v1.yaml) | 冻结 test（当前工作配置） | 8 / 2 |

服务问答使用索引和 Chunks；Benchmark 题集用于评测，不是运行 `/query` 的输入。

| 项目 | 配置与约束 |
| --- | --- |
| 生成模型 | Qwen/Qwen2.5-1.5B-Instruct |
| 生成设置 | max_new_tokens=256，客户端 do_sample=False |
| Embedding | sentence-transformers/all-MiniLM-L6-v2 |
| 索引 | IndexFlatIP，384 维 |
| 检索模式 | YAML 的 `retrieval.mode`：dense / bm25 / hybrid |
| 重排 | YAML 的 `reranker.enabled`；工作配置会随实验变更，复现时显式固定 |
| TinyStories 数据 | `data/chunking_v2/20261013-141109-775427-qwen128-overlap32-story-boundaries/` |
| SEC Chunks | `data/sec/chunking_v1/20261021-minilm200-overlap32-v1/chunks.json` |
| SEC 索引 | `data/sec/indexes/20261022-minilm-flatip-v1/sec.faiss` |
| SEC Benchmark | `data/sec/benchmark/20261022-sec-v1-reviewed/` 的 dev/test 三件套 |

这个 bundle 在迁移核验中包含 5092 篇保留故事和 11303 个文段。完整历史 bundle 已被 Git
跟踪；请确认所选配置对应的索引、chunks、题集和 manifest 同时存在，勿混用旧版资产。
模型权重不在仓库和镜像中。数据保留边界见 [data/README.md](data/README.md)。

SEC 复现可恢复已有匹配 bundle，或从六份本地 HTML 依次运行 `scripts/build_sec_sections.py`、
`scripts/build_sec_chunks.py`、`scripts/build_sec_index.py`。每个构建入口要求新的输出目录，
参数、模型 snapshot、原始文件列表和构建校验见 [SEC 数据说明](data/sec/README.md)。
本项目的 HTML hash 绑定浏览器保存的快照，重新从相同 URL 下载不保证字节一致。
重建结果只有通过冻结 Benchmark 的资产 hash 校验，才能用于复现该版本成绩；
新字节版本应建立新资产及 Benchmark 绑定，不修改冻结 manifest 来绕过校验。

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
python -c "from huggingface_hub import snapshot_download; snapshot_download('Qwen/Qwen2.5-1.5B-Instruct', allow_patterns=['*.json','*.safetensors','*.txt','*.model']); snapshot_download('sentence-transformers/all-MiniLM-L6-v2', revision='1110a243fdf4706b3f48f1d95db1a4f5529b4d41', allow_patterns=['*.json','*.safetensors','*.txt','*.model']); snapshot_download('cross-encoder/ms-marco-MiniLM-L6-v2', allow_patterns=['*.json','*.safetensors','*.txt','*.model'])"
```

这是基于官方 [snapshot_download / 文件过滤接口](https://huggingface.co/docs/huggingface_hub/guides/download)
提供的资源准备方式。本轮验证使用已有缓存，没有重复验证空缓存下载。
默认 Hub 缓存位于 `$env:USERPROFILE\.cache\huggingface\hub`；自定义 HF_HOME / HF_HUB_CACHE
时，运行容器的 source 应改为实际缓存目录。
上面的命令包含重排模型；关闭重排时可以省略它，纯检索评测也可以省略 Qwen。
MiniLM 的 revision 与 SEC 索引构建清单一致；Qwen 和 CrossEncoder 仍读取 main 分支。
加载器目前使用模型名称，不强制指定缓存 revision；有多个缓存版本时需核对实际使用的版本。
历史缓存观测与复现局限见 [服务验收记录](docs/service-acceptance-2026-10-19.md)。

## 启动本地服务

启动本地开发服务：

```powershell
python -m uvicorn rag_agent_system.api:app --app-dir src --host 127.0.0.1 --port 8000
```

本地调试入口：[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)。
服务按数据集缓存 Agent，修改 YAML 或提示词后重启此进程。第一次问答会加载模型；
`/health` 成功只表示应用可响应，不证明模型、索引和答案质量都已通过检查。

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
| POST /query | 接收 `question` 与可选 `dataset`，执行所选 Agent，返回四字段结果 |

请求：

```json
{
  "question": "Who found a needle in her room and wanted her mother to sew a button on her shirt?",
  "dataset": "tinystories"
}
```

`dataset` 支持 `tinystories`（默认）与 `sec`，分别使用 `configs/chunking_v2.yaml`
和 `configs/SEC_v1.yaml`。同一个选择同时决定 Agent 提示词与搜索工具描述；
每个数据集首次构建成功后缓存 Agent，后续请求复用。修改对应 YAML 后重启服务使其生效。

SEC 请求示例：

```json
{
  "question": "What were Microsoft's research and development expenses in FY2025?",
  "dataset": "sec"
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
不支持的 dataset 返回 HTTP 422；创建 Agent 失败时不缓存失败结果，后续请求可重新尝试。
得到 AgentResult 时 HTTP 返回 200；调用方仍需检查业务 status，包括 model_error。
模型调用中的 ValueError、OSError、RuntimeError 进入该结果；其他未处理的程序错误仍可能返回 500。
日志编号和耗时保留在接口层，不加入 AgentResult，也不会自动把全部检索结果当作答案引用。
共享 search_documents 工具的每条结果包含原 chunk 的 metadata，用于报告、财年和来源追溯；
不同数据集的 metadata 字段可以不同，工具不会补造缺失信息。

## 复现检索实验

### 先做资产预检

```powershell
python scripts/eval_retrieval.py --config configs/chunking_v2.yaml --check-only --candidate-top-k 20
python scripts/eval_retrieval.py --config configs/SEC_v1.yaml --check-only --candidate-top-k 20
```

预检不加载模型、不新建运行目录。检查 `benchmark_version`、`queries_path`、`retrieval_mode`、
`reranker_enabled`、`candidate_top_k`：SEC test 应为 10 题、计分 8、排除 2；dev 为 30 / 24 / 6。
缺文件或 hash 不匹配时先处理数据版本，不进入模型推理。

### 固定三种方法与重排协议

以下命令从冻结时的配置快照生成本地复现配置，避免当前工作 YAML 的模式或开关影响对比。
只写入被 Git 忽略的 `data/local/reproduce-sec/`，不修改冻结题集和原始实验结果。

```powershell
@'
from copy import deepcopy
from pathlib import Path
import yaml

bundle = Path("data/sec/benchmark/20261022-sec-v1-reviewed")
base = yaml.safe_load((bundle / "evaluation_config.yaml").read_text(encoding="utf-8"))
for split in ("dev", "test"):
    output = Path("data/local/reproduce-sec") / split
    output.mkdir(parents=True, exist_ok=True)
    for mode in ("dense", "bm25", "hybrid"):
        config = deepcopy(base)
        for key, name in (
            ("benchmark_queries", "queries.jsonl"),
            ("benchmark_manifest", "manifest.json"),
            ("absence_evidence", "absence_evidence.json"),
        ):
            config["paths"][key] = (bundle / f"{split}_{name}").as_posix()
        config["retrieval"]["mode"] = mode
        config["reranker"]["enabled"] = True
        (output / f"{mode}.yaml").write_text(
            yaml.safe_dump(config, sort_keys=False, allow_unicode=True), encoding="utf-8"
        )
'@ | python -
```

先检查并运行开发集。例如 Dense，或批量运行三个开发配置：

```powershell
python scripts/eval_retrieval.py --config data/local/reproduce-sec/dev/dense.yaml --check-only --candidate-top-k 20

Get-ChildItem data/local/reproduce-sec/dev/*.yaml | ForEach-Object {
    python scripts/eval_retrieval.py --config $_.FullName --candidate-top-k 20
    if ($LASTEXITCODE -ne 0) { throw "Evaluation failed: $($_.FullName)" }
}
```

每次开启重排的运行同时输出 `Without Rerank` 与 `With Rerank`，因此三次运行即得到六组结果。
纯检索评测由 `--candidate-top-k 20` 指定候选数，并对这 20 条候选完整重排；
YAML 中的 `retrieval.top_k=50`、`reranker.top_k=5` 和 `context.top_k=5` 用于应用链路，
不替代本次离线评测预算。Hybrid 两路各取 20、融合后取 20，其计算成本高于单路检索。

方案固定后，测试集命令使用同目录下的 test 配置，例如：

```powershell
python scripts/eval_retrieval.py --config data/local/reproduce-sec/test/dense.yaml --candidate-top-k 20
```

历史测试集三种方法的六组结果已完成并保留，当前收尾无需再次运行。
以上命令供复核和他人复现使用；不根据测试成绩继续修改参数或标注。
TinyStories 的三方法对照使用 `configs/chunking_v2.yaml` 的资产路径，
同样依次设置三种 mode、开启 reranker 并显式指定候选数 20；其题集没有独立测试拆分。

### 判断运行是否完成

- SEC 输出到 `data/evaluation/sec/dev/` 或 `sec/test/`；TinyStories 输出到 `data/evaluation/tinystories/retrieval/`。
- `config.json` 保存方法、预算和资产 hash；`per_query.json` 保存逐题排名与指标。
- `summary.json` 和 `total.csv` 是汇总；只有 `run_status.json` 的 status 为 `complete` 才是完整运行。
- 失败时保留 `failure.json` 和已完成题目的检查点，重跑创建新目录；`--run-dir` 可指定尚不存在的目录。
- 不可回答题记录在 `excluded_queries.json`，不参与 Recall、HitRate 和 MRR，也没有因此完成拒答评测。

当前工作配置可以编辑，复现实验以每次保存的 config、资产指纹和代码版本为准。
本项目未完整锁定模型加载 revision、传递依赖与历史检索实现 hash，不能保证不同环境得到逐位一致的结果。
已有成绩与原始记录分别见 [检索实验报告](docs/retrieval-experiments.md) 和 [实验索引](data/evaluation/README.md)。

## 实验与证据

SEC 开发集上 Dense + CrossEncoder 的 HitRate@5 为 17/24；独立题目测试集上为 7/8，
与 Dense 的 7/8 相同，且 MRR 从 Dense 的 0.5729 降为 0.5188。重排收益未稳定延续到测试集。
测试集仅 8 道计分题，这些指标衡量标注证据检索，不能写成问答准确率。

历史纯检索对照使用同一组 40 道可回答题（另排除 5 道不可回答题），结果如下：

| 指标 | 无重排 | 有重排 |
| --- | ---: | ---: |
| HitRate@5 | 27/40 | 38/40 |
| MRR@20 | 0.5844 | 0.9250 |

来源：[原始 summary](data/archive/evaluation/historical/stage2/20261012-111210-861047-retrieval-v1/summary.json)。
这些是旧分段、固定题集的检索指标，不是当前服务的回答准确率。

新分段 Agent 评估与阶段三固定证据 A/B 回放另有独立目录：

- [阶段二协议](docs/stage2-evaluation-protocol.md)：指标口径、资产与运行记录要求。
- [Agent 人工复核](docs/stage2-agent-review.md)：答案、证据、引用与拒答的分别判定。
- [阶段三回放复核](data/evaluation/tinystories/answer_replay/20261018-103123-691887-answer-replay-v1/review.md)：
  A/B 各 12 条固定证据请求。原消息、工具结果和模型设置保持一致，B 只增加末尾回答约束。
  当前没有采用这条通用后置指令；复核仍部分待确认，不发布最终整组严格通过率。

12 道 Agent 开发题被反复用于调试，不能称为独立测试集。文段命中、completed 和引用 ID 存在
都不能替代对答案和原文支持关系的人工检查。

Agent 与固定证据回放的独立入口：

```powershell
# 仅校验配置、题集与资产绑定，不加载模型或新建实验目录
python scripts/eval_agent.py --config configs/chunking_v2.yaml --check-only

# 实际运行会加载模型并创建新的实验记录
python scripts/eval_agent.py --config configs/chunking_v2.yaml
python scripts/replay_answers.py
```

Agent 评估按配置选择是否重排；纯检索入口关闭重排时只输出 baseline，开启时同时输出两组结果。
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
| src/rag_agent_system/agents/prompts.py | TinyStories / SEC Agent 问答提示选择 |
| src/rag_agent_system/tools/ | 工具 schema、校验、执行与 observation |
| src/rag_agent_system/retrieval/ | FAISS 检索与 CrossEncoder 重排 |
| scripts/run_agent.py | 计算、时间、检索等真实 Agent 演示 |
| scripts/eval_*.py / replay_answers.py | 分层评估和固定证据对照 |

```powershell
python scripts/run_agent.py --config configs/chunking_v2.yaml --scenario calculator
```

早期固定 RAGPipeline 与 CLI 仍保留，历史学习记录见 [docs/learning-log](docs/learning-log/)。

## 局限与项目边界

- SEC 仅 6 份报告的三个目标章节，独立测试集仅 8 道可回答题；TinyStories 没有独立测试拆分，不能推出广泛泛化表现。
- 检索正确后仍可能幻觉、错误拒答或漏引用；当前没有程序化保证整句引用成立。
- 单进程内加锁串行推理，尚未验证负载、排队上限、请求取消或多 worker 部署。
- health 是存活检查；缺模型或索引可能到首次问答才暴露。尚未设置完整输入 token 预算。
- 工具线程超时不保证正在执行的函数停止，不能视为硬隔离。
- 模型缓存 main 分支、基础镜像标签和传递依赖未完全固定，不宣称逐位复现。

本轮完成最小服务与容器演示范围。后续扩展应由实际需求决定，保留失败案例和验证口径。
