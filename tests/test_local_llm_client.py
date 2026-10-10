"""Local Qwen generation and Agent-message adaptation checks."""

import pytest
import json
from rag_agent_system.agents.llm_client import LocalLLMClient
from rag_agent_system.config import load_config
from rag_agent_system.tools.schemas import CALCULATOR_SCHEMA


def test_local_model_emits_calculator_tool_call() -> None:
    config = load_config()
    client = LocalLLMClient(
        model_name=config.agent.model_name,
        max_new_tokens=config.agent.max_new_tokens,
    )
    messages = [
        {"role": "user", "content": "请使用 calculator 计算 12 × 8，并根据工具结果回答。"},
    ]

    raw_response = client._generate_text(messages, [CALCULATOR_SCHEMA])
    assert "<tool_call>" in raw_response
    assert "</tool_call>" in raw_response
    json_text = raw_response.split("<tool_call>", 1)[1].split("</tool_call>", 1)[0]
    tool_call = json.loads(json_text)
    assert tool_call["name"] == "calculator"
    assert tool_call["arguments"]["operation"] == "multiply"
    assert tool_call["arguments"]["a"] == 12
    assert tool_call["arguments"]["b"] == 8


@pytest.mark.parametrize(
    "raw_response, expected_kind",
    [
        pytest.param(
            '<tool_call>\n{"name": "calculator", "arguments": '
            '{"operation": "multiply", "a": 12, "b": 8}}\n</tool_call>',
            "tool_call",
            id="tool-call",
        ),
        pytest.param("计算结果是 96。", "direct_answer", id="direct-answer"),
    ],
)
def test_chat_normalizes_model_response(
    monkeypatch: pytest.MonkeyPatch,
    raw_response: str,
    expected_kind: str,
) -> None:
    client = LocalLLMClient(model_name="unused-local-model", max_new_tokens=16)
    monkeypatch.setattr(client, "_generate_text", lambda messages, tools: raw_response)
    messages = [{"role": "user", "content": "请使用 calculator 计算 12 × 8。"}]

    response = client.chat(messages, [CALCULATOR_SCHEMA])
    assert response["role"] == "assistant"
    if expected_kind == "tool_call":
        assert response["content"] == ""
        calls = response["tool_calls"]
        assert len(calls) == 1
        call = calls[0]
        assert isinstance(call["id"], str) and call["id"]
        assert call["name"] == "calculator"
        assert call["arguments"] == {"operation": "multiply", "a": 12, "b": 8}
    else:
        assert response["content"] == "计算结果是 96。"
        assert not response.get("tool_calls")


@pytest.mark.parametrize(
    "raw_response",
    [
        pytest.param(
            '<tool_call>\n{"name": "calculator", "arguments": {}}',
            id="missing-closing-tag",
        ),
        pytest.param("</tool_call>", id="missing-opening-tag"),
    ],
)
def test_chat_rejects_incomplete_tool_call(monkeypatch, raw_response):
    client = LocalLLMClient(model_name="unused-local-model", max_new_tokens=16)
    monkeypatch.setattr(client, "_generate_text", lambda messages, tools: raw_response)

    with pytest.raises(ValueError):
        client.chat([{"role": "user", "content": "calculate"}], [CALCULATOR_SCHEMA])

