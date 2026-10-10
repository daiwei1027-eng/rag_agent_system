from typing import Any, Protocol
from rag_agent_system.tools.registry import ToolRegistry
import json
from rag_agent_system.agents.models import AgentResult
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
        max_repeated_calls: int = 2,
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
    def run(self, question: str) -> AgentResult:
        if not isinstance(question, str):
            raise TypeError("question should be a string")
        if not question.strip():
            raise ValueError("question should not be empty")

        messages = [
            {"role": "user", "content": question},
        ]
        schemas = self.registry.get_schemas()
        last_call_signature = None
        repeated_calls = 0
        for step in range(self.max_steps):
            try:
                response = self.llm.chat(messages, schemas)
            except ValueError as e:
                return {
                    "status": "model_error",
                    "answer": "",
                    "trace": messages,
                    "error": str(e),
                }
            if not isinstance(response, dict):
                return {
                    "status": "model_error",
                    "answer": "",
                    "trace": messages,
                    "error": "Response is not a dict",
                }
            if response.get("role") != "assistant":
                return {
                    "status": "model_error",
                    "answer": "",
                    "trace": messages,
                    "error": "Role is not 'assistant'",
                }
            messages.append(response)
            tool_calls = response.get("tool_calls")
            if tool_calls is not None and not isinstance(tool_calls, list):
                return {
                    "status": "model_error",
                    "answer": "",
                    "trace": messages,
                    "error": "tool_calls is not a list",
                }
            if not tool_calls:
                content = response.get("content")
                if not isinstance(content, str) or not content.strip():
                    return {
                        "status": "model_error",
                        "answer": "",
                        "trace": messages,
                        "error": "Content must be a non-empty string without tool calls",
                    }
                return {
                    "status": "completed",
                    "answer": content,
                    "trace": messages,
                    "error": None,
                }

            for tool_call in tool_calls:
                if not isinstance(tool_call, dict):
                    return {
                        "status": "model_error",
                        "answer": "",
                        "trace": messages,
                        "error": "Tool call is not dict"
                    }
                for field in ("id", "name", "arguments"):
                    if field not in tool_call:
                        return {
                            "status": "model_error",
                            "answer": "",
                            "trace": messages,
                            "error": f"{field} Missing"
                        }
                if not isinstance(tool_call["arguments"], dict):
                    return {
                        "status": "model_error",
                        "answer": "",
                        "trace": messages,
                        "error": "ID->str,name->str,arguments->dict"
                    }
                if not (
                        isinstance(tool_call["name"], str)
                        and isinstance(tool_call["id"], str)
                ):
                    return {
                        "status": "model_error",
                        "answer": "",
                        "trace": messages,
                        "error": "ID->str,name->str,arguments->dict"
                    }
                if not (tool_call["id"].strip() and tool_call["name"].strip()):
                    return {
                        "status": "model_error",
                        "answer": "",
                        "trace": messages,
                        "error": "ID or name is empty"
                    }
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
                        "answer": "",
                        "trace": messages,
                        "error": "重复工具调用达到上限",
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
            "answer": "",
            "trace": messages,
            "error": "抵达最大步数",
        }
