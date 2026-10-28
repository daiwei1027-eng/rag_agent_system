# 阶段二 Agent 两组人工判定（已确认）

整理日期：2026-10-13（Asia/Shanghai）。实验日期：2026-10-12。状态：**24 条判定均已由用户确认，最终评分固定。**

原始运行文件不修改。有重排组 q003、q041 经用户复核判为不通过；2026-10-13 用户明确回复“接受”，确认其余 22 条初判。以下为冻结的人工判定；如将来修订，需注明原因，不以提高指标为目的调整评分。

## 判定口径

- 答案/拒答正确：正例要求覆盖问题条件且没有错误补充；负例明确表达信息不足且不编造。
- 证据支持：工具返回文段支持完整回答。表中“核心答案”注明主答案有依据，但引用或依据描述另行判断。
- 引用正确：正例必须引用工具返回的、实际支持答案且与标注对应的 chunk_id；夹带无关引用也失败。负例不强制引用；额外引用如有仍需核验。
- 严格通过：正例 completed + 答案正确 + 证据支持 + 引用正确；负例 completed + 正确拒答 + 返回指定故事证据 + 无虚假内容/引用。
- 负例的“标注命中”填 N/A；指定故事返回只是拒答证据审查的线索，不证明全库不存在答案。

## 已核验的运行事实

两组每题均 completed，有一次成功 search_documents 调用，请求 top_k=5，返回 5 条文段；模型请求共两轮且快照与 trace 前缀对应。两组题集顺序、提示词、工具 schema、实际搜索 query/top_k 和已保存配置一致，配置只有重排开关不同。资产哈希一致。

实际运行顺序为先有重排、后无重排，与原协议预设顺序不同，如实保留；每组独立运行并预热 q002。模型权重 revision、完整依赖和硬件环境尚未保存在这两次记录中，不声明跨机器逐位复现。工具保留 top_k 请求契约，本次两组恰好均请求并返回 5 条。

| 已核验项 | 无重排 | 有重排 |
|---|---:|---:|
| completed | 12/12 | 12/12 |
| 自主调用检索 | 12/12 | 12/12 |
| 正例标注证据返回 | 5/9 | 6/9 |
| 正例出现 chunk_id 引用 | 1/9 | 0/9 |
| 正式单题耗时中位数 | 1.7404 s | 1.9376 s |

出现引用不等于引用正确；无重排 q006 的额外引用需要语义审查。耗时包含完整 Agent 运行，生成文本长度不同，差异不能全部归因于重排。

## 有重排：12 条已确认记录

原始记录：[per_query.json](../data/archive/evaluation/historical/stage2/20261012-160851-010726-agent-v1/per_query.json)。全部 12 条已由用户确认。

| ID | 标注/指定故事返回（事实） | 答案或拒答（已确认） | 证据支持（已确认） | 引用（已确认） | 严格通过（已确认） | 判定理由 |
|---|---|---|---|---|---|---|
| q001 | 是：0 | 是 | 是 | 无引用 | 否 | 回答 Lily，与返回 chunk 0 一致；缺引用。 |
| q003 | 是：500 | 否（用户确认） | 否（用户确认） | 无引用 | 否 | 用户判定：原文尚未分离，没有提及已经想念；模型将担心未来分离写成 missed him，不能接受为等义回答。 |
| q005 | 是：1001 | 是 | 是 | 无引用 | 否 | 回答 white hut；chunk 1001 支持；缺引用。 |
| q006 | 是：1250 | 是 | 是（核心答案） | 无引用 | 否 | 核心答案 hearts and flowers 正确；用分数区间描述依据，未引用 chunk_id。 |
| q007 | 否 | 否 | 否 | 无引用 | 否 | 返回文段没有标注证据，回答证据不足；这是可回答题上的失败。 |
| q015 | 否 | 否 | 否 | 无引用 | 否 | 问题问年龄，却回答 Lina 并混入另一篇故事；返回结果无标注证据。 |
| q022 | 是：5250 | 否 | 否（完整答案） | 无引用 | 否 | 正确文段讲鼓，答案另加 violin；小提琴来自另一篇故事。 |
| q038 | 否 | 否 | 否 | 无引用 | 否 | 回答 veterinarian，目标故事的答案是 owl；返回结果无标注证据。 |
| q040 | 是：9750 | 是 | 是 | 无引用 | 否 | 回答红樱桃树，chunk 9750 支持；缺引用。 |
| q041 | N/A；故事：0, 1 | 否（用户确认） | 否（用户确认） | N/A | 否（用户确认） | 用户判定：does not have 是针没有厂商与型号的断言；原文仅未说明这些信息，回答超出原文证据。 |
| q042 | N/A；故事：9250 | 否 | 否 | N/A | 否 | 把另一篇故事 chunk 818 的 laser 当成药名；目标 chunk 9250 仅写 some medicine。 |
| q045 | N/A；故事：2500, 2501 | 否 | 否 | 引用存在但不支持答案 | 否 | 编造约 50 克，引用 chunk 2500；该文段没有重量。 |

### 原始最终回答摘录

- **q001**：The person who found a needle in her room and wanted her mother to sew a button on her shirt is Lily.
- **q003**：Tim was sad when Jack was going away to university because Tim missed him and did not want to lose their friendship.
- **q005**：Lucy received a white hut from her mother in exchange for helping clean the house.
- **q006**：The pictures that decorated the special card Lily made for her mother were hearts and flowers, along with the words "I love you". The evidence comes from the text chunks identified as having scores between 0.55019 and 0.65225, which contain relevant information about the card design and sentiment expressed towards the mother.
- **q007**：The text snippets returned indicate that there is no direct evidence supporting the answer to the question "Who slid down together and hugged after Max ran away from the slide?" The retrieved documents discuss various scenarios involving characters sliding down slides, but none explicitly mention two people hugging after Max runs away from a slide. Therefore, based on the available information, the answer is: /  / Evidence insufficient.
- **q015**：The youngest child in the wealthy family who also wanted to go to university is Lina. According to the information from Tinystories, Lina grew up and pursued her dreams despite facing challenges. She worked hard, became wealthy, and later decided to use her wealth and talents to help others. Therefore, the answer to the question is: Lina.
- **q022**：The instruments that Timmy and Billy banged on when they played music together every day were drums and the violin.
- **q038**：The person who examined the bird's wing and gave it medicine after the cat took it directly to another animal for help was the veterinarian at the vet clinic.
- **q040**：According to the search results, what caught Sarah's attention while she was walking through the park with her mother was a big tree with lots of bright red cherries on it.
- **q041**：The needle mentioned in the story does not have an exact manufacturer and model number.
- **q042**：The medicine given to the bird by the owl is **Laser**. The dose is not specified in the text.
- **q045**：他们使用了大约 50 克的泥巴。 /  / (chunk_id: 2500)

## 无重排：12 条已确认记录

原始记录：[per_query.json](../data/archive/evaluation/historical/stage2/20261012-161523-426332-agent-v1/per_query.json)。全部 12 条已由用户确认。

| ID | 标注/指定故事返回（事实） | 答案或拒答（已确认） | 证据支持（已确认） | 引用（已确认） | 严格通过（已确认） | 判定理由 |
|---|---|---|---|---|---|---|
| q001 | 是：0 | 否 | 否（完整答案） | 无引用 | 否 | 除 Lily 外又声称 Ben 找针让母亲缝纽扣；返回的 Ben 故事其实是他帮 Lily 缝娃娃裙子。 |
| q003 | 是：500 | 是 | 是 | 无引用 | 否 | 明确回答担心 Jack 上大学后与自己分离；chunk 500 支持；缺引用。 |
| q005 | 是：1001 | 是 | 是 | 无引用 | 否 | 回答 white hut；chunk 1001 支持；缺引用。 |
| q006 | 是：1250 | 是 | 是（核心答案） | 否：包含无关引用 | 否 | 核心答案正确，但列出全部五个 ID；6350 讲手机、5540 讲签名，不能支持卡片图案。 |
| q007 | 否 | 否 | 否 | 无引用 | 否 | 可回答题上回答证据不足；返回结果没有标注文段。 |
| q015 | 否 | 否 | 否 | 无引用 | 否 | 问年龄却回答 Lily 并混合故事情节；返回结果没有标注文段。 |
| q022 | 是：5250 | 是 | 是 | 无引用 | 否 | 回答 drum，返回的 5249/5250 支持；缺引用。 |
| q038 | 否 | 否 | 否 | 无引用 | 否 | 回答 veterinarian 而不是 owl；返回结果没有标注文段。 |
| q040 | 否 | 否 | 否 | 无引用 | 否 | 回答 Sarah 抓糖果引起母亲注意，目标故事是樱桃树引起 Sarah 注意。 |
| q041 | N/A；故事：0 | 是（拒答） | 是（故事范围） | N/A | 是（已确认） | 明确回答证据不足，返回了指定故事 chunk 0，未编造细节。 |
| q042 | N/A；故事：未返回 | 是（拒答） | 否 | N/A | 否 | 回答证据不足，但没有返回指定猫与猫头鹰故事；不计证据支持的严格通过。 |
| q045 | N/A；故事：2500, 2501 | 否 | 否 | N/A | 否 | 编造约 10 克；返回的 2500/2501 未提供重量。 |

### 原始最终回答摘录

- **q001**：The story mentions two instances where someone found a needle in their room and wanted their mother to sew a button on their shirt: /  / 1. A little girl named Lily found a needle in her room and wanted her mother to sew a button on her shirt. / 2. A boy named Ben found a needle in his room and wanted his mother to sew a button on his doll's dress. /  / Both stories involve children finding needles in their rooms and wanting their mothers to sew buttons onto items like shirts or dolls. The evidence for these events is clear from the text snippets returned by the search tool.
- **q003**：Tim was sad because he was worried that Jack would be separated from him while attending university.
- **q005**：Lucy received a white hut from her mother in exchange for helping clean the house.
- **q006**：The pictures that decorated the special card Lily made for her mother were hearts and flowers, along with the words "I love you". The evidence comes from the text chunks with chunk_ids 1250, 5400, 1249, 6350, and 5540.
- **q007**：The text mentions that Max ran away from the slide, and later, Lily and Max were sad because they missed the slide. However, there is no direct evidence of anyone sliding down together and hugging after Max ran away from the slide. Therefore, the answer is: Evidence insufficient.
- **q015**：The youngest child in the wealthy family who also wanted to go to university was Lily. According to the text, Lily was a little girl named Lily who loved playing and never wanted to go to sleep. Her mother told her to study for her school, but Lily refused and went to bed instead. Later, Lily's mother encouraged her to study, and she eventually became very good at what she did.
- **q022**：The instrument that Timmy and Billy banged on when they played music together every day is a **drum**.
- **q038**：The person who examined the bird's wing and gave it medicine after the cat took it directly to another animal for help was the veterinarian at the vet clinic.
- **q040**：Sarah caught her mother's attention when she reached into the jar and grabbed a handful of candy.
- **q041**：证据不足。
- **q042**：证据不足。
- **q045**：他们使用了大约 10 克的粘土来制作这个特别的东西。

## 用户复核区

- 有重排 q003：2026-10-13 用户确认答案与证据支持均不通过。理由：“想念是原文没有提及的，那会还没有分离。” 标注证据确实返回，与引用遗漏分别计分，不能因拿到正确文段而将答案判正确。
- 有重排 q041：2026-10-13 用户确认正确拒答、证据支持与严格通过均不通过。理由：“我认为是断言，超出原文证据。” 目标故事确实返回，但资料未提供信息不能推出信息不存在。
- 其余 22 条：2026-10-13 用户明确回复“接受”，按表中判定固定。

后续保持同一语义标准：接受不改变事实的等义措辞，但不能把尚未发生的事件写成已经发生，也不能把“未说明”改成“不存在”。最终有重排组正例答案正确数为 4/9，修正了先前含 q003 的暂定 5/9；无重排组同为 4/9。有重排组正确拒答为 0/3。

已按同一口径统计每组分子/分母：答案正确率 9 题；标注证据返回率 9 题；证据支持率 9 题；引用正确率 9 题；负例拒答率 3 题；证据支持的拒答率 3 题；严格通过率 12 题。适用性不同的 N/A 不混入专项分母。

人工判定已固定。下一步选择一项回答约束优化，保持题集、评分、模型和检索参数不变，与同模式基线对照；优化实现优先由用户完成。原始结果不覆盖。

## 最终人工评分汇总

| 指标 | 无重排 | 有重排 |
|---|---:|---:|
| completed | 12/12 | 12/12 |
| 自主检索 | 12/12 | 12/12 |
| 正例标注证据返回 | 5/9 | 6/9 |
| 正例答案正确 | 4/9 | 4/9 |
| 正例核心答案证据支持 | 4/9 | 4/9 |
| 正例引用正确 | 0/9 | 0/9 |
| 正例缺引用 | 8/9 | 9/9 |
| 负例正确拒答 | 2/3 | 0/3 |
| 负例证据支持的拒答 | 1/3 | 0/3 |
| 严格通过 | 1/12 | 0/12 |

证据支持项沿用用户接受的判定：q006 的核心答案有原文支持，其附加引用/依据说明单独评分，不能据此把完整回答当作严格通过。

机器可读评分分别追加到两个运行目录的 `manual_review.json`，原始 `per_query.json`、`summary.json`、配置及快照不修改。每份包含 12 条判定、确认状态和各项分子/分母；判定理由以本文为准。

## 追加：v1_citation 最终复核（2026-10-13）

本节属于新提示词实验，不修改上面的 v1 基线评分。无重排目录为 `20261013-093821-150038-agent-improved_v1_citation)`，有重排目录为 `20261013-093918-574513-agent-improved_v1_citation)`，均位于 `data/archive/evaluation/historical/stage2/`。

用户分析后接受以下两题的澄清判定，均来自有重排组：

| ID | 标注证据返回 | 核心答案正确 | 核心答案有证据支持 | 引用 | 严格通过 | 判定理由 |
|---|---|---|---|---|---|---|
| q006 | 是：1250；另返回 1249 | 是 | 是 | 不通过：完整引文归属错误 | 否 | 1249 已写明 hearts and flowers，能够支持核心答案，但止于 and said。模型将包含 I love you 的完整句子归给 1249；完整文字实际在返回的 1250。不是要求被引用文段必须句子完整，而是要求所引用编号支持对应陈述。 |
| q040 | 是：9750 | 否 | 否 | 缺引用 | 否 | 问题问什么吸引 Sarah 的注意，原文为挂满鲜红樱桃的大树；答案却声称 Sarah 接住一颗大樱桃。正确证据已返回，错误发生在生成阶段。检索命中不等于引用正确，最终答案没有编号。 |

用户随后对完整批量复核表明确回复“我确认”，本轮两组共 24 条判定全部冻结。评分沿用 v1 标准，以下为最终逐题理由与汇总。


| ID | 无重排：已确认 | 有重排：已确认 |
|---|---|---|
| q001 | 答案 Lily 及母亲缝纽扣均有原文支持，去掉了原先无依据的 Ben 情节；缺引用。 | 答案 Lily 正确；缺引用。 |
| q003 | 正确表达担心 Jack 上大学后分离；缺引用。 | 仍声称已经想念，超出尚未分离的事实范围；缺引用。 |
| q005 | 白色小屋，答案正确；缺引用。 | 白色小屋，答案正确；缺引用。 |
| q006 | 爱心和花朵正确；引用 1250，完整引文与原文对应；严格通过。 | 核心答案爱心和花朵正确；1249 支持核心答案，但止于 and said，模型将 1250 才完整出现的引文归给 1249，引用不通过。 |
| q007 | 混入无依据的滑下、拥抱情节，未回答正确人物；缺引用。 | 错答 Lily 和 Max，标注答案为 Ben 和 Lily；缺引用。 |
| q015 | 问题问年龄却回答 Lily，未返回标注证据；缺引用。 | 问题问年龄却回答 Lina，未返回标注证据；缺引用。 |
| q022 | 回答鼓，返回原文支持；缺引用。 | 回答鼓或大鼓，返回原文支持；缺引用。 |
| q038 | 错答兽医，目标答案是猫头鹰，未返回标注证据；缺引用。 | 错答兽医，目标答案是猫头鹰，未返回标注证据；缺引用。 |
| q040 | 可回答题拒答，标注证据未返回；缺引用。 | 正确证据 9750 已返回，却将樱桃树吸引注意改成接住一颗大樱桃；答案错误、缺引用。 |
| q041 | 返回目标故事 0 并明确说证据不足，未编造信息；严格通过。 | 虽追加证据不足，仍断言针没有厂家型号；沿用原标准，不能将未说明推为不存在。 |
| q042 | 明确拒答，但未返回目标故事，严格不通过。 | 将其他故事的 Laser 当药名，答案无证据支持。 |
| q045 | 编造约 10 克，返回的目标故事未给出重量。 | 编造约 100 克，返回的目标故事未给出重量。 |

| 指标 | 无重排 | 有重排 |
|---|---:|---:|
| completed | 12/12 | 12/12 |
| 自主检索 | 12/12 | 12/12 |
| 正例标注证据返回 | 5/9 | 6/9 |
| 正例答案正确 | 5/9 | 4/9 |
| 正例核心答案证据支持 | 5/9 | 4/9 |
| 正例引用正确 | 1/9 | 0/9 |
| 正例缺引用 | 8/9 | 8/9 |
| 负例正确拒答 | 2/3 | 0/3 |
| 负例证据支持的拒答 | 1/3 | 0/3 |
| 严格通过 | 2/12 | 0/12 |

无重排相对 v1：答案正确 4/9 → 5/9，引用正确 0/9 → 1/9，严格通过 1/12 → 2/12。有重排三项分别保持 4/9、0/9、0/12，但 q022 改善与 q040 退步相互抵消。每组仍有 8/9 正例缺引用。收益有限，不能称为全面提升；这是已见小样本上的实验。两个新运行目录已追加 manual_review.json，原始结果与 v1 评分不变。

## 追加：句末引用实验最终复核（2026-10-13）

有重排目录 `20261013-095327-737486-agent-improved_v1_citation)`，无重排目录 `20261013-095427-474647-agent-improved_v1_citation)`。虽然目录后缀与上轮相同，本轮实际提示已改为一句话回答并在句末注明依据；以保存的 prompt 区分版本。以下内容不修改上轮已确认评分。

### 用户已确认：有重排 q003

问题为 Why was Tim sad when Jack was going away to university? 原文 chunk 500 写明 We will be separated now that you're going away. I don't want that to happen! 模型回答 Tim was sad because Jack was going away to university. (依据：chunk_id=500)。

用户判定：“这个回答不过是在重复题目，没有回答‘即将分开，不希望分开’”。答案正确与严格通过均不通过；标注证据已返回，错误在生成阶段遗漏核心因果。引用编号来自工具结果，原文支持 Jack 将离开的陈述，引用归属可通过；这不能替代对答案是否回答所问原因的判断。

### 本轮批量终评

用户对批量复核表回复“可以”，本轮共 24 条判定全部确认。下表为最终判定。

| ID | 无重排已确认 | 有重排已确认 |
|---|---|---|
| q001 | Lily 正确，引用 0 支持；严格通过 | Lily 正确，引用 0 支持；严格通过 |
| q003 | 已经想念超出原文事实，缺引用；不通过 | 重复题目而遗漏不愿分离的原因，引用 500 归属正确；已确认不通过 |
| q005 | 错答狗，9093 不支持目标事件；不通过 | 白色小屋正确，引用 1001 支持；严格通过 |
| q006 | 核心答案和完整引文对应 1250；严格通过 | 核心答案和完整引文对应 1250；严格通过 |
| q007 | 回答悲伤而未回答正确人物，引用 4443 不支持目标事件；不通过 | 错答 Lily，1596 不支持所问事件；不通过 |
| q015 | 问年龄却回答 Lina，6694 不支持所问年龄；不通过 | 问年龄却回答 Lina，7007 不支持所问年龄；不通过 |
| q022 | 鼓正确，但引用 4801 为另一个没有 Billy 的故事；不通过 | 鼓正确，引用 5250 支持；严格通过 |
| q038 | 错答兽医，5552 不支持猫带鸟向猫头鹰求助的目标事件；不通过 | 同样错答兽医并引用 5552；不通过 |
| q040 | 可回答题拒答且缺引用；不通过 | 仍编造接住樱桃，9750 不支持该动作；不通过 |
| q041 | 返回指定故事并明确证据不足；严格通过 | 改为 not specified，表达未说明而非不存在，目标故事已返回；严格通过 |
| q042 | 正确拒答但目标故事未返回；严格不通过 | 编造 Laser 药名，8634 不支持；不通过 |
| q045 | 编造约 100 克，2500 未给出重量；不通过 | 同样编造约 100 克并引用 2500；不通过 |

最终严格通过为无重排 q001、q006、q041（3/12），有重排 q001、q005、q006、q022、q041（5/12）。有重排 q003 不因带正确编号而计通过。两个运行目录已新增 manual_review.json；原始记录及之前两轮的评分不修改。


| 最终指标 | 无重排 | 有重排 |
|---|---:|---:|
| completed | 12/12 | 12/12 |
| 自主检索 | 12/12 | 12/12 |
| 正例标注证据返回 | 3/9 | 6/9 |
| 正例答案正确 | 3/9 | 4/9 |
| 正例核心答案证据支持 | 3/9 | 4/9 |
| 正例引用归属正确 | 2/9 | 5/9 |
| 正例缺引用 | 2/9 | 0/9 |
| 负例正确拒答 | 2/3 | 1/3 |
| 负例证据支持的拒答 | 1/3 | 1/3 |
| 严格通过 | 3/12 | 5/12 |

有重排 q003 引用归属通过，只表示 500 支持其所写的离开事实；答案未解释所问原因，核心答案正确、核心答案证据支持和严格通过均不通过。此处核心答案证据支持不等于逐句事实真实性；不得据此说该句离开事实为编造。无重排 q022 返回 5249 可支持核心乐器答案，但选用 4801 不能支持目标人物事件，故引用与严格通过不通过。

相对上一轮，无重排严格通过 2/12 → 3/12，但答案正确 5/9 → 3/9；有重排严格通过 0/12 → 5/12，答案正确仍为 4/9。相对最初 v1 严格通过分别为 1/12 → 3/12、0/12 → 5/12。收益主要来自引用与正确拒答，不能称为全面提升。查询发生变化，本轮并非固定检索结果的回答消融；12 题反复用于提示调试，不作为独立测试集效果。


## 追加：逐故事切分 v2 Agent 结果（3 条已确认，其余待确认）

有重排目录 20261013-143642-156957-agent-stage2-story-boundaries-qwen128-overlap32-v2-reviewed；无重排目录 20261013-143834-593213-agent-stage2-story-boundaries-qwen128-overlap32-v2-reviewed。两组正式运行使用新已复核题集/索引/文段；本节为模型输出人工评分初评，不与先前“迁移标注审核完成”混淆。

对照为旧切分候选 50 的同模式运行（100316 有重排、100217 无重排）。已验证模型/参数、提示、每题实际检索 query/top_k、工具 schema 一致；新资产及快照哈希正确，所有模型请求消息与 trace 前缀一致。两组均 12 completed、12 次成功检索、每题返回 5 条，两组 q002 均真实检索预热。

| 已核验事实 | 旧切分无重排 | 新切分无重排 | 旧切分有重排 | 新切分有重排 |
|---|---:|---:|---:|---:|
| 正例标注证据返回 | 3/9 | 5/9 | 7/9 | 9/9 |
| 新切分正例出现 chunk_id | — | 7/9 | — | 9/9 |
| 新切分负例目标故事返回 | — | 3/3 | — | 3/3 |

旧/新相关文段 ID 随切分迁移，标注 evidence_mode 和语义要求保留。这里只报告命中经用户复核的标签，不当作答案正确率；正例相关块数量可能变化，不能直接将 Recall 题内分母变化归为能力变化。实际答案必须与所引文段核对。

| ID | 无重排判定（未注明确认的仍为初评） | 有重排判定（未注明确认的仍为初评） |
|---|---|---|
| q001 | Lily 正确，引用目标块；严格通过候选。 | Lily 正确，引用目标块；严格通过候选。 |
| q003 | 用户已确认通过：分离与希望维持友谊已揭露悲伤原因，接受该因果概括；引用 000256_001 支持，严格通过。 | 加入已经想念及不愿失去友谊，沿用原标准不通过；引用也不能支持已经想念。 |
| q005 | 错答 shiny medal，目标故事未返回；不通过。 | 白色小屋正确，引用 000515_000；严格通过候选。 |
| q006 | 缺少 flowers，引用另一篇故事 002452_001，且该块没有所声称图案；不通过。 | 爱心、花朵和文字均有 000656_000 支持；严格通过候选。 |
| q007 | 错答 Max 和 Lily，标注目标块未返回；缺引用，不通过。 | Ben 和 Lily 正确，引用 000741_003；严格通过候选。 |
| q015 | 三岁正确但引用 002146_003 的兄妹迎接婴儿故事，无年龄/大学依据；严格不通过。 | 三岁正确，引用 001662_000；严格通过候选。 |
| q022 | 鼓正确，引用 002365_001；严格通过候选。 | 鼓正确，引用 002365_001；严格通过候选。 |
| q038 | 目标原文已返回仍错答 vet，引用另一篇 004195_001；不通过。 | 用户已确认：猫头鹰核心答案正确且有证据支持；引用 004500_001 从 to a wise owl 开始，未完整支持附加的猫带鸟求助动作，引用及严格通过均不通过。 |
| q040 | 可回答题拒答，标注目标块未返回；不通过。 | 用户已确认通过：接受 cherry 为原文树上樱桃的简略表达，未编造接住动作；引用 004763_000 支持，严格通过。 |
| q041 | 明确证据不足，目标故事两块返回；严格通过候选。 | 表达未明确说明厂家型号并拒答，目标故事两块返回；严格通过候选。 |
| q042 | 编造 rotten apple 药名和剂量，虽引用目标故事 004500_000 但其只写 some medicine；不通过。 | 编造 Laser 药名和 1 unit 剂量，引用目标故事不支持；不通过。 |
| q045 | 编造 100 克；不通过。 | 编造 100 克，缺引用；不通过。 |

表中简写 ID 省略 story_ 与 chunk_，实际记录保持完整 ID。2026-10-13 用户确认上述三个边界：无重排 q003 通过，有重排 q038 核心答案通过但引用及严格判定不通过，有重排 q040 通过。q003 的理由为“尽管要分离和想要维持友谊已经揭露了原因”；后两题接受助手判定。该回复未明确确认其余 21 条，故其他条目仍保留初评，暂不发布两组最终严格通过数或生成整组确认版 manual_review.json。不修改旧评分口径，不因正例 9/9 命中而自动全判严格通过。两组 comparison_audit.json 保持原始客观核验记录。
