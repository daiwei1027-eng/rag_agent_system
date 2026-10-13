from __future__ import annotations
import shutil
import argparse
import json
from rag_agent_system.paths import resolve_project_path
from time import perf_counter
from pathlib import Path
from typing import Any
import hashlib
from collections import Counter
from rag_agent_system.agents.llm_client import LocalLLMClient
from rag_agent_system.agents.loop import Agent
from rag_agent_system.agents.prompts import build_agent_prompt
from rag_agent_system.config import load_config
from rag_agent_system.evaluation.benchmark import load_benchmark
from rag_agent_system.retrieval import CrossEncoderReranker, FaissRetriever
from rag_agent_system.tools.calculator_tool import calculator
from rag_agent_system.tools.registry import ToolRegistry
from rag_agent_system.tools.schemas import (
    CALCULATOR_SCHEMA,
    SEARCH_DOCUMENTS_SCHEMA,
    TIME_SCHEMA,
)
from copy import deepcopy
from datetime import timedelta,timezone,datetime
from rag_agent_system.tools.time_tool import get_current_time
def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        while block := f.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()

class HistoryClient:
    def __init__(self, client):
        self.client = client
        self.history = []

    def chat(self, messages, tools):
        self.history.append({
            "messages": deepcopy(messages),
            "tools": deepcopy(tools),
        })
        response = self.client.chat(messages, tools)
        return response
def load_cases(queries_path: Path) -> list[dict]:
    TARGET_IDS = (
    "q001", "q003", "q005", "q006", "q007", "q015",
    "q022", "q038", "q040", "q041", "q042", "q045",
)

    target_cases = []
    scored_queries = []
    excluded_queries = []
    query_ids = []
    with queries_path.open("r", encoding="utf-8-sig") as f:
        queries = [json.loads(line) for line in f if line.strip()]
    for item in queries:
        query_id=item["query_id"]
        if query_id in TARGET_IDS:
            if query_id in query_ids:
                raise ValueError(f"Duplicate query_id: {query_id}")
            target_cases.append(item)
            query_ids.append(query_id)
    missing_ids = set(TARGET_IDS) - set(query_ids)
    if missing_ids:
        raise ValueError(f"Missing query IDs: {sorted(missing_ids)}")

    target_cases.sort(
        key=lambda item: TARGET_IDS.index(item["query_id"])
    )
    for item in target_cases:
        answerable = item["answerable"]
        relevant_ids = item["relevant_chunk_ids"]
        if type(answerable) is not bool:
            raise ValueError("answerable must be a boolean")
        if answerable != bool(relevant_ids):
            raise ValueError(f"Inconsistent annotation: {item['query_id']}")
        if not answerable:
            excluded_queries.append({"query_id": item["query_id"], "excluded_reason": "unanswerable_no_relevant_ids"})
        else:
            scored_queries.append(item)
        if item["annotation_status"] != "reviewed":
            raise ValueError(f"Unreviewed query: {item['query_id']}")
    if len(scored_queries) != 9:
        raise ValueError("Scored queries must have exactly 9 queries.")
    if len(excluded_queries) != 3:
        raise ValueError("Excluded queries must have exactly 3 queries.")
    if len(target_cases) != 12:
        raise ValueError("Queries must have exactly 12 queries.")
    return target_cases



def build_agent(config, *, rerank_enabled: bool):
    reranker = None
    if rerank_enabled:
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
        output = []
        candidates = retriever.retrieve(query, top_k=config.retrieval.top_k)
        if reranker is not None:
            reranked_candidates = reranker.rerank(query=query,documents=candidates, top_k=top_k)
            for item in reranked_candidates[:top_k]:
                document = {
                    "chunk_id": item.chunk.chunk_id,
                    "text": item.chunk.text,
                    "score": float(item.score),
                    "source": item.chunk.source,
                    "rerank_score": (
                        float(item.rerank_score)
                        if item.rerank_score is not None else None
                    ),
                    "rerank_rank": item.rerank_rank,
                }
                output.append(document)
            return output
        else:
            for item in candidates[:top_k]:
                document = {
                    "chunk_id": item.chunk.chunk_id,
                    "text": item.chunk.text,
                    "score": float(item.score),
                    "source": item.chunk.source,
                    "rerank_score": (
                        float(item.rerank_score)
                        if item.rerank_score is not None else None
                    ),
                    "rerank_rank": item.rerank_rank,
                }
                output.append(document)
            return output

    registry = ToolRegistry()
    registry.register(SEARCH_DOCUMENTS_SCHEMA, search_handler)
    registry.register(TIME_SCHEMA, get_current_time)
    registry.register(CALCULATOR_SCHEMA, calculator)
    client = LocalLLMClient(
        config.agent.model_name,
        max_new_tokens=config.agent.max_new_tokens,
    )
    recorder = HistoryClient(client)
    agent = Agent(recorder, registry)
    return agent, client, retriever, reranker


def run_case(agent, item: dict) -> dict:
    """构造统一提示词，运行一题，记录完整结果、模型请求和耗时。"""
    query=item["query"]
    prompted_query=build_agent_prompt(query)
    agent.llm.history.clear()

    start = perf_counter()
    result = agent.run(prompted_query)
    cost_time = perf_counter() - start

    model_requests = deepcopy(agent.llm.history)
    return {
        "query_id": item["query_id"],
        "question": query,
        "prompt": prompted_query,
        "elapsed_seconds": cost_time,
        "result": result,
        "model_requests": model_requests,
    }


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Evaluate agent on the formal TinyStories benchmark.(improved prompts schema)")
    parser.add_argument("--config", default="configs/default.yaml", help="Config selecting one data/benchmark version.")
    parser.add_argument("--check-only", action="store_true", help="Validate inputs without loading models or creating a run.")
    parser.add_argument(
        "--run-dir", type=Path,
        help="New output directory; defaults to a timestamped directory under data/evaluation/stage2.",
    )
    args = parser.parse_args(argv)
    config = load_config(args.config)
    benchmark = load_benchmark(config)
    queries_path = benchmark["queries_path"]
    manifest_path = benchmark["manifest_path"]
    cases = load_cases(queries_path)
    if args.check_only:
        print(json.dumps({"benchmark_version": benchmark["manifest"]["version"],
                          "case_count": len(cases), "queries_path": str(queries_path),
                          "chunks_path": str(config.paths.chunks),
                          "faiss_index": str(config.paths.faiss_index)}, ensure_ascii=True, indent=2))
        return
    if args.run_dir is None:
        run_id = datetime.now(timezone(timedelta(hours=8))).strftime("%Y%m%d-%H%M%S-%f")
        args.run_dir = Path("data/evaluation/stage2") / f"{run_id}-agent-{benchmark['manifest']['version']}"
    run_dir = resolve_project_path(args.run_dir)
    run_dir.mkdir(parents=True, exist_ok=False)
    agent, client, retriever, reranker=build_agent(config,rerank_enabled=config.reranker.enabled)
    shutil.copy2(queries_path, run_dir / queries_path.name)
    shutil.copy2(manifest_path, run_dir / manifest_path.name)
    shutil.copy2(benchmark["absence_path"], run_dir / benchmark["absence_path"].name)
    with manifest_path.open("r", encoding="utf-8") as f:
        manifest = json.load(f)
    benchmark_version = manifest["version"]
    asset_hashes = {
        "queries": sha256_file(run_dir / queries_path.name),
        "manifest": sha256_file(run_dir / manifest_path.name),
        "faiss_index": sha256_file(config.paths.faiss_index),
        "chunks": sha256_file(config.paths.chunks),
        "absence_evidence": sha256_file(benchmark["absence_path"]),
    }

    if asset_hashes["queries"] != manifest["dataset_sha256"]:
        raise ValueError("Benchmark hash does not match manifest")
    all_queries = benchmark["queries"]
    warmup_item = next(
        item for item in all_queries
        if item["query_id"] == "q002"
    )
    start = perf_counter()
    retriever._load_resources()
    retriever_end = perf_counter()
    retriever_load_seconds = retriever_end - start
    if config.reranker.enabled:
        reranker._load_resources()
        reranker_end = perf_counter()
        reranker_load_seconds = reranker_end - retriever_end
    else:
        reranker_load_seconds = None
    client_start = perf_counter()
    client._load_resources()
    client_end = perf_counter()
    client_load_seconds = client_end - client_start
    warmup_record = run_case(agent, warmup_item)
    warm_up_seconds = warmup_record["elapsed_seconds"]
    with (run_dir / "warmup.json").open("w", encoding="utf-8") as f:
        json.dump(warmup_record, f, ensure_ascii=False, indent=2)
    all_results=[]
    for item in cases:
        record = run_case(agent, item)
        all_results.append(record)
    if not all_results:
        raise ValueError("No evaluation results")
    summary_record = {
        "case_count": len(all_results),
        "answerable_count": sum(item["answerable"] for item in cases),
        "unanswerable_count": sum(not item["answerable"] for item in cases),
        "rerank_enabled": config.reranker.enabled,
        "retriever_load_seconds": retriever_load_seconds,
        "reranker_load_seconds": reranker_load_seconds,
        "client_load_seconds": client_load_seconds,
        "warmup_query_id": warmup_item["query_id"],
        "warmup_seconds": warm_up_seconds,
        "status_counts": dict(Counter(record["result"]["status"] for record in all_results)),
    }
    json_path = run_dir / "per_query.json"
    print(json.dumps(summary_record, ensure_ascii=False, indent=2))
    json_path.parent.mkdir(parents=True, exist_ok=True)
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    summary_path = run_dir / "summary.json"
    with summary_path.open("w", encoding="utf-8") as f:
        json.dump(summary_record, f, ensure_ascii=False, indent=2)
    config_json = {"do_sample": False,
                   "Retrieved_top_k": config.retrieval.top_k,
                   "rerank_enabled": config.reranker.enabled,
                   "tokenizer and generation model": config.agent.model_name,
                   "Reranker": config.reranker.model_name,
                   "Retriever": config.retrieval.embedding_model,
                   "Max_Length": config.reranker.max_length,
                   "Batch_size": config.reranker.batch_size,
                   "Normalize_embeddings": config.retrieval.normalize_embeddings,
                   "max_new_tokens": config.agent.max_new_tokens,
                   "Faiss_Index_Path": str(config.paths.faiss_index),
                   "Data_Chunks_Path": str(config.paths.chunks),
                   "Query_count": len(all_results),
                   "Queries_path": str(queries_path),
                   "benchmark_version": benchmark_version,
                   "config_source": str(resolve_project_path(args.config)),
                   "asset_sha256": asset_hashes,
                   }
    config_path = run_dir / "config.json"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with config_path.open("w", encoding="utf-8") as f:
        json.dump(config_json, f, ensure_ascii=False, indent=2)

    print(f"Saved config to {config_path}")

if __name__ == "__main__":
    main()
