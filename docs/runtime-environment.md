# 依赖与运行环境

## 文件分工

- `pyproject.toml`：项目直接依赖及 `service`、`dev` 两组额外依赖的唯一声明入口。
- `constraints/runtime-py311.txt`：已观察到的九项直接运行依赖版本，供 pip 解析时约束使用。
- `requirements.txt`：引用上述约束并以 editable 方式安装 `.[service]`，不维护另一套依赖清单。
- `.gitignore`：本地缓存、环境、运行日志和新生成的大型数据文件规则。
- `.dockerignore`：将数据、模型、Git 历史和开发材料排除出 Docker 构建上下文。
- `data/README.md`：benchmark、manifest、实验证据与历史 bundle 的保留边界。

## 本次记录的环境

2026-10-19 读取现有 `hf_llm` 环境的包元数据。随后离线重新安装本地项目以刷新
安装元数据，未安装、升级或降级第三方依赖：

| 项目 | 观察值 |
| --- | --- |
| 操作系统 | Windows 10，build 19045 |
| Python | 3.11.16 |
| faiss-cpu | 1.15.1 |
| NumPy | 2.4.6 |
| PyYAML | 6.0.3 |
| sentence-transformers | 6.1.0 |
| Transformers | 5.17.0 |
| PyTorch | 2.11.0+cu128 |
| FastAPI | 0.143.3 |
| Uvicorn | 0.54.0 |
| Pydantic | 2.14.1 |
| pytest | 8.4.2 |
| HTTPX | 0.28.1 |

NumPy 2.4.6 的包元数据要求 Python >=3.11，因此项目最低 Python 声明同步为 3.11。
这些是本次本地验证所使用的环境信息，不补写成旧实验运行当时的环境记录。
项目声明中的版本区间也不表示每个版本组合都已测试。

## 安装入口

从仓库根目录，在选定的 Python 3.11 环境中执行：

```powershell
python -m pip install -r requirements.txt
```

开发环境需要服务、pytest、Ruff 和 HTTPX 时，使用同一份约束：

```powershell
python -m pip install -c constraints/runtime-py311.txt -e ".[service,dev]"
```

现有服务与脚本通过源码位置查找项目根目录，当前使用 editable 安装保留这一布局。
普通 wheel 安装到 site-packages 后的资源路径尚未适配，不应当作已经验证的安装方式。

## CPU / CUDA 与复现边界

约束中的 `torch==2.11.0` 约束发布版本；按 Python 版本比较规则，现有
`2.11.0+cu128` 也满足这一约束。它不选择 CPU/CUDA wheel，也不锁定 CUDA 后缀。
全新环境需先按目标平台选定 PyTorch wheel 来源，再安装项目；本机 CUDA wheel
不能直接复制进 Linux 容器。后续 Dockerfile 使用官方 CPU wheel 源安装 2.11.0+cpu；
实际构建、依赖版本与运行结果见 [服务验收记录](service-acceptance-2026-10-19.md)。

这份约束只固定直接运行依赖，不是带哈希的完整传递依赖锁文件，也不固定模型权重。
第一步只验证本地安装声明与元数据。随后已完成 Linux CPU 镜像环境安装和已有缓存下的真实问答，
容器 Python 为 3.11.17；仍未验证从空模型缓存准备全部资源或跨机器逐位复现。

当前模型使用本地 Hugging Face 缓存；Qwen 客户端设置 `local_files_only=True`。
安装 Python 包不会自动准备模型、FAISS 索引和文段，实际运行仍需准备或挂载这些资源。
`configs/chunking_v2.yaml` 当前关闭 reranker，不将这个服务配置当作有重排实验配置。

主 README 已在容器实际验收后更新架构、运行步骤和实验摘要；原 Python 3.10、
Day 17 资源和“Agent 尚未实现”等说明已由当前状态替换。

## 第一步实际验收（2026-10-19）

- TOML 解析、Python 版本要求、九项直接运行依赖与约束对应检查通过；
  现有环境版本全部满足声明和约束。
- pip 成功解析 `requirements.txt` 的九项约束与唯一 editable 安装目标。
- 15 个 `git check-ignore --no-index` 样例通过：嵌套生成资产被忽略，
  benchmark、manifest、实验结果与 `.env.example` 保留可跟踪状态。
- 离线安装预演通过（`--dry-run --no-deps --no-build-isolation --no-index`）；
  该检查验证本地项目的 editable 打包元数据，不等于完整依赖解析或干净环境安装。
- 首次 `pip check` 仍读到旧安装元数据中的 Transformers / Sentence Transformers
  版本上限。随后执行 `pip install --no-deps --no-build-isolation --no-index --no-cache-dir -e .`，
  仅刷新本地项目的 editable 安装；再次 `pip check` 返回 `No broken requirements found.`。
  前后核对的 13 项第三方包版本全部未变。
- 151 个已跟踪 data 文件中，仅主动更新了本目录保留规则说明 `data/README.md`；
  其余 150 份数据和实验资产的合并指纹与修改前一致，Git 跟踪状态未调整。
- `.dockerignore` 已整理资源排除规则；实际构建上下文与容器运行在下一阶段验证。

第一步只整理依赖与忽略规则，未修改 Agent/API 核心实现或新建应用 Dockerfile。
后续容器构建与文档收尾另见服务验收记录；Git 提交和推送仍由用户完成。
