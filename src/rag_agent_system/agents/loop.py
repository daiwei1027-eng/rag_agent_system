from typing import Any, Protocol
from rag_agent_system.tools.calculator_tool import calculator
from rag_agent_system.tools.schemas import CALCULATOR_SCHEMA
from rag_agent_system.tools.registry import ToolRegistry
import json
from copy import deepcopy
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
    ) -> None:
        if type(max_steps) is not int:
            raise TypeError("max_steps should be an integer")
        if max_steps <= 0:
            raise ValueError("max_steps should be a positive integer")
        self.max_steps = max_steps
        self.llm = llm
        self.registry = registry

    def run(self, question: str) -> dict[str, Any]:
        if not isinstance(question, str):
            raise TypeError("question should be a string")
        if not question.strip():
            raise ValueError("question should not be empty")
        # 格式：{"role": "user", "content": question}
        messages = [
            {"role": "user", "content": question},
        ]
        schemas=self.registry.get_schemas()
        for step in range(self.max_steps):
            response=self.llm.chat(messages, schemas)
            messages.append(response)
            if not response.get("tool_calls"):
                return response
            for tool_call in response["tool_calls"]:
                observation=self.registry.execute_safe(tool_call)
                messages.append({
    "role": "tool",
    "tool_call_id": observation["tool_call_id"],
    "content": json.dumps(observation, ensure_ascii=False),
})

        return {
                        "status": "max_steps_reached",
                        "answer": None,
                        "steps": self.max_steps,
                    }
