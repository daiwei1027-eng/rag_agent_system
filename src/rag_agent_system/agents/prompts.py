"""TinyStories question prompt shared by Agent evaluation entry points."""

PROMPT_TEMPLATE = (
    "请回答 TinyStories 资料库中的问题。仅根据工具返回的原文片段回答，"
    "并给出直接支持答案的 chunk_id；编号必须来自工具结果。\n"
    "如需检索，请只提出一次简短的英文查询，返回 5 条文段，"
    "然后根据返回的文段回答。\n"
    "有直接证据时，用一句话简短回答，并在该句末尾注明"
"（依据：chunk_id=<编号>）；该编号对应的原文必须支持这句话的全部事实。\n"
    "如果没有直接证据，请明确说明“证据不足”，不要猜测；"
    "不可回答时无需编造引用。\n"
    "问题：{query}"
)

def build_agent_prompt(question: str) -> str:
    return PROMPT_TEMPLATE.format(query=question)
