# SEC corpus：准备阶段

六份 HTML 已从用户提供的本地文件复制到 `raw/`，按公司与财年规范命名。
复制不改写原始字节，已逐份比较原件与副本的 SHA256。原件保持不变。
`raw/` 为本地输入，不进入 Git；manifest 草稿和说明可以提交。

## manifest 草稿

`manifest.draft.json` 的 `source_file` 相对于 manifest 所在目录解析。
公司、财年和完整报告期已与本地 Inline XBRL 对应；公司 CIK、表单、报告期、
accession 与主文档名称已核对 SEC 官方申报详情页。
`accession_number` 与 `source_url` 已补齐；证据及核对范围见 `source-verification.json`。
当前文件仍为草稿，尚未完成章节内容验收与 corpus 版本冻结。
文件大小及 hash 不足以证明报告内容完整或来源真实。

## 当前学习任务：本地 manifest 校验

建议在 `src/rag_agent_system/ingestion/sec_manifest.py` 实现：

```python
from pathlib import Path
from typing import Any


def validate_local_manifest(manifest_path: Path) -> list[dict[str, Any]]:
    """校验本地输入并返回文档记录；不负责认证 SEC 来源。"""
    raise NotImplementedError
```

本次固定范围：

1. 校验 schema_version=1、非空 documents 列表、每条记录的 document_id、
   source_file、sha256 和 size_bytes；ID 和路径唯一，大小为正整数且不接受 bool，
   SHA256 为 64 位十六进制字符串。
2. 以 manifest 目录为基准解析路径；只接受解析后位于其 raw/ 内的 HTML 文件。
3. 校验文件存在、实际字节数与 SHA256 一致；错误包含文档 ID 或记录位置。

此函数允许草稿里的 accession_number/source_url 为空；正式来源校验属于下一步。
通用函数不写死六份文件；本次真实数据验收期望返回六条。

集中验收：真实六份成功；临时小文件构造缺文件、hash 不符、重复 ID、
路径越界和格式错误等代表性失败输入。同类格式错误可参数化。
无需加载模型、构建索引或引入新的测试框架。

## 后续范围

本地校验与来源信息核对已完成，下一步选一份年报实现 Item 1、1A、7
章节抽取。章节抽取单独验收后才进入分块、索引及新 benchmark。
TinyStories 配置、题集与历史实验保留，Git 提交和推送由用户完成。

## 2026-10-20 本地校验审查

- 已直接调用用户实现核对真实 manifest：六份文件全部返回，大小和 SHA256 匹配。
- 新增 `tests/test_sec_manifest.py`，集中检查格式、解析后路径查重、目录越界、
  缺文件、大小/hash 不符以及有效摘要大小写等行为；未修改用户核心实现。
- 在 hf_llm 环境运行，20 passed、2 failed。两项失败均为缺字段时暴露 KeyError：
  根对象缺 schema_version，以及文档记录缺 size_bytes。
  这是修复前的结果。
- 首次测试因沙箱无法创建 pytest 临时目录而发生环境错误，经授权在沙箱外重跑后
  得到上述结果；环境错误不计为业务校验失败。
- 此次验证只涉及本地输入一致性与代表性边界；未认证 SEC 来源、报告完整性，
  尚未完成 accession、URL 和完整日期的独立核验。

同日用户授权助手直接完成剩余修复：已在读取字段前检查根对象与每条文档的必要字段，
缺字段抛出包含字段名的 ValueError，文档错误同时标出从 0 开始的记录位置。
复跑原有验收为 22 passed，真实六份文件的大小与 SHA256 再次核对通过。
本地 manifest 校验阶段完成；来源核验继续作为下一步，当前 manifest 仍为草稿。

## 2026-10-20 来源信息核对完成

六份报告的本地保存来源 URL 与 SEC 官方申报详情页已对应，补齐 accession 与规范
source_url（去除浏览器保存链接中的跟踪参数）。本地 Inline XBRL 的公司 CIK、
form、财年与完整报告期均与预期一致；日期包含 continuedAt 指向的后续文本，
不能只读取第一个 ix:nonNumeric 的直接文本。

核对详情、官方申报详情页链接和本地 hash 绑定保存在 `source-verification.json`。
Microsoft 正文超过浏览工具上限，官方核对使用申报详情页的主文档和报告期信息；
NVIDIA、Alphabet 同时查看了官方正文封面日期。
更新后直接调用本地校验函数，六份文件的大小与 hash 仍全部通过；未改动原始 HTML。

本地 HTML 是浏览器保存快照，与 SEC 详情页列出的主文档字节数不同。
manifest 中的 size_bytes、sha256 绑定本地快照，不代表官网 HTTP 响应原始字节；
本次没有做全文逐字比较，也没有据此认证每个章节完整。

本次尝试按 UTF-8 解码 HTML 时出现 UnicodeDecodeError；随后按原始字节交给本机
BeautifulSoup 检测编码，六份均检测为 windows-1252，记录在核对结果中。
后续解析不要默认所有原始 HTML 都是 UTF-8，也不要用 errors="ignore" 静默丢字。
BeautifulSoup 本次仅用于检查；正式 ingestion 使用前需将选定的解析依赖声明到项目中。

下一项学习任务仅处理 Microsoft FY2025 的 Item 1、1A、7：保留正文段落和来源
anchor，排除目录匹配，人工核对章节首尾。不在本任务接入 chunking、索引或 benchmark。

## Microsoft FY2025 段落抽取进展

用户在 `notebooks/html.ipynb` 实现 extract_paragraphs，使用开始/结束标题 ID 定位，
按文档顺序遍历 p，并保留祖先包含 div.main-content-container 的非空段落。
结束判断先于容器过滤；缺少边界或无法在开始之后遇到结束标题时明确报错。

对 Item 1 → Item 1A 的真实检查：过滤前 199 段，过滤后 160 段；开头为 GENERAL
及业务介绍，结尾为 AVAILABLE INFORMATION 的网站说明。已观察到的页码、PART I、
Item 1A 页眉被排除。缺少开始标题、结束标题位于开始之前的代表性错误已检查。
未修改用户函数，本次直接调用 notebook 中保存的定义验证。

当前完成的是这一章节的段落抽取检查，不代表六份报告的通用清洗完成。
这一章节的管理层表格有 p 文本，能够被当前遍历读出，但返回扁平字符串会丢失
表头/行列关系；正式结构化 ingestion 时需决定如何保留表格，不把本次结果视为
完整表格解析。下一步批量检查同一份报告的 Item 1A 与 Item 7，之后再归纳结构契约。

同日继续检查用户输出：Item 1A 为 75 个非空 p 文本，开头是风险说明，结尾是人才
招募和保留风险；Item 7 为 410 个非空 p 文本，开头为 MD&A 说明，结尾为管理层
财务报表责任声明及签署人。已回看原始 HTML：该声明与签署人位于 Item 7A 正式
标题之前，章节结束位置符合当前按主 Item 边界提取的定义，不因姓名结尾而删除。
三项目标章节的 Microsoft FY2025 试点边界与已观察页眉/页码过滤检查完成；尚未做
全文内容覆盖认证、表格结构保留或其余五份文件的结构兼容检查。

## 三家公司共用的目录锚点定位

用户已在 notebook 实现 find_section_anchor：精确匹配统一空白后的目录标题，
从 href 提取 fragment，检查目标 id 存在，集合去重后要求唯一目标。
直接调用保存的函数，对六份报告各检查 Business、Risk Factors、Unresolved Staff
Comments、MD&A 和 Market Risk 五个目录标题，30/30 次定位成功。
同目标重复链接、标题缺失、fragment 缺失、目标不存在、不同目标歧义五类小样例
均符合预期。此为一次直接脚本验收，不计入 pytest 项目测试数量。

跨文件观察：Microsoft 两份的目标为带语义 ID 的 p，均有 main-content-container；
NVIDIA 和 Alphabet 的目标为带生成 ID 的空 div，均无该正文容器 class。
因此目录定位可共用，现有仅遍历 p、过滤 Microsoft class 的内容抽取不能直接共用。
下一步设计跨标签的章节边界遍历与正文块提取，避免对嵌套容器重复 get_text，
再统一章节输出；当前未生成 SEC chunk 或索引。

## 跨标签章节范围遍历完成

用户在 notebook 实现 collect_section_elements，返回 Tag 列表，不进行正文过滤或
文字转换。直接调用该函数与 find_section_anchor，对六份报告各检查三个目标章节，
18/18 个范围均非空、返回 Tag、能够到达并排除结束锚点。另以小样例检查嵌套标签
保留、空 div 结束锚点、边界缺失与逆序，均符合预期。这只证明范围遍历行为，
不证明祖先容器的整段 get_text 严格限于范围或已经完成清洗。
下一步选择正文块，避免嵌套元素重复提取，并把表格作为独立块保留。

## 正文候选块筛选完成

用户在 notebook 实现 select_content_blocks：跳过有 table 祖先的节点，保留最外层
table，以及不包含更深 p/div/table/ul/ol/li 的 p/div/li。返回 Tag，保持输入顺序。
直接脚本检查嵌套容器与 span 去重、列表文字、嵌套表格只保留外表、空输入，均通过。
六份报告的 18 个章节均产生非空候选块，所选块之间没有祖先/后代关系，未选入
表格内部子元素。此检查为结构行为验收，不是全文无遗漏或去噪验收，也未新增 pytest。

真实候选结果仍有空 div、页眉页码等内容；最外层 table 可能是数据表，也可能用于
排版/列表，不能把所有 table 默认解释为财务表格。下一步集中处理空块与排版噪声，
然后保留来源信息生成统一章节记录；尚未生成 chunk 或构建索引。

## 第一版排版噪声过滤验收完成

用户在 notebook 实现 is_noise_block：空文字块删除；MSFT 删除正文容器外候选块；
其余当前文档检查祖先的 position:absolute 与 bottom:0 页脚声明；NVDA/GOOG
按完整页眉文字及 Table of Contents 链接组合识别目录页眉。正常分支返回 False。

直接脚本集中检查 16 个代表性输入，覆盖三种 ticker 的空块、正文年份数字和数据表，
MSFT 非正文区、嵌套页脚、目录页眉、正文提及目录及无链接短语；均符合预期。
结合前面三个用户函数运行六份报告的 18 个章节，均非空，并排除了抽查目标的
PART/Item/目录独立页眉。来源 hash、候选/删除/保留数量、保留表格数量、首尾文字
预览与删除样例保存在 `cleaning-review.json`；未修改用户核心函数，未新增 pytest。

这是一版针对已核对六份 HTML 的结构与噪声验收，不认证全文无遗漏或未来来源兼容。
表格保留数量也不代表财务表格解析已完成。此阶段收尾，不继续追加相似过滤试验；
下一步为模块整理及统一章节记录输出，文字与表格分别保留，之后再设计分块。
