# Day21 阶段一：问题集与标注说明

这是数据准备交付，不是实验报告。没有运行 Day21 检索或生成实验，也没有建立训练／开发／测试划分。

## 交付文件

| 文件 | 实际内容 |
|---|---|
| tinystories_queries.jsonl | 40 条 Day20 已复核题，以及 5 条助手检查后用户确认复核的无答案题 |
| tinystories_annotation_review.md | 逐题参考答案、证据、标注状态；新增题的故事全文 |
| tinystories_absence_evidence.json | 新增题的完整故事、关键词检查候选、缺失信息判断和限制 |
| tinystories_benchmark_manifest.json | 数据版本、实际来源内容哈希、标注来源、数量及限制 |
| tinystories_labeling_guide.md | 本说明 |

文件结构参考 evaluation 的问题和标注文件。config.json、per_query.json、total.csv 属于后续实验记录，不在本次数据交付中。

## 标注状态与来源

- q001–q040：annotation_status=reviewed，依据是 Day20 学习记录中用户已复核和修正问题的记载。原文件的状态保存在 source_annotation_status，review_provenance 记录来源。不是本次新增的人工复核。
- q041–q045：annotation_status=reviewed。助手已阅读恢复的指定故事全文和全库关键词匹配片段；用户于 2026-10-05 在本次对话确认复核完毕。分别保留 assistant_review_provenance 和用户确认来源。未测量多标注者一致性。
- 每条 split=unsplit。没有用 chunk ID 假定完整故事分组；paired_with 仅记录新增问题与原题的改写关系，不能视为整个数据集的故事分组已经完成。

## 保留和修正

40 条已有题目的 query、expected_answer、relevant_chunk_ids、evidence 保持 Day20 修正版内容。q005 的错误字段名 ,category 仅在副本中修正为 category。q038 保留限定猫直接向另一只动物求助的问法。

本次再次核验原有 evidence.quote 是否逐字存在于对应 chunk，并阅读 gold chunk 检查参考答案支持。检查已标注正例不意味着相关片段列表完备，也不替代用户或独立标注者的新一轮复核。

## 可回答题

answerable=true，相关 ID 非空。多个相关 ID 表示多个预期能独立支持答案的片段；本数据集没有专门标注必须联合多个 chunk 才能回答的问题。

参考答案是标注，不是模型输出。允许同义表述，评分要检查关键事实和证据；不能用答案字符串精确匹配判断所有回答，也不能只凭相关 ID 命中就判断生成正确。若发现漏标或不足以支持答案的正例，更新数据版本并记录修改。

## 无答案题

answerable=false、relevant_chunk_ids=[]、evidence=[]。absence_evidence 指向指定故事全文和判断依据，不把“没有匹配到某个关键词”当成全库没有答案的证明。

题目限定具体故事，询问该故事未给出的制造商／型号、药品名称／剂量、大学地址或黏土克数。标注预期是说明信息不足，不编造所问细节。其他故事中的相同人物名、药物或数字不能回答所限定的故事。

故事全文由相邻重叠 chunk 的相同字符去重恢复。全库关键词筛选有检索限制，因此判断范围明确限定于所指故事。新增五题均为控制题，不宣称代表真实无答案用户请求。

## 使用边界

模型输入只能包含问题和正常检索得到的 Context，不向模型暴露答案、answerable、证据标注或缺失信息判断。

若沿用 Day20 检索指标函数，只统计可回答题；空 gold 不传给 Recall/MRR。五条新题已获用户复核确认，可以纳入拒答评估；报告时仍应说明这些题目的故事范围及其控制题性质。

数据来源于已知答案片段，规模小，没有独立保留测试集，不代表真实流量。重新切分语料后需迁移、复核相关 ID；当前未验证 chunk size/overlap。实际实验配置、运行输出和结果只能在实验时据实生成。
