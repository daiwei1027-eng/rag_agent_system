import argparse
import json
from pathlib import Path
import csv
from rag_agent_system.config import load_config
from rag_agent_system.evaluation.benchmark import load_benchmark
from rag_agent_system.evaluation.metrics import (
    recall_at_k,
    hit_rate_at_k,
    reciprocal_rank,
)
from rag_agent_system.retrieval.faiss_retriever import FaissRetriever
from rag_agent_system.retrieval.reranker import CrossEncoderReranker
from rag_agent_system.paths import resolve_project_path
import shutil
from time import perf_counter
import hashlib
from datetime import datetime, timedelta, timezone

def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        while block := f.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evaluate retrieval on the formal TinyStories benchmark.")
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
    queries = benchmark["queries"]
    if args.check_only:
        print(json.dumps({"benchmark_version": benchmark["manifest"]["version"],
                          "query_count": len(queries), "queries_path": str(queries_path),
                          "chunks_path": str(config.paths.chunks),
                          "faiss_index": str(config.paths.faiss_index)}, ensure_ascii=True, indent=2))
        return 0
    if args.run_dir is None:
        run_id = datetime.now(timezone(timedelta(hours=8))).strftime("%Y%m%d-%H%M%S-%f")
        args.run_dir = Path("data/evaluation/stage2") / f"{run_id}-retrieval-{benchmark['manifest']['version']}"
    run_dir = resolve_project_path(args.run_dir)
    run_dir.mkdir(parents=True, exist_ok=False)

    retriever = FaissRetriever(
        index_path=config.paths.faiss_index,
        chunks_path=config.paths.chunks,
        embedding_model=config.retrieval.embedding_model,
        normalize_embeddings=config.retrieval.normalize_embeddings,
    )

    reranker = CrossEncoderReranker(
        model_name=config.reranker.model_name,
        max_length=config.reranker.max_length,
        batch_size=config.reranker.batch_size,
    )

    all_results = []
    json_path = run_dir / "per_query.json"
    scored_queries=[]
    excluded_queries=[]
    query_ids=[]

    for item in queries:
        query = item["query"]
        if item["query_id"] in query_ids:
            raise ValueError("Query ids must be unique.")
        else:
            query_ids.append(item["query_id"])
        answerable = item["answerable"]
        relevant_ids = item["relevant_chunk_ids"]
        if type(answerable) is not bool:
            raise ValueError("answerable must be a boolean")
        if answerable != bool(relevant_ids):
            raise ValueError(f"Inconsistent annotation: {item['query_id']}")
        if not answerable:
            excluded_queries.append({"query_id": item["query_id"],"excluded_reason":"unanswerable_no_relevant_ids"})
        else:
            scored_queries.append(item)
        if item["annotation_status"] != "reviewed":
            raise ValueError(f"Unreviewed query: {item['query_id']}")
    if len(scored_queries) != 40:
        raise ValueError("Scored queries must have exactly 40 queries.")
    if len(excluded_queries) != 5:
        raise ValueError("Excluded queries must have exactly 5 queries.")
    if len(queries) != 45:
        raise ValueError("Queries must have exactly 45 queries.")
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
    start = perf_counter()
    retriever._load_resources()
    retriever_end = perf_counter()
    retriever_load_seconds = retriever_end - start
    reranker._load_resources()
    reranker_end = perf_counter()
    reranker_load_seconds = reranker_end - retriever_end
    warmup_item = next(
        item for item in queries if item["query_id"] == "q002"
    )
    retrieved_warm_up_chunks=retriever.retrieve(warmup_item["query"],top_k=20)
    rerank_warm_up_chunk=reranker.rerank(warmup_item["query"],retrieved_warm_up_chunks,top_k=20)
    warm_up_end = perf_counter()
    warm_up_seconds = warm_up_end - reranker_end
    for item in scored_queries:
        query = item["query"]
        relevant_ids = set(item["relevant_chunk_ids"])
        start = perf_counter()
        candidates = retriever.retrieve(query, top_k=20)
        retrieval_end_time = perf_counter()
        retrieval_time = retrieval_end_time - start
        reranked = reranker.rerank(query, candidates, top_k=20)
        rerank_end_time = perf_counter()
        rerank_time = rerank_end_time - retrieval_end_time
        baseline_ids = [result.chunk.chunk_id for result in candidates]
        reranked_ids = [result.chunk.chunk_id for result in reranked]

        # TODO：分别计算两组 Recall@1/3/5、HitRate@5、RR@20
        # TODO：保存 query_id、两组排序 ID 和逐问题指标
        with_rerank_recall_1=recall_at_k(reranked_ids,relevant_ids,1)
        with_rerank_recall_3 = recall_at_k(reranked_ids, relevant_ids, 3)
        with_rerank_recall_5 = recall_at_k(reranked_ids, relevant_ids, 5)
        with_rerank_hit_5 = hit_rate_at_k(reranked_ids, relevant_ids, 5)
        with_rerank_relevance = [chunk_id in relevant_ids for chunk_id in reranked_ids[:20]]
        with_rr_20 = reciprocal_rank(with_rerank_relevance)
        without_rerank_recall_1 = recall_at_k(baseline_ids, relevant_ids, 1)
        without_rerank_recall_3 = recall_at_k(baseline_ids, relevant_ids, 3)
        without_rerank_recall_5 = recall_at_k(baseline_ids, relevant_ids, 5)
        without_rerank_hit_5 = hit_rate_at_k(baseline_ids, relevant_ids, 5)
        without_rerank_relevance = [chunk_id in relevant_ids for chunk_id in baseline_ids[:20]]
        without_rr_20 = reciprocal_rank(without_rerank_relevance)
        experiments={
            "With Rerank":{"recall_1":with_rerank_recall_1,
                           "recall_3": with_rerank_recall_3,
                           "recall_5": with_rerank_recall_5,
                           "hit_5": with_rerank_hit_5,
                           "rr_at_20": with_rr_20,
                           "retrieval_seconds":retrieval_time,
                           "rerank_seconds":rerank_time,
                           }
            ,"Without Rerank":{"recall_1":without_rerank_recall_1,
                           "recall_3": without_rerank_recall_3,
                           "recall_5": without_rerank_recall_5,
                           "hit_5": without_rerank_hit_5,
                           "rr_at_20": without_rr_20,
                           "retrieval_seconds": retrieval_time,
                           "rerank_seconds": None,
                           }
        }
        all_results.append({
            "query_id": item["query_id"],
            "query": query,
            "relevant_chunk_ids": sorted(relevant_ids),
            "baseline_ids": baseline_ids,
            "reranked_ids": reranked_ids,
            "metrics": experiments,
        })
    if not all_results:
        raise ValueError("No evaluation results")


    summary = {}

    for run in ("Without Rerank", "With Rerank"):
        summary[run] = {}

        for metric in ("recall_1", "recall_3", "recall_5", "hit_5", "rr_at_20"):
            average = sum(
                result["metrics"][run][metric]
                for result in all_results
            ) / len(all_results)

            name = "mrr_at_20" if metric == "rr_at_20" else metric
            summary[run][name] = average
    summary_record={
        "scored_count":len(all_results),
        "excluded_count":len(excluded_queries),
        "retriever_load_seconds":retriever_load_seconds,
        "reranker_load_seconds":reranker_load_seconds,
    "warmup_query_id": warmup_item["query_id"],
    "warmup_seconds": warm_up_seconds,
        "metrics":summary,
    }
    print(json.dumps(summary_record, ensure_ascii=False, indent=2))
    json_path.parent.mkdir(parents=True, exist_ok=True)
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    summary_path = run_dir / "summary.json"
    with summary_path.open("w", encoding="utf-8") as f:
        json.dump(summary_record, f, ensure_ascii=False, indent=2)
    csv_path = run_dir / "total.csv"
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    config_json={"Temperature":config.generation.temperature,
                       "Retrieved_top_k":20,
                       "Rerank_top_k":20,
                       "Context_top_k":config.context.top_k,
                       "tokenizer and generation model":config.generation.model_name,
                       "Reranker":config.reranker.model_name,
                       "Retriever":config.retrieval.embedding_model,
                       "Max_Length":config.reranker.max_length,
                       "Batch_size":config.reranker.batch_size,
                       "Normalize_embeddings":config.retrieval.normalize_embeddings,
                       "max_new_tokens":config.generation.max_new_tokens,
                       "Faiss_Index_Path":str(config.paths.faiss_index),
                       "Data_Chunks_Path":str(config.paths.chunks),
    "Query_count": len(all_results),
    "Queries_path": str(queries_path),
                 "benchmark_version":benchmark_version,
                 "config_source": str(resolve_project_path(args.config)),
    "asset_sha256": asset_hashes,
                       }
    config_path = run_dir / "config.json"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    excluded_path = run_dir / "excluded_queries.json"
    with excluded_path.open("w", encoding="utf-8") as f:
        json.dump(excluded_queries, f, ensure_ascii=False, indent=2)
    with config_path.open("w", encoding="utf-8") as f:
        json.dump(config_json, f, ensure_ascii=False, indent=2)

    print(f"Saved config to {config_path}")
    with csv_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "run",
                "recall_1",
                "recall_3",
                "recall_5",
                "hit_5",
                "mrr_at_20",
            ],
        )

        writer.writeheader()

        for run, metrics in summary.items():
            writer.writerow({
                "run": run,
                **metrics,
            })
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
