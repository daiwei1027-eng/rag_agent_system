# SEC benchmark v1 — reviewed / frozen

冻结日期：2026-10-22。用户确认「核实完毕，可以冻结」，原文与覆盖的题号见 review_record.json。
保留上一版 20261022-sec-v1-draft 的全部文件，未修改题目、答案、证据或拆分；仅更新审核状态。
JSON 中 review_notes、draft_reason 和 review_requirement 保留起草时的检查指导，不表示仍待审核。

| Split | 总题数 | 可回答 | 不可回答 | 用途 |
| --- | ---: | ---: | ---: | --- |
| dev | 30 | 24 | 6 | 开发与调参 |
| test | 10 | 8 | 2 | 方案固定后的最终评测 |

configs/SEC_v1.yaml 仅绑定 dev。test 仅做结构及资产检查，不运行质量评测、不参与调参。
当前没有 SEC 检索或生成成绩。预检：

```powershell
python scripts/eval_retrieval.py --config configs/SEC_v1.yaml --check-only
```

两份 split manifest 绑定题集、缺失证据、3091 个 chunk、FAISS 索引及模型配置的指纹。
bundle_manifest.json 最后生成，记录本目录文件指纹和父版本；不包含自身 hash。
validation.json 记录实际结构检查，review_record.json 记录人工确认来源。
修改任何标注或绑定资产时创建新版本，保留本版本。复现还需要本地原始 HTML、chunk 和模型文件。

范围仅为六份报告抽取的 Item 1、1A、7；负例仅针对各题明确的报告片段。
这是同 corpus 的题目留出，不代表跨公司泛化；test 仅 8 个正例，报告指标时保留分母。
relevant_chunk_ids 用于现有 Recall/MRR；多证据问题完整支持需要覆盖每个 evidence_group。
不可回答题不进入 Recall/MRR，后续另做拒答评测。替代证据标注仍可能不完整。
