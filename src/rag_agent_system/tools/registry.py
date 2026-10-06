from typing import Any, Callable
from rag_agent_system.tools.validation import validate_arguments

class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, dict[str, Any]] = {}
    def register(
        self,
        schema: dict[str, Any],
        handler: Callable[..., Any],
    ) -> None:
        name = schema["name"]
        if name in self._tools:
            raise ValueError(f"Tool '{name}' is already registered")
        if not callable(handler):
            raise TypeError(f"Handler for tool '{name}' must be callable")
        self._tools[name] = {"schema": schema, "handler": handler}
    def get_schemas(self) -> list[dict[str, Any]]:
        schemas = []
        for tool in self._tools.values():
            schemas.append(tool["schema"])
        return schemas

    def execute(self, tool_call: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(tool_call, dict):
            raise TypeError("Tool call must be a dict")

        for field in ("id", "name", "arguments"):
            if field not in tool_call:
                raise ValueError(f"Missing tool call field: {field}")

        if not isinstance(tool_call["arguments"], dict):
            raise TypeError("Arguments for tool must be a dict")
        if not (
                isinstance(tool_call["name"], str)
                and isinstance(tool_call["id"], str)
        ):
            raise TypeError("Id and Name must be strings")
        if not (tool_call["id"].strip() and tool_call["name"].strip()):
            raise ValueError("Id and Name must not be empty")
        tool_call_name=tool_call["name"]
        if tool_call_name not in self._tools:
            raise ValueError(f"Tool '{tool_call_name}' is not registered")
        schema = self._tools[tool_call_name]["schema"]
        handler = self._tools[tool_call_name]["handler"]
        arguments = tool_call["arguments"]
        validate_arguments(arguments, schema["parameters"])
        result = handler(**arguments)
        target={
            "tool_call_id":tool_call["id"],
            "name":tool_call["name"],
            "ok":True,
            "result":result,
        }
        return target

    def execute_safe(self, tool_call: dict[str, Any]) -> dict[str, Any]:
        try :
            return self.execute(tool_call)
        except (TypeError, ValueError) as exc:
            return {
                "tool_call_id": tool_call.get("id") if isinstance(tool_call, dict) else None,
                "name": tool_call.get("name") if isinstance(tool_call, dict) else None,
                "ok": False,
                "error": {
                    "type": type(exc).__name__,
                    "message": str(exc),
                },
            }