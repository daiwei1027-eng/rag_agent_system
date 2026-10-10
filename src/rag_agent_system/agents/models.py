"""Public result contract for one Agent.run() invocation."""

from typing import Any, Literal, TypedDict


AgentStatus = Literal[
    "completed",
    "repeated_tool_call",
    "max_steps_reached",
    "model_error",
]


class AgentResult(TypedDict):
    status: AgentStatus
    answer: str
    trace: list[dict[str, Any]]  # Full messages, including serialized tool observations.
    error: str | None  # Task-level error; None for a completed run.
