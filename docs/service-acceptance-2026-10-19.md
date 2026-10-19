# 最小服务与 Docker 验收：2026-10-19

## 范围与证据来源

本轮将已有本地 Agent 接入 FastAPI，再构建并运行单进程 Linux CPU 镜像。
保留现有四字段 AgentResult 与问答提示，未接入阶段三的后置回答指令。

真实问答结果来自用户在本地 `/docs` 与容器 `8001/docs` 的操作及本对话中提供的响应。
本文件记录其验收摘要，不冒充完整原始 HTTP 响应快照或正式质量基准。
容器端口、挂载、Python / 包版本由助手直接核对；健康与无效输入由助手直接请求验证。
为了避免重复加载与推理，没有再次调用真实模型重跑同一问题。

## 完成的实现

- `agents/factory.py` 提取 retriever、可选 reranker、registry、LocalLLMClient 和 Agent 装配。
  通用命令行与服务复用该装配；评估脚本保留各自的受控实验记录流程。
- FastAPI lifespan 创建共享 Agent 和进程内 Lock。
- QueryRequest 去掉 question 两端空白，拒绝缺字段、空字符串和纯空白。
- POST /query 使用已有 `build_agent_prompt()`，在锁内执行 `Agent.run()`。
- `llm.chat` 的 ValueError、OSError、RuntimeError 进入四字段 model_error 结果。
- 日志记录 request_id、Agent status 和含锁等待的耗时，接口结果仍为四字段。
- Dockerfile 安装 Linux CPU 版 PyTorch，运行单个 Uvicorn worker，无 reload。

用户亲手完成上述核心代码；助手审查并进行下面列出的检查。

## 实际检查

| 检查 | 结果与范围 |
| --- | --- |
| CLI 提取后计算场景 | 用户运行成功：calculator.multiply(12, 8) -> 96 -> completed |
| 本地 HTTP 计算场景 | 用户提供的真实响应为 completed，trace 含工具调用、结果和最终回答 |
| 本地 HTTP 检索问答 | 用户提供 Lily 正确答案与支持它的 chunk_id |
| 无效输入 | 本地与实际容器均验证 `{}`、空字符串、纯空白返回 HTTP 422 |
| 启动与串行调用 | 替身 Agent + TestClient：启动只创建一次；两个并发 HTTP 请求中最大同时执行 Agent 数为 1，结果各自对应输入 |
| 异常与恢复 | 真实 Agent + 替身 LLM：三类预期异常分别返回 model_error，锁释放，下一条请求 completed，消息历史分别保存 |
| 日志 | 替身分别返回 completed / model_error，两次编号不同，均有非负耗时，四字段响应未改变 |
| Agent Loop 回归 | 本轮修改异常分支后，`tests/test_agent_loop.py`：48 passed；有 pytest 缓存写入权限警告 |
| 依赖 | 离线 editable 打包及安装元数据刷新成功；`pip check` 通过，第三方依赖版本未调整 |
| 评估入口检查 | chunking_v2 配置下，Agent check-only 识别 12 题，检索 check-only 识别 45 题，无模型推理 |
| 容器健康检查 | 直接请求 `http://127.0.0.1:8001/health`，HTTP 200，`{"status":"ok"}` |
| 容器真实检索问答 | 用户提供 8001/docs 的 completed 响应，搜索返回 5 段，Lily 与引用正确 |

以上测试范围不相加成业务场景总数。本轮没有运行全套 pytest、整组 Agent 质量评估或负载测试。
TestClient 检查是进程内应用测试；表中另有明确列出的真实 HTTP / 容器检查。

## 容器观测

- 容器名：`rag-agent-demo`。
- 镜像标签：`rag-agent:local`。
- 此次镜像 ID：`sha256:975c82973fefb7b3e353b7b0df9097ecb184708ed4595abbca3bab058d30a3f5`。
- 用户报告镜像显示大小：1.53 GB；这是该次本机观测，不作为固定镜像大小保证。
- 宿主机绑定：`127.0.0.1:8001` -> 容器 `8000/tcp`。
- 项目 `data/` -> `/app/data`，只读。
- 本机 Hugging Face Hub 缓存 -> `/models/huggingface/hub`，只读。
- 环境：Linux、Python 3.11.17、torch 2.11.0+cpu、cuda_available=False。

| 依赖 | 容器内读取版本 |
| --- | --- |
| FastAPI | 0.143.3 |
| Uvicorn | 0.54.0 |
| Pydantic | 2.14.1 |
| Transformers | 5.17.0 |
| sentence-transformers | 6.1.0 |
| faiss-cpu | 1.15.1 |
| NumPy | 2.4.6 |
| PyYAML | 6.0.3 |

镜像来自含未提交修改的工作区。后续文档更新或重建可能改变镜像 ID，标签不固定镜像内容。

本轮读取到的宿主机缓存 refs/main：

| 模型 | 缓存 revision |
| --- | --- |
| Qwen/Qwen2.5-1.5B-Instruct | 989aa7980e4cf806f80c7fef2b1adb7bc71aa306 |
| sentence-transformers/all-MiniLM-L6-v2 | 1110a243fdf4706b3f48f1d95db1a4f5529b4d41 |

这是缓存引用的观测值，没有逐文件校验全部权重，也没有将 revision 强制写入加载配置。

## 容器问答样例

问题：Who found a needle in her room and wanted her mother to sew a button on her shirt?

用户提供的结果：

- status：completed；error：null。
- 工具：search_documents，query 为 `needle in room mother button shirt`，top_k=5，ok=true。
- 答案：The person who found a needle in her room and wanted her mother to sew a button on her shirt is Lily. (依据：chunk_id=story_000000_chunk_000)
- 工具返回的对应原文明确说明 Lily 在房间找到针，并希望妈妈用它缝衬衫纽扣，支持该回答。
- rerank_score / rerank_rank 为 null，与当前 `reranker.enabled=false` 配置一致。

这条样例通过，但不证明所有问题都能正确引用或拒答，不改变阶段三尚未完全确认的人工评分。

## 环境排错与限制

Windows 虚拟化固件已开启，但 VirtualMachinePlatform 最初处于 Disabled。
用户在管理员终端启用该功能并重启，等待 Docker Engine 启动后，docker info 出现正常 Server 信息。
没有重写启动配置，也没有重置 Docker 或清理其他容器。

当前完成了镜像环境安装与已有模型缓存下的真实问答。尚未验证空缓存下载、跨机器部署、GPU 容器、
排队上限、取消请求、多进程或服务压力；health 不验证模型和索引 readiness。
直接依赖约束不等于完整锁文件，基础镜像标签和模型 main 引用仍可变化。

本轮服务功能范围到此收尾。README 已更新运行方式和证据入口；Git 提交、推送由用户完成。
