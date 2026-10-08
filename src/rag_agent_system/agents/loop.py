from typing import Any, Protocol
from rag_agent_system.tools.calculator_tool import calculator
from rag_agent_system.tools.schemas import CALCULATOR_SCHEMA
from rag_agent_system.tools.registry import ToolRegistry
import json
from copy import deepcopy
import math
class LLMClient(Protocol):
    def chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
    ) -> dict[str, Any]:
        ...


class Agent:
    def __init__(
        self,
        llm: LLMClient,
        registry: ToolRegistry,
        max_steps: int = 5,
        *,
        tool_timeout_seconds: float | None = None,
        max_repeated_calls: int = 2
    ) -> None:
        if type(max_steps) is not int:
            raise TypeError("max_steps should be an integer")
        if max_steps <= 0:
            raise ValueError("max_steps should be a positive integer")
        self.max_steps = max_steps
        self.llm = llm
        self.registry = registry
        if tool_timeout_seconds is not None:
            if type(tool_timeout_seconds) not in (int, float):
                raise TypeError("tool_timeout_seconds should be a number")
            if not math.isfinite(tool_timeout_seconds):
                raise ValueError("tool_timeout_seconds should be finite")
            if tool_timeout_seconds <= 0:
                raise ValueError("tool_timeout_seconds should be positive")
        if type(max_repeated_calls) is not int:
            raise TypeError("max_repeated_calls should be an integer")
        if max_repeated_calls <= 0:
            raise ValueError("max_repeated_calls should be positive")
        self.tool_timeout_seconds = tool_timeout_seconds
        self.max_repeated_calls = max_repeated_calls
    def run(self, question: str) -> dict[str, Any]:
        if not isinstance(question, str):
            raise TypeError("question should be a string")
        if not question.strip():
            raise ValueError("question should not be empty")

        messages = [
            {"role": "user", "content": question},
        ]
        schemas=self.registry.get_schemas()
        last_call_signature=None
        repeated_calls=0
        for step in range(self.max_steps):
            response = self.llm.chat(messages, schemas)
            messages.append(response)
            if not response.get("tool_calls"):
                return response

            for tool_call in response["tool_calls"]:
                signature = (
                    tool_call["name"],
                    json.dumps(tool_call["arguments"], sort_keys=True, ensure_ascii=False),
                )
                if last_call_signature == signature:
                    repeated_calls += 1
                else:
                    last_call_signature = signature
                    repeated_calls = 1

                if repeated_calls > self.max_repeated_calls:
                    return {
                        "status": "repeated_tool_call",
                        "answer": "工具调用连续重复，已停止，任务尚未完成。",
                        "steps": step + 1,
                    }
                observation = self.registry.execute_safe(
                    tool_call,
                    timeout_seconds=self.tool_timeout_seconds,
                )
                messages.append({
                    "role": "tool",
                    "tool_call_id": observation["tool_call_id"],
                    "content": json.dumps(observation, ensure_ascii=False),
                })

        return {
            "status": "max_steps_reached",
            "answer": "已达到最大模型调用轮数，任务尚未完成。",
            "steps": self.max_steps,
        }
