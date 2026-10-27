from copy import deepcopy
from typing import Any

from rag_agent_system.datasets import DatasetName

CALCULATOR_SCHEMA = {
    "name": "calculator",
    "description": "对两个数字执行加、减、乘、除运算。",
    "parameters": {
        "type": "object",
        "properties": {
            "operation": {
                "type": "string",
                "enum": ["add", "subtract", "multiply", "divide"],
                "description": "要执行的运算。",
            },
            "a": {"type": "number", "description": "第一个数字。"},
            "b": {"type": "number", "description": "第二个数字。"},
        },
        "required": ["operation", "a", "b"],
        "additionalProperties": False,
    },
}

SEARCH_DOCUMENTS_SCHEMA = {
    "name": "search_documents",
    "description": (
        "检索本地 TinyStories 故事资料库并返回原文片段。"
        "回答 TinyStories 中的人物、情节或事件问题时，先调用此工具查找证据；"
        "普通常识问题无需检索。"
    ),
    "parameters": {
        "type":"object",
        "properties": {


            "query":{"type":"string","description":"用户提出来的问题","minLength":1},
            "top_k":{"type":"integer","description":"控制返回的文段数目","minimum":1,"maximum":10}
        },
        "required": ["query","top_k"],
        "additionalProperties": False,
    }
}

SEARCH_DOCUMENTS_DESCRIPTIONS: dict[DatasetName, str] = {
    "tinystories": SEARCH_DOCUMENTS_SCHEMA["description"],
    "sec": (
        "检索本地 SEC 公司申报文件资料库并返回原文片段及 chunk_id。"
        "回答公司业务、风险、财务指标或跨报告比较问题时，先检索支持答案的证据。"
        "query 应保留公司或 ticker、报告财年和目标指标；"
        "跨公司或跨年度问题可以分别检索。公司和财年通过查询文本表达，"
        "本工具当前不提供结构化元数据过滤参数。"
    ),
}


def build_search_documents_schema(
    dataset: DatasetName = "tinystories",
) -> dict[str, Any]:
    """Return an independent schema for the selected dataset."""
    if dataset not in SEARCH_DOCUMENTS_DESCRIPTIONS:
        raise ValueError(f"Unknown dataset: {dataset}")
    schema = deepcopy(SEARCH_DOCUMENTS_SCHEMA)
    schema["description"] = SEARCH_DOCUMENTS_DESCRIPTIONS[dataset]
    return schema


TIME_SCHEMA = {
    "name": "time",
    "description":"根据用户提供的时区，提供时间查询",
    "parameters": {
        "type":"object",
        "properties": {
    "timezone_name": {
        "type": "string",
        "enum": ["UTC", "Asia/Shanghai"],
        "description": "指定查询的时区",
    },
},
        "required": ["timezone_name"],
        "additionalProperties": False,
    }
}
