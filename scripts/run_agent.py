"""Run and optionally record representative local Qwen Agent scenarios."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from rag_agent_system.agents.llm_client import LocalLLMClient
from rag_agent_system.agents.loop import Agent
from rag_agent_system.agents.models import AgentResult
from rag_agent_system.config import AppConfig, load_config
from rag_agent_system.paths import project_root
from rag_agent_system.retrieval import CrossEncoderReranker, FaissRetriever
from rag_agent_system.tools.calculator_tool import calculator
from rag_agent_system.tools.registry import ToolRegistry
from rag_agent_system.tools.schemas import (
    CALCULATOR_SCHEMA,
    SEARCH_DOCUMENTS_SCHEMA,
    TIME_SCHEMA,
)
from rag_agent_system.tools.search_docments import search_documents
from rag_agent_system.tools.time_tool import get_current_time


SCENARIOS = {
    "direct": "水的化学式是什么？",
    "tinystories": (
        "请调用 search_documents 检索 TinyStories，top_k 为 3。"
        "仅根据工具返回的文段回答问题，最终回答必须恰好两行：\n"
        "第一行以“答案：”开头，写人物名字。\n"
        "第二行以“依据：chunk_id=”开头，写直接支持答案的文段编号；"
        "编号必须来自工具结果。\n"
        "如果没有直接证据，改为输出“答案：证据不足”和“依据：无”。\n"
        "Who found a needle in her room and wanted her mother to sew a button on her shirt?"
    ),
    "tinystories_auto": (
        "请回答 TinyStories 资料库中的问题，并给出支持答案的 chunk_id。"
        "如需检索，请只提出一次简短的英文查询，然后根据返回的文段回答；"
        "找不到证据就说明证据不足。\n"
        "Who found a needle in her room and wanted her mother "
        "to sew a button on her shirt?"
    ),
    "calculator": "请使用 calculator 计算 12 × 8，并根据工具结果回答。",
    "time": "请调用 time 查询 Asia/Shanghai 当前时间，并根据工具结果回答。",
    "multi_tool": (
        "请调用 time 查询 Asia/Shanghai 当前时间，并调用 calculator 计算 12 × 8；"
        "读取两个工具的结果后，同时给出时间和计算结果。"
    ),
    "tool_failure": (
        "请调用 calculator 计算 12 ÷ 0，并根据工具结果回答；"
        "如果工具报错，请说明错误，不要编造数值。"
    ),
}


def _json_default(value: Any) -> str:
    if isinstance(value, Path):
        return str(value)
    raise TypeError(f"Cannot serialize {type(value).__name__}")


def save_run_record(
    path: Path,
    *,
    scenario: str,
    question: str,
    config: AppConfig,
    agent: Agent,
    tool_schemas: list[dict[str, Any]],
    result: AgentResult,
) -> None:
    """Save the result plus exact message/tool inputs for each model call."""
    trace = result["trace"]
    record = {
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        "scenario": scenario,
        "question": question,
        "config": asdict(config),
        "agent_runtime": {
            "max_steps": agent.max_steps,
            "max_repeated_calls": agent.max_repeated_calls,
            "tool_timeout_seconds": agent.tool_timeout_seconds,
        },
        "tool_schemas": tool_schemas,
        "model_requests": [
            {
                "response_trace_index": index,
                "messages": trace[:index],
                "tools": tool_schemas,
            }
            for index, message in enumerate(trace)
            if message.get("role") == "assistant"
        ],
        "result": result,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = path.with_suffix(path.suffix + ".tmp")
    temporary_path.write_text(
        json.dumps(record, ensure_ascii=False, indent=2, default=_json_default) + "\n",
        encoding="utf-8",
    )
    temporary_path.replace(path)


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="backslashreplace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", choices=SCENARIOS, default="tool_failure")
    parser.add_argument("--all", action="store_true", help="Run all scenarios.")
    parser.add_argument(
        "--record-dir",
        type=Path,
        help="Save one JSON record per scenario in this directory.",
    )
    args = parser.parse_args(argv)
    if args.all and args.record_dir is None:
        parser.error("--all requires --record-dir")

    config = load_config()
    reranker = None
    if config.reranker.enabled:
        reranker = CrossEncoderReranker(
            config.reranker.model_name,
            max_length=config.reranker.max_length,
            batch_size=config.reranker.batch_size,
        )
    retriever = FaissRetriever(
        index_path=config.paths.faiss_index,
        chunks_path=config.paths.chunks,
        embedding_model=config.retrieval.embedding_model,
        normalize_embeddings=config.retrieval.normalize_embeddings,
    )

    def search_handler(query: str, top_k: int) -> list[dict[str, Any]]:
        return search_documents(
            query,
            top_k,
            retriever=retriever,
            reranker=reranker,
            candidate_top_k=config.retrieval.top_k,
        )

    registry = ToolRegistry()
    registry.register(SEARCH_DOCUMENTS_SCHEMA, search_handler)
    registry.register(TIME_SCHEMA, get_current_time)
    registry.register(CALCULATOR_SCHEMA, calculator)
    client = LocalLLMClient(
        config.agent.model_name,
        max_new_tokens=config.agent.max_new_tokens,
    )
    agent = Agent(client, registry)

    record_dir = args.record_dir
    if record_dir is not None and not record_dir.is_absolute():
        record_dir = project_root() / record_dir

    selected = SCENARIOS if args.all else {args.scenario: SCENARIOS[args.scenario]}
    all_completed = True
    for scenario, question in selected.items():
        result = agent.run(question)
        if record_dir is not None:
            record_path = record_dir / f"{scenario}.json"
            save_run_record(
                record_path,
                scenario=scenario,
                question=question,
                config=config,
                agent=agent,
                tool_schemas=registry.get_schemas(),
                result=result,
            )
        print(f"[{scenario}] status={result['status']} answer={result['answer']}")
        if not args.all:
            for message in result["trace"]:
                print(message)
        if record_dir is not None:
            print(f"Record: {record_path}")
        all_completed &= result["status"] == "completed"

    return 0 if all_completed else 1


if __name__ == "__main__":
    raise SystemExit(main())
