from rag_agent_system.tools.registry import ToolRegistry
from rag_agent_system.tools.calculator_tool import calculator
from rag_agent_system.tools.schemas import CALCULATOR_SCHEMA
import json
from typing import Any, Protocol
from copy import deepcopy
from rag_agent_system.agents.loop import Agent
import pytest
class FakeLLM:
    def __init__(self, responses: list[dict[str, Any]]) -> None:
        self.responses = responses
        self.call_count = 0
        self.message_history = []

    def chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
    ) -> dict[str, Any]:
        self.message_history.append(deepcopy(messages))
        if self.call_count>=len(self.responses):
            raise RuntimeError("FakeLLM responses exhausted")
        response=self.responses[self.call_count]
        self.call_count += 1
        return response

def test_agent_returns_answer_after_tool_call():

    registry=ToolRegistry()
    registry.register(CALCULATOR_SCHEMA,calculator)
    fake = FakeLLM([
        {
            "role": "assistant",
            "content": None,
            "tool_calls": [
                {
                    "id": "call_001",
                    "name": "calculator",
                    "arguments": {
                        "operation": "multiply",
                        "a": 12,
                        "b": 8,
                    },
                }
            ],
        },
        {
            "role": "assistant",
            "content": "12 × 8 = 96",
        },
    ])
    agent = Agent(llm=fake, registry=registry)
    result = agent.run("12 × 8 等于多少？")
    second_input = fake.message_history[1]
    assert [msg["role"] for msg in second_input] == [
        "user", "assistant", "tool"
    ]
    assert second_input[2]["tool_call_id"] == "call_001"
    observation = json.loads(second_input[2]["content"])
    assert observation["ok"] is True
    assert observation["result"] == 96
    assert result == {
        "role": "assistant",
        "content": "12 × 8 = 96",
    }
    assert fake.call_count == 2
def test_agent_passes_tool_error_back_to_llm():
    registry=ToolRegistry()
    registry.register(CALCULATOR_SCHEMA,calculator)
    fake = FakeLLM([
        {
            "role": "assistant",
            "content": None,
            "tool_calls": [
                {
                    "id": "call_div_zero",
                    "name": "calculator",
                    "arguments": {
                        "operation": "divide",
                        "a": 12,
                        "b": 0,
                    },
                }
            ],
        },
        {
            "role": "assistant",
            "content": "You can't provide 0 to be divisible by 12"
        },
    ])
    agent = Agent(llm=fake, registry=registry)
    result = agent.run("12/0=?")
    assert fake.message_history[0] == [
        {"role": "user", "content": "12/0=?"}
    ]
    assert fake.call_count == 2

    second_input = fake.message_history[1]
    assert [msg["role"] for msg in second_input] == [
        "user", "assistant", "tool"
    ]
    assert second_input[2]["tool_call_id"] == "call_div_zero"
    observation = json.loads(second_input[2]["content"])
    assert observation["ok"] is False
    assert "result" not in observation
    assert result == {"role": "assistant",
            "content": "You can't provide 0 to be divisible by 12"}
    assert observation["error"]["type"] == "ValueError"
    assert "nonzero" in observation["error"]["message"]


def test_agent_handles_multiple_tool_calls_in_one_turn():
    calls = []

    def recording_calculator(operation, a, b):
        calls.append({"operation": operation, "a": a, "b": b})
        return calculator(operation, a, b)
    registry = ToolRegistry()
    registry.register(CALCULATOR_SCHEMA, recording_calculator)
    fake = FakeLLM([
        {
            "role": "assistant",
            "content": None,
            "tool_calls": [
                {
                    "id": "call_001",
                    "name": "calculator",
                    "arguments": {
                        "operation": "multiply",
                        "a": 12,
                        "b": 8,
                    },
                },{
                    "id": "call_002",
                    "name": "calculator",
                    "arguments": {
                        "operation": "add",
                        "a": 96,
                        "b": 4,
                    },
                }
            ],
        },
        {
            "role": "assistant",
            "content": "12*8=96,96+4=100"
        },
    ])

    agent = Agent(llm=fake, registry=registry)
    result = agent.run("12*8=? and 96+4=?")
    assert fake.message_history[0] == [
        {"role": "user", "content": "12*8=? and 96+4=?"}
    ]
    assert fake.call_count == 2
    second_input = fake.message_history[1]
    assert [msg["role"] for msg in second_input] == [
        "user", "assistant", "tool", "tool"
    ]
    assert second_input[2]["tool_call_id"] == "call_001"
    assert second_input[3]["tool_call_id"] == "call_002"

    observation_0 = json.loads(second_input[2]["content"])
    observation_1 = json.loads(second_input[3]["content"])
    assert observation_0["ok"] is True
    assert observation_0["result"] == 96
    assert observation_1["ok"] is True
    assert observation_1["result"] == 100
    assert result == {"role": "assistant",
            "content": "12*8=96,96+4=100"}
    assert calls == [
        {"operation": "multiply", "a": 12, "b": 8},
        {"operation": "add", "a": 96, "b": 4},
    ]
def test_agent_stops_at_max_steps():
    calls = []

    def recording_calculator(operation, a, b):
        calls.append({"operation": operation, "a": a, "b": b})
        return calculator(operation, a, b)

    registry = ToolRegistry()
    registry.register(CALCULATOR_SCHEMA, recording_calculator)
    fake = FakeLLM([
        {
            "role": "assistant",
            "content": None,
            "tool_calls": [
                {
                    "id": "call_001",
                    "name": "calculator",
                    "arguments": {
                        "operation": "multiply",
                        "a": 12,
                        "b": 8,
                    },
                }
            ],
        },
        {
            "role": "assistant",
            "content": "12 × 8 = 96",
        },
    ])
    agent = Agent(llm=fake, registry=registry,max_steps=1)
    result = agent.run("Please the result of 12*8")
    assert result =={
                        "status": "max_steps_reached",
                        "answer": None,
                        "steps": 1,
                    }
    assert calls == [{"operation": "multiply", "a": 12, "b": 8}]
    assert fake.call_count == 1
def test_agent_returns_direct_answer_at_max_steps_1():
    calls = []

    def recording_calculator(operation, a, b):
        calls.append({"operation": operation, "a": a, "b": b})
        return calculator(operation, a, b)

    registry = ToolRegistry()
    registry.register(CALCULATOR_SCHEMA, recording_calculator)
    fake = FakeLLM([
        {
            "role": "assistant",
            "content": "hello,12*8=96",

        },

    ])
    agent = Agent(llm=fake, registry=registry,max_steps=1)
    result = agent.run("Please the result of 12*8")
    assert result =={
            "role": "assistant",
            "content": "hello,12*8=96",
        }
    assert calls == []
    assert fake.call_count == 1
@pytest.mark.parametrize(
    "question, expected_error",
    [
        (123, TypeError),
        (None, TypeError),
        ("",ValueError),
        (" ", ValueError),
    ],
)
def test_agent_rejects_invalid_question(question, expected_error):
    fake = FakeLLM([])
    agent = Agent(llm=fake, registry=ToolRegistry())

    with pytest.raises(expected_error):
        agent.run(question)
    assert fake.call_count == 0

@pytest.mark.parametrize(
    "max_steps, expected_error",
    [(True, TypeError),
        (False, TypeError),
("5", TypeError),
        (1.5, TypeError),
(None, TypeError),
        (0,ValueError),
        (-1, ValueError),
        # TODO：True、False、"5"、1.5、None → TypeError
        # TODO：0、-1 → ValueError
    ],
)
def test_agent_rejects_invalid_max_steps(max_steps, expected_error):
    fake = FakeLLM([])

    with pytest.raises(expected_error):
        agent = Agent(llm=fake, registry=ToolRegistry(),max_steps=max_steps)
    assert fake.call_count == 0
def test_agent_keeps_message_history_separate_between_runs():
    calls = []

    def recording_calculator(operation, a, b):
        calls.append({"operation": operation, "a": a, "b": b})
        return calculator(operation, a, b)

    registry = ToolRegistry()
    registry.register(CALCULATOR_SCHEMA, recording_calculator)
    fake = FakeLLM([
        {
            "role": "assistant",
            "content": "hello,12*8=96",

        },
        {
            "role": "assistant",
            "content": "hello,12+8=20",

        },

    ])
    agent = Agent(llm=fake, registry=registry, max_steps=1)
    result1 = agent.run("Please the result of 12*8")
    result2 = agent.run("Please the result of 12+8")
    assert result1 == {
        "role": "assistant",
        "content": "hello,12*8=96",
    }
    assert result2 == {
        "role": "assistant",
        "content": "hello,12+8=20",
    }
    assert calls == []
    assert fake.call_count == 2