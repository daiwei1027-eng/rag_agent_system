# 数据与实验资产保留规则

当前服务使用 `configs/chunking_v2.yaml` 指向的 story-boundaries bundle。
不要把顶层旧索引与这个 bundle 的文段、题集或 manifest 混用。

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

