import json
import threading
from copy import deepcopy
from typing import Any

import pytest

from rag_agent_system.agents.loop import Agent
from rag_agent_system.tools.calculator_tool import calculator
from rag_agent_system.tools.registry import ToolRegistry
from rag_agent_system.tools.schemas import CALCULATOR_SCHEMA


class FakeLLM:
    def __init__(self, responses: list[dict[str, Any]]) -> None:
        self.responses = responses
        self.call_count = 0
        self.message_history = []

    def chat(self, messages, tools) -> dict[str, Any]:
        self.message_history.append(deepcopy(messages))
        if self.call_count >= len(self.responses):
            raise RuntimeError("FakeLLM responses exhausted")
        response = self.responses[self.call_count]
        self.call_count += 1
        return response


def tool_call(call_id, arguments, name="calculator"):
    return {"id": call_id, "name": name, "arguments": arguments}


def tool_response(*calls):
    return {"role": "assistant", "content": None, "tool_calls": list(calls)}


@pytest.fixture
def recorded_registry():
    calls = []

    def recording_calculator(operation, a, b):
        calls.append({"operation": operation, "a": a, "b": b})
        return calculator(operation, a, b)

    registry = ToolRegistry()
    registry.register(CALCULATOR_SCHEMA, recording_calculator)
    return registry, calls


@pytest.mark.parametrize(
    "call_id, arguments, question, answer, expected_result, error_message",
    [
        pytest.param(
            "call_001", {"operation": "multiply", "a": 12, "b": 8},
            "12 × 8 等于多少？", "12 × 8 = 96", 96, None, id="success",
        ),
        pytest.param(
            "call_div_zero", {"operation": "divide", "a": 12, "b": 0},
            "12/0=?", "You can't provide 0 to be divisible by 12",
            None, "nonzero", id="division-by-zero",
        ),
    ],
)
def test_agent_returns_answer_after_tool_observation(
    recorded_registry, call_id, arguments, question, answer, expected_result, error_message,
):
    registry, _ = recorded_registry
    final_response = {"role": "assistant", "content": answer}
    fake = FakeLLM([tool_response(tool_call(call_id, arguments)), final_response])

    result = Agent(llm=fake, registry=registry).run(question)

    assert fake.message_history[0] == [{"role": "user", "content": question}]
    assert fake.call_count == 2
    second_input = fake.message_history[1]
    assert [msg["role"] for msg in second_input] == ["user", "assistant", "tool"]
    assert second_input[2]["tool_call_id"] == call_id
    observation = json.loads(second_input[2]["content"])
    if error_message is None:
        assert observation["ok"] is True
        assert observation["result"] == expected_result
    else:
        assert observation["ok"] is False
        assert "result" not in observation
        assert observation["error"]["type"] == "ValueError"
        assert error_message in observation["error"]["message"]
    assert result == final_response


@pytest.mark.parametrize(
    "first_name, question, answer, first_result",
    [
        pytest.param(
            "calculator", "12*8=? and 96+4=?", "12*8=96,96+4=100", 96,
            id="both-succeed",
        ),
        pytest.param(
            "unknown", "Use tool unknown and 96+4=?", "Unknown call_001,96+4=100", None,
            id="unknown-tool-then-success",
        ),
    ],
)
def test_agent_handles_multiple_tool_calls_in_one_turn(
    recorded_registry, first_name, question, answer, first_result,
):
    registry, calls = recorded_registry
    first_args = {"operation": "multiply", "a": 12, "b": 8}
    second_args = {"operation": "add", "a": 96, "b": 4}
    final_response = {"role": "assistant", "content": answer}
    fake = FakeLLM([
        tool_response(
            tool_call("call_001", first_args, first_name),
            tool_call("call_002", second_args),
        ),
        final_response,
    ])

    result = Agent(llm=fake, registry=registry).run(question)

    assert fake.message_history[0] == [{"role": "user", "content": question}]
    assert fake.call_count == 2
    second_input = fake.message_history[1]
    assert [msg["role"] for msg in second_input] == ["user", "assistant", "tool", "tool"]
    assert second_input[2]["tool_call_id"] == "call_001"
    assert second_input[3]["tool_call_id"] == "call_002"
    first = json.loads(second_input[2]["content"])
    second = json.loads(second_input[3]["content"])
    if first_name == "unknown":
        assert first["ok"] is False
        assert "result" not in first
        assert first["error"]["type"] == "ValueError"
        assert "not registered" in first["error"]["message"]
        assert calls == [second_args]
    else:
        assert first["ok"] is True
        assert first["result"] == first_result
        assert calls == [first_args, second_args]
    assert second["ok"] is True
    assert second["result"] == 100
    assert result == final_response


@pytest.mark.parametrize(
    "first_name, first_args, recovery_args, injected_error, error_type, error_message, "
    "exact_message, question, answer, expected_result, handler_calls",
    [
        pytest.param(
            "unknown", {"operation": "multiply", "a": 12, "b": 8},
            {"operation": "add", "a": 96, "b": 4}, None,
            "ValueError", "not registered", False,
            "Use tool unknown and 96+4=?", "Unknown call_001,96+4=100", 100, 1,
            id="unknown-tool",
        ),
        pytest.param(
            "calculator", {"operation": "multiply", "a": "12", "b": 8},
            {"operation": "multiply", "a": 12, "b": 8}, None,
            "TypeError", "must be a number(integer or float)", False,
            "Use tool to calculate 12*8", "12*8=96", 96, 1,
            id="invalid-arguments",
        ),
        pytest.param(
            "calculator", {"operation": "multiply", "a": 12, "b": 8},
            {"operation": "multiply", "a": 12, "b": 8}, RuntimeError,
            "RuntimeError", "temporary tool failure", True,
            "Use tool to calculate 12*8", "12*8=96", 96, 2,
            id="tool-exception",
        ),
        pytest.param(
            "calculator", {"operation": "multiply", "a": 12, "b": 8},
            {"operation": "multiply", "a": 12, "b": 8}, TimeoutError,
            "TimeoutError", "tool execution timed out", True,
            "Use tool to calculate 12*8", "12*8=96", 96, 2,
            id="tool-reported-timeout",
        ),
    ],
)
def test_agent_recovers_after_tool_failure(
    first_name, first_args, recovery_args, injected_error, error_type, error_message,
    exact_message, question, answer, expected_result, handler_calls,
):
    calls = []

    def flaky_calculator(operation, a, b):
        calls.append({"operation": operation, "a": a, "b": b})
        if injected_error is not None and len(calls) == 1:
            raise injected_error(error_message)
        return calculator(operation, a, b)

    registry = ToolRegistry()
    registry.register(CALCULATOR_SCHEMA, flaky_calculator)
    final_response = {"role": "assistant", "content": answer}
    fake = FakeLLM([
        tool_response(tool_call("call_001", first_args, first_name)),
        tool_response(tool_call("call_002", recovery_args)),
        final_response,
    ])

    result = Agent(llm=fake, registry=registry).run(question)

    assert fake.message_history[0] == [{"role": "user", "content": question}]
    assert fake.call_count == 3
    second_input, third_input = fake.message_history[1:3]
    assert [msg["role"] for msg in second_input] == ["user", "assistant", "tool"]
    assert [msg["role"] for msg in third_input] == [
        "user", "assistant", "tool", "assistant", "tool",
    ]
    assert second_input[2]["tool_call_id"] == "call_001"
    assert third_input[4]["tool_call_id"] == "call_002"
    failed = json.loads(second_input[2]["content"])
    succeeded = json.loads(third_input[4]["content"])
    assert failed["ok"] is False
    assert "result" not in failed
    assert failed["error"]["type"] == error_type
    if exact_message:
        assert failed["error"]["message"] == error_message
    else:
        assert error_message in failed["error"]["message"]
    assert succeeded["ok"] is True
    assert succeeded["result"] == expected_result
    assert result == final_response
    # 校验失败不进入 handler；执行异常则进入两次。
    expected_calls = [recovery_args] if handler_calls == 1 else [first_args, recovery_args]
    assert calls == expected_calls


def test_agent_stops_at_max_steps(recorded_registry):
    registry, calls = recorded_registry
    arguments = {"operation": "multiply", "a": 12, "b": 8}
    fake = FakeLLM([
        tool_response(tool_call("call_001", arguments)),
        {"role": "assistant", "content": "12 × 8 = 96"},
    ])

    result = Agent(llm=fake, registry=registry, max_steps=1).run("Please the result of 12*8")

    assert result == {
        "status": "max_steps_reached",
        "answer": "已达到最大模型调用轮数，任务尚未完成。",
        "steps": 1,
    }
    assert calls == [arguments]
    assert fake.call_count == 1


def test_agent_returns_direct_answer_at_max_steps_1(recorded_registry):
    registry, calls = recorded_registry
    answer = {"role": "assistant", "content": "hello,12*8=96"}
    fake = FakeLLM([answer])

    result = Agent(llm=fake, registry=registry, max_steps=1).run("Please the result of 12*8")

    assert result == answer
    assert calls == []
    assert fake.call_count == 1


@pytest.mark.parametrize(
    "question, expected_error",
    [(123, TypeError), (None, TypeError), ("", ValueError), (" ", ValueError)],
    ids=["integer", "none", "empty", "whitespace"],
)
def test_agent_rejects_invalid_question(question, expected_error):
    fake = FakeLLM([])
    agent = Agent(llm=fake, registry=ToolRegistry())
    with pytest.raises(expected_error):
        agent.run(question)
    assert fake.call_count == 0


@pytest.mark.parametrize(
    "option, value, expected_error",
    [
        pytest.param("max_steps", True, TypeError, id="steps-true"),
        pytest.param("max_steps", False, TypeError, id="steps-false"),
        pytest.param("max_steps", "5", TypeError, id="steps-string"),
        pytest.param("max_steps", 1.5, TypeError, id="steps-float"),
        pytest.param("max_steps", None, TypeError, id="steps-none"),
        pytest.param("max_steps", 0, ValueError, id="steps-zero"),
        pytest.param("max_steps", -1, ValueError, id="steps-negative"),
        pytest.param("tool_timeout_seconds", True, TypeError, id="timeout-true"),
        pytest.param("tool_timeout_seconds", False, TypeError, id="timeout-false"),
        pytest.param("tool_timeout_seconds", "1", TypeError, id="timeout-string"),
        pytest.param("tool_timeout_seconds", 0, ValueError, id="timeout-zero"),
        pytest.param("tool_timeout_seconds", -1, ValueError, id="timeout-negative"),
        pytest.param("tool_timeout_seconds", float("nan"), ValueError, id="timeout-nan"),
        pytest.param("tool_timeout_seconds", float("inf"), ValueError, id="timeout-inf"),
        pytest.param("tool_timeout_seconds", float("-inf"), ValueError, id="timeout-neg-inf"),
        pytest.param("max_repeated_calls", True, TypeError, id="repeats-bool"),
        pytest.param("max_repeated_calls", 1.5, TypeError, id="repeats-float"),
        pytest.param("max_repeated_calls", 0, ValueError, id="repeats-zero"),
        pytest.param("max_repeated_calls", -1, ValueError, id="repeats-negative"),
    ],
)
def test_agent_rejects_invalid_configuration(option, value, expected_error):
    fake = FakeLLM([])
    with pytest.raises(expected_error):
        Agent(llm=fake, registry=ToolRegistry(), **{option: value})
    assert fake.call_count == 0
    assert fake.message_history == []


def test_agent_keeps_message_history_separate_between_runs(recorded_registry):
    registry, calls = recorded_registry
    arguments = {"operation": "multiply", "a": 12, "b": 8}
    answers = [
        {"role": "assistant", "content": "hello,12*8=96"},
        {"role": "assistant", "content": "again,12*8=96"},
    ]
    fake = FakeLLM([
        tool_response(tool_call("call_001", arguments)), answers[0],
        tool_response(tool_call("call_002", arguments)), answers[1],
    ])
    agent = Agent(llm=fake, registry=registry, max_steps=2, max_repeated_calls=1)

    assert agent.run("Please the result of 12*8") == answers[0]
    assert agent.run("Calculate 12*8 again") == answers[1]
    assert calls == [arguments, arguments]
    assert fake.call_count == 4
    assert fake.message_history[0] == [{"role": "user", "content": "Please the result of 12*8"}]
    assert fake.message_history[2] == [{"role": "user", "content": "Calculate 12*8 again"}]


@pytest.mark.parametrize(
    "operations, same_turn, expected_status, expected_steps, executed",
    [
        pytest.param(
            ["multiply"] * 3, False, "repeated_tool_call", 3, 2,
            id="repeated-across-rounds",
        ),
        pytest.param(
            ["multiply"] * 3, True, "repeated_tool_call", 1, 2,
            id="repeated-in-one-round",
        ),
        pytest.param(
            ["multiply", "multiply", "add", "multiply", "multiply"],
            False, None, 6, 5, id="different-call-resets-count",
        ),
        pytest.param(
            ["multiply", "add", "multiply", "add"],
            False, "max_steps_reached", 4, 4, id="alternating-loop-hits-step-budget",
        ),
    ],
)
def test_agent_stops_or_resets_repeated_calls(
    recorded_registry, operations, same_turn, expected_status, expected_steps, executed,
):
    registry, calls = recorded_registry
    requests = []
    for index, operation in enumerate(operations):
        # ID 每次变化、参数键顺序交替：两者都不能绕过重复检测。
        arguments = {"operation": operation, "a": 12, "b": 8}
        if index % 2:
            arguments = dict(reversed(list(arguments.items())))
        requests.append(tool_call(f"call_{index}", arguments))
    responses = (
        [tool_response(*requests)] if same_turn
        else [tool_response(request) for request in requests]
    )
    answer = {"role": "assistant", "content": "done"}
    fake = FakeLLM([*responses, answer])
    max_steps = expected_steps if expected_status == "max_steps_reached" else len(responses) + 1

    result = Agent(llm=fake, registry=registry, max_steps=max_steps).run("calculate")

    assert fake.call_count == expected_steps
    assert calls == [request["arguments"] for request in requests[:executed]]
    if expected_status is None:
        assert result == answer
    else:
        fallback = (
            "工具调用连续重复，已停止，任务尚未完成。"
            if expected_status == "repeated_tool_call"
            else "已达到最大模型调用轮数，任务尚未完成。"
        )
        assert result == {"status": expected_status, "answer": fallback, "steps": expected_steps}


def test_agent_recovers_after_blocked_tool_timeout():
    release = threading.Event()
    started = threading.Event()
    finished = threading.Event()
    calls = []

    def flaky_calculator(operation, a, b):
        calls.append({"operation": operation, "a": a, "b": b})
        if len(calls) == 1:
            started.set()
            try:
                release.wait()
                return calculator(operation, a, b)
            finally:
                finished.set()
        return calculator(operation, a, b)

    registry = ToolRegistry()
    registry.register(CALCULATOR_SCHEMA, flaky_calculator)
    arguments = {"operation": "multiply", "a": 12, "b": 8}
    answer = {"role": "assistant", "content": "12*8=96"}
    fake = FakeLLM([
        tool_response(tool_call("call_001", arguments)),
        tool_response(tool_call("call_002", arguments)), answer,
    ])
    agent = Agent(llm=fake, registry=registry, tool_timeout_seconds=0.05)
    try:
        assert agent.run("12*8=?") == answer
        failed_message = fake.message_history[1][2]
        succeeded_message = fake.message_history[2][4]
        failed = json.loads(failed_message["content"])
        succeeded = json.loads(succeeded_message["content"])
        assert failed_message["tool_call_id"] == "call_001"
        assert failed["ok"] is False
        assert "result" not in failed
        assert failed["error"]["type"] == "TimeoutError"
        assert succeeded_message["tool_call_id"] == "call_002"
        assert succeeded["ok"] is True
        assert succeeded["result"] == 96
        assert fake.call_count == 3
        assert calls == [arguments, arguments]
        assert started.is_set()
        assert not finished.is_set()
    finally:
        release.set()
        assert finished.wait(timeout=1), "后台工具未在清理期限内完成"


def test_execute_safe_returns_before_blocked_tool_finishes():
    started = threading.Event()
    release = threading.Event()
    finished = threading.Event()
    calls = []

    def blocking_calculator(operation, a, b):
        calls.append({"operation": operation, "a": a, "b": b})
        started.set()
        try:
            release.wait()
            return calculator(operation, a, b)
        finally:
            finished.set()

    registry = ToolRegistry()
    registry.register(CALCULATOR_SCHEMA, blocking_calculator)
    arguments = {"operation": "multiply", "a": 12, "b": 8}
    try:
        result = registry.execute_safe(tool_call("call_001", arguments), timeout_seconds=0.05)
        assert result["ok"] is False
        assert "result" not in result
        assert result["error"]["type"] == "TimeoutError"
        assert result["error"]["message"] == "tool execution timed out"
        assert result["tool_call_id"] == "call_001"
        assert result["name"] == "calculator"
        assert started.is_set()
        assert not release.is_set()
        assert not finished.is_set()
        assert calls == [arguments]
    finally:
        release.set()
        assert finished.wait(timeout=1), "后台工具未在清理期限内完成"


def test_execute_safe_preserves_tool_exception_with_timeout():
    calls = []

    def failing_calculator(operation, a, b):
        calls.append({"operation": operation, "a": a, "b": b})
        raise RuntimeError("temporary tool failure")

    registry = ToolRegistry()
    registry.register(CALCULATOR_SCHEMA, failing_calculator)
    arguments = {"operation": "multiply", "a": 12, "b": 8}
    result = registry.execute_safe(tool_call("call_001", arguments), timeout_seconds=1)
    assert result["ok"] is False
    assert "result" not in result
    assert result["error"]["type"] == "RuntimeError"
    assert result["error"]["message"] == "temporary tool failure"
    assert result["tool_call_id"] == "call_001"
    assert calls == [arguments]
