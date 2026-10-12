
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
