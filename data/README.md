# 数据与实验资产保留规则

安装、资源准备、服务启动与评测命令统一见 [根目录 README 的复现路线](../README.md#复现路线)。

API 按 dataset 分别使用 `configs/chunking_v2.yaml` 和 `configs/SEC_v1.yaml`。
两套原始数据、Chunks、索引和冻结 Benchmark 保持原位；不要跨版本混用。

## 实验记录入口（2026-10-28 整理）

- [正式实验索引](evaluation/README.md)：SEC dev/test、TinyStories 检索，以及代表性 Agent/回答回放。
- [检索实验报告](../docs/retrieval-experiments.md)：最终指标、失败分析与评测局限。
- `archive/evaluation/`：重复运行、早期实验和失败记录，保留用于追溯。
- [迁移清单](evaluation/organization-20261028.json)：49 项原路径与新路径、303 个文件的 SHA256。

每种检索模式保留一份开启重排的完整运行，其中同时包含重排前后两组排名和指标。
独立的未重排重复运行移入归档，先核对它与保留记录的基础排名一致。
此次只移动文件，没有删除实验记录或改写历史 JSON；配置快照中的旧绝对路径保留为原始来源，
查找迁移后的记录使用清单。移动前后逐文件 hash 相同，Git 提交与推送由用户完成。

新检索运行按 `evaluation/sec/dev/`、`evaluation/sec/test/` 或
`evaluation/tinystories/retrieval/` 输出；Agent 运行按数据集放入 `agent/`。
未识别为 SEC 的 benchmark 按历史 TinyStories 路径组织，新增数据集时需扩展路由。
临时诊断输出放在被 Git 忽略的 `data/local/diagnostics/`。

## 保留的项目证据

- benchmark 题集、标注说明、absence evidence 和人工复核。
- 构建与 benchmark manifest、资产指纹、迁移说明。
- 用于结论的实验配置、请求、逐题结果与复核记录。
- 已经进入 Git 的历史 bundle，包括其中的索引、文段和源故事。
  本次收尾保留其文件与跟踪状态，保证历史实验仍能对应到原始资产。

## 新生成的本地文件

`.gitignore` 会忽略嵌套目录中新生成的 FAISS 索引、chunks、源故事副本、
NumPy/Parquet 文件与临时备份。题集、manifest 和实验 JSON/Markdown 不做整体忽略。
新实验记录仍需检查用途、体积和内容后再由用户选择提交。

- `data/raw/`：本地原始输入。
- `data/local/`：本地草稿与临时结果。
- `data/runtime/`：运行时生成数据。

忽略规则不会让已跟踪文件自动退出 Git。本次没有移除文件、修改历史快照或重写 Git 历史。
需要重建资产时应使用真实输入与现有构建入口，不能编造索引或文段。

## 容器资源

`.dockerignore` 排除整个 `data/`，模型缓存也不进入构建上下文。
后续 Docker 启动需挂载所选 bundle，并保留配置所需的相对路径；只挂载已有数据，
不会因为镜像里缺少文件就生成替代资产。2026-10-19 已完成 Linux CPU 容器的只读挂载与
真实问答验收，见 [服务验收记录](../docs/service-acceptance-2026-10-19.md)。

