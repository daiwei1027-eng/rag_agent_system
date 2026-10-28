"""Locate q007/q038 evidence in FAISS candidates and their full reranking."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path
from time import perf_counter

from rag_agent_system.config import load_config
from rag_agent_system.paths import project_root


SOURCE_RUN = "20261013-100316-593488-agent-improved_v1_retrieval_top_k)"
SOURCE_CANDIDATE_TOP_K = 50
TARGETS = {"q007": "1500", "q038": "9250"}
CANDIDATE_TOP_K = 100
FINAL_TOP_K = 5


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        while block := f.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def load_inputs(source_dir: Path) -> tuple[list[dict], dict]:
    with (source_dir / "config.json").open(encoding="utf-8") as f:
        config = json.load(f)
    if config["Retrieved_top_k"] != SOURCE_CANDIDATE_TOP_K or not config["rerank_enabled"]:
        raise ValueError(f"Expected the saved rerank-enabled, top-{SOURCE_CANDIDATE_TOP_K} source run")
    with (source_dir / "per_query.json").open(encoding="utf-8") as f:
        records = json.load(f)
    cases = []
    for query_id, target_id in TARGETS.items():
        matches = [r for r in records if r["query_id"] == query_id]
        if len(matches) != 1:
            raise ValueError(f"Expected one saved record for {query_id}")
        record = matches[0]
        calls = [
            call for message in record["result"]["trace"]
            for call in message.get("tool_calls", [])
            if call["name"] == "search_documents"
        ]
        if len(calls) != 1 or calls[0]["arguments"]["top_k"] != FINAL_TOP_K:
            raise ValueError(f"Expected one top-5 search call for {query_id}")
        cases.append({
            "query_id": query_id,
            "question": record["question"],
            "query": calls[0]["arguments"]["query"],
            "target_chunk_id": target_id,
        })
    return cases, config


def serialize_documents(documents: list) -> list[dict]:
    return [
        {
            "chunk_id": item.chunk.chunk_id,
            "text": item.chunk.text,
            "source": item.chunk.source,
            "faiss_rank": item.rank,
            "score": float(item.score),
            "rerank_rank": item.rerank_rank,
            "rerank_score": float(item.rerank_score) if item.rerank_score is not None else None,
        }
        for item in documents
    ]


def diagnose_case(case: dict, retriever, reranker) -> dict:
    start = perf_counter()
    candidates = retriever.retrieve(case["query"], top_k=CANDIDATE_TOP_K)
    retrieved_at = perf_counter()
    # Keep all candidates so a target below the final top five remains visible.
    reranked = reranker.rerank(case["query"], candidates, top_k=CANDIDATE_TOP_K)
    finished_at = perf_counter()
    candidate_ids = [str(item.chunk.chunk_id) for item in candidates]
    reranked_ids = [str(item.chunk.chunk_id) for item in reranked]
    if len(candidate_ids) != CANDIDATE_TOP_K or len(set(candidate_ids)) != CANDIDATE_TOP_K:
        raise ValueError(f"Expected {CANDIDATE_TOP_K} unique FAISS candidates")
    if len(reranked_ids) != CANDIDATE_TOP_K or set(candidate_ids) != set(reranked_ids):
        raise ValueError("Reranking must preserve the full candidate set")
    target = case["target_chunk_id"]
    faiss_rank = candidate_ids.index(target) + 1 if target in candidate_ids else None
    rerank_rank = reranked_ids.index(target) + 1 if target in reranked_ids else None
    return {
        **case,
        "faiss_rank": faiss_rank,
        "rerank_rank": rerank_rank,
        "in_final_top_5": rerank_rank is not None and rerank_rank <= FINAL_TOP_K,
        "retrieval_seconds": retrieved_at - start,
        "rerank_seconds": finished_at - retrieved_at,
        "candidates": serialize_documents(candidates),
        "reranked": serialize_documents(reranked),
    }


def main() -> None:
    base = project_root() / "data/archive/evaluation/historical/stage2"
    source_dir = base / SOURCE_RUN
    cases, saved_config = load_inputs(source_dir)
    original_case = next(
        item for item in cases if item["query_id"] == "q007"
    )

    rewritten_case = {
        **original_case,
        "query_id": "q007_rewrite",
        "query": "Two children slid down the slide together and hugged after Max ran away.",
    }

    cases.append(rewritten_case)
    # Current config supplies portable asset paths; model settings come from the run.
    config = load_config()
    hashes = {
        "faiss_index": sha256_file(config.paths.faiss_index),
        "chunks": sha256_file(config.paths.chunks),
    }
    for key, digest in hashes.items():
        if digest != saved_config["asset_sha256"][key]:
            raise ValueError(f"Current {key} differs from the saved run")

    from rag_agent_system.retrieval import CrossEncoderReranker, FaissRetriever

    retriever = FaissRetriever(
        index_path=config.paths.faiss_index,
        chunks_path=config.paths.chunks,
        embedding_model=saved_config["Retriever"],
        normalize_embeddings=saved_config["Normalize_embeddings"],
    )
    reranker = CrossEncoderReranker(
        saved_config["Reranker"],
        max_length=saved_config["Max_Length"],
        batch_size=saved_config["Batch_size"],
    )
    run_id = datetime.now().astimezone().strftime("%Y%m%d-%H%M%S-%f")
    output_dir = project_root() / "data/local/diagnostics" / f"{run_id}-retrieval-diagnostic"
    output_dir.mkdir(parents=True, exist_ok=False)
    output_path = output_dir / "diagnostic.json"
    record = {
        "created_at": datetime.now().astimezone().isoformat(),
        "source_run": SOURCE_RUN,
        "source_records_sha256": sha256_file(source_dir / "per_query.json"),
        "source_config": saved_config,
        "asset_sha256": hashes,
        "candidate_top_k": CANDIDATE_TOP_K,
        "final_top_k": FINAL_TOP_K,
        "timing_note": "Model loading recorded separately; no inference warmup. First inference may include cold-start overhead. Diagnostic timings are not a performance comparison.",
        "cases": cases,
        "results": [],
    }

    def save() -> None:
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(record, f, ensure_ascii=False, indent=2)

    save()
    start = perf_counter()
    retriever._load_resources()
    loaded_at = perf_counter()
    reranker._load_resources()
    record["retriever_load_seconds"] = loaded_at - start
    record["reranker_load_seconds"] = perf_counter() - loaded_at
    save()
    print("query_id | target_chunk | FAISS rank | rerank rank | in top 5")
    for case in cases:
        result = diagnose_case(case, retriever, reranker)
        record["results"].append(result)
        save()
        print(f"{case['query_id']} | {case['target_chunk_id']} | "
              f"{result['faiss_rank']} | {result['rerank_rank']} | {result['in_final_top_5']}")
    print(f"None means the target was not found among the {CANDIDATE_TOP_K} candidates.")
    print(f"Saved diagnostic to {output_path}")


if __name__ == "__main__":
    main()
