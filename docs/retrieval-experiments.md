# 检索实验结果与局限

结果整理于 2026-10-28。完整配置、题集快照、逐题排名及指标见 [实验索引](../data/evaluation/README.md)。

## 评测条件

SEC：6 份申报文件的 Item 1、1A、7，共 3091 个 chunk；dev 为 24 道可回答题 + 6 道不可回答题，test 为 8 + 2。开发集与测试集按问题及事实组隔离，共用同一语料；不属于跨公司或新文档泛化测试。TinyStories 共 11303 个 chunk，使用同一份 40 道可回答题 + 5 道不可回答题，没有独立测试集。

Dense 使用 all-MiniLM-L6-v2 与归一化 IndexFlatIP；BM25 使用小写后按空白分词，k1=1.5、b=0.75；Hybrid 使用等权 RRF，c=60，两路各取 20、融合后取 20。可选 CrossEncoder 为 ms-marco-MiniLM-L6-v2，对全部 20 条候选重排。Hybrid 的计算预算高于单路检索。算法参数来自当前实现；旧运行未单独记录实现文件 hash，不能声称完整复现了未记录的历史代码版本。

不可回答题不参与下面的检索指标。HitRate@5 是前五至少命中一个标注证据的题目比例；Recall@5 是逐题相关 chunk 召回比例的平均；MRR@20 使用第一个标注证据的倒数排名。以上均不代表答案正确率、引用正确率、拒答能力或多证据完整覆盖。

## SEC 开发集

| 方法 | Recall@5 | HitRate@5 | MRR@20 |
|---|---:|---:|---:|
| dense | 43.75% | 11/24 | 0.3025 |
| dense + CrossEncoder | 63.89% | 17/24 | 0.5569 |
| bm25 | 35.42% | 9/24 | 0.2563 |
| bm25 + CrossEncoder | 41.67% | 11/24 | 0.3931 |
| hybrid | 43.75% | 12/24 | 0.3480 |
| hybrid + CrossEncoder | 61.81% | 16/24 | 0.4858 |

## SEC 测试集

| 方法 | Recall@5 | HitRate@5 | MRR@20 |
|---|---:|---:|---:|
| dense | 81.25% | 7/8 | 0.5729 |
| dense + CrossEncoder | 81.25% | 7/8 | 0.5188 |
| bm25 | 56.25% | 5/8 | 0.4513 |
| bm25 + CrossEncoder | 50.00% | 4/8 | 0.4710 |
| hybrid | 68.75% | 6/8 | 0.5595 |
| hybrid + CrossEncoder | 56.25% | 5/8 | 0.5074 |

## TinyStories 已用题集

| 方法 | Recall@5 | HitRate@5 | MRR@20 |
|---|---:|---:|---:|
| dense | 81.25% | 33/40 | 0.6510 |
| dense + CrossEncoder | 93.75% | 38/40 | 0.9375 |
| bm25 | 86.25% | 35/40 | 0.8050 |
| bm25 + CrossEncoder | 97.50% | 39/40 | 0.9750 |
| hybrid | 96.25% | 39/40 | 0.8654 |
| hybrid + CrossEncoder | 100.00% | 40/40 | 0.9875 |

## 结论与代表性失败

开发集上 Dense + CrossEncoder 的 HitRate@5 为 17/24，高于 Dense 的 11/24。测试集两者均为 7/8，但重排后 MRR 从 0.5729 降为 0.5188；开发集上的重排收益未稳定延续到测试集。测试集仅 8 道计分题，一题改变 HitRate 12.5 个百分点，不作统计显著性或普遍优越性结论。保留全部预定方案的结果，不按测试表现继续调参。

- `sec_test_001`：要求微软 FY2026 销售费用及收入占比，三种检索的 Top20 都缺少标注表格，属于候选召回失败，重排无法补回。
- `sec_test_004`：NVIDIA FY2025 客户占比标注表格，Dense 第 1 → 重排第 5，Hybrid 第 1 → 第 6；Dense 重排第一条来自 FY2026。候选中也有其他章节披露相同数值，因此标注表格的排名下降不等同于最终答案必错。
- TinyStories 上 Hybrid + CrossEncoder 的 HitRate@5 达到 40/40；这是已使用题集上的检索结果，不代表未见问题或生成回答达到 100%。

仍存在公司/财年候选混入、数值表格检索困难，以及相关证据标注不穷尽等局限。真实 SEC Agent 示例出现正确列出业务分部但遗漏引用，也曾编造来源描述；该问题不由这些检索指标衡量。

## 复现入口

```powershell
python scripts/eval_retrieval.py --config configs/SEC_v1.yaml --check-only
python scripts/eval_retrieval.py --config configs/SEC_v1.yaml
```

先检查输出中的 benchmark_version、retrieval_mode、reranker_enabled 和 candidate_top_k；当前 SEC YAML 指向测试集，默认候选数为 20。重跑 dev 时一起切换 queries、manifest、absence_evidence 为相应 dev 文件。变更方法或开关须在新目录运行，不覆盖历史结果；启用重排的一次运行已经同时输出重排前后结果。这里提供复现方法，不建议为了改善当前成绩反复使用测试集。

运行快照绑定题集、Chunks、索引 hash，历史模型名称与完整参数见各自 config.json。多数运行没有记录模型 snapshot 和检索实现 hash；额外 Dense baseline 的 runtime.json 记录模型来源，但不能将它直接当作其他运行的实际环境证明。
