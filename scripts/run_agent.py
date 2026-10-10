"""Run one local Qwen Agent round trip with the calculator tool."""

from rag_agent_system.agents.llm_client import LocalLLMClient
from rag_agent_system.agents.loop import Agent
from rag_agent_system.config import load_config
from rag_agent_system.tools.calculator_tool import calculator
from rag_agent_system.tools.registry import ToolRegistry
from rag_agent_system.tools.schemas import CALCULATOR_SCHEMA


def main() -> None:
    config = load_config()
    history = []
    question = "请使用 calculator 计算 12 × 8，并根据工具结果回答。"
    client = LocalLLMClient(config.agent.model_name,max_new_tokens=config.agent.max_new_tokens)
    registry = ToolRegistry()
    def history_calculator(operation, a, b):
        result = calculator(operation, a, b)
        history.append({"operation": operation, "a": a, "b": b, "result": result})
        return result

    registry.register(CALCULATOR_SCHEMA,history_calculator)
    agent=Agent(client,registry)
    result=agent.run(question)
    assert result["status"] == "completed"
    trace=result["trace"]
    for message in trace:
        print(message)
    print(trace)
if __name__ == "__main__":
    main()
