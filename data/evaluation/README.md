# 正式实验索引

2026-10-28 整理。每个检索目录包含重排前、重排后两组结果；无需再单独保留一份未重排运行。

| 数据 / 拆分 | 方法 | 完整运行 | 计分 / 排除 |
|---|---|---|---|
| sec/dev | dense | [20261022-103517-397721-retrieval-sec-v1-dev-reviewed](sec/dev/20261022-103517-397721-retrieval-sec-v1-dev-reviewed/summary.json) | 24 / 6 |
| sec/dev | bm25 | [20261025-110129-704775-retrieval-sec-v1-dev-reviewed](sec/dev/20261025-110129-704775-retrieval-sec-v1-dev-reviewed/summary.json) | 24 / 6 |
| sec/dev | hybrid | [20261025-111805-236329-retrieval-sec-v1-dev-reviewed](sec/dev/20261025-111805-236329-retrieval-sec-v1-dev-reviewed/summary.json) | 24 / 6 |
| sec/test | dense | [20261028-113231-108186-retrieval-sec-v1-test-reviewed](sec/test/20261028-113231-108186-retrieval-sec-v1-test-reviewed/summary.json) | 8 / 2 |
| sec/test | bm25 | [20261028-113310-841617-retrieval-sec-v1-test-reviewed](sec/test/20261028-113310-841617-retrieval-sec-v1-test-reviewed/summary.json) | 8 / 2 |
| sec/test | hybrid | [20261028-113054-992043-retrieval-sec-v1-test-reviewed](sec/test/20261028-113054-992043-retrieval-sec-v1-test-reviewed/summary.json) | 8 / 2 |
| tinystories/retrieval | dense | [20261025-112241-178645-retrieval-stage2-story-boundaries-qwen128-overlap32-v2-reviewed](tinystories/retrieval/20261025-112241-178645-retrieval-stage2-story-boundaries-qwen128-overlap32-v2-reviewed/summary.json) | 40 / 5 |
| tinystories/retrieval | bm25 | [20261025-112407-133712-retrieval-stage2-story-boundaries-qwen128-overlap32-v2-reviewed](tinystories/retrieval/20261025-112407-133712-retrieval-stage2-story-boundaries-qwen128-overlap32-v2-reviewed/summary.json) | 40 / 5 |
| tinystories/retrieval | hybrid | [20261025-112206-368845-retrieval-stage2-story-boundaries-qwen128-overlap32-v2-reviewed](tinystories/retrieval/20261025-112206-368845-retrieval-stage2-story-boundaries-qwen128-overlap32-v2-reviewed/summary.json) | 40 / 5 |

## Agent 与回答回放

`tinystories/agent/` 保留当前切分的两组 Agent 对照；`tinystories/answer_replay/` 保留固定证据的回答回放及人工复核状态。回放尚无全部语义评分的人工确认，不将其计为总体质量收益。

## 归档与追溯

- [迁移清单](organization-20261028.json)：原路径 → 新路径以及逐文件 hash。
- `../archive/evaluation/duplicates/`：9 份未重排重复记录，已与保留运行逐题核对基础排名及资产 hash。
- `../archive/evaluation/historical/`：早期 Agent、提示词、切分和候选数量实验。
- `../archive/evaluation/failed/`：未完成的 TinyStories 运行与错误信息。
- `../archive/evaluation/reference/`：额外 Dense baseline，包含模型来源记录。

历史 JSON 中的路径是运行时快照，未随搬迁改写。查看旧路径请使用迁移清单。原始数据、Chunks、索引与冻结 Benchmark 均未移动。

新输出自动按数据集/拆分归类，历史 benchmark 版本不以 `sec-` 开头时按 TinyStories 目录处理；`--run-dir` 仍可显式覆盖。
