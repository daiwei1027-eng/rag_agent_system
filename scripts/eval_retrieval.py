"""Evaluate a version-bound retrieval benchmark with optional reranking."""

import argparse
import csv
import json
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path
from time import perf_counter

from rag_agent_system.config import load_config
from rag_agent_system.evaluation.benchmark import load_benchmark, sha256_file
from rag_agent_system.evaluation.metrics import hit_rate_at_k, recall_at_k, reciprocal_rank
from rag_agent_system.paths import resolve_project_path
from rag_agent_system.retrieval.faiss_retriever import DocumentRetriever
from rag_agent_system.retrieval.reranker import CrossEncoderReranker

METRIC_NAMES = ("recall_1", "recall_3", "recall_5", "hit_5", "rr_at_20")


def write_json(path: Path, value) -> None:
    """Replace a checkpoint only after its new JSON has been fully written."""
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def score_ranking(ids: list[str], relevant: set[str], *,
                  retrieval_seconds: float, rerank_seconds: float | None) -> dict:
    return {
        **{f"recall_{k}": recall_at_k(ids, relevant, k) for k in (1, 3, 5)},
        "hit_5": hit_rate_at_k(ids, relevant, 5),
        "rr_at_20": reciprocal_rank([chunk_id in relevant for chunk_id in ids[:20]]),
        "retrieval_seconds": retrieval_seconds,
        "rerank_seconds": rerank_seconds,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/SEC_v1.yaml",
                        help="Config selecting one benchmark and its retrieval assets.")
    parser.add_argument("--check-only", action="store_true",
                        help="Validate inputs without constructing models or creating a run.")
    parser.add_argument("--run-dir", type=Path, help="New output directory; never overwritten.")
    parser.add_argument("--candidate-top-k", type=int, default=20,
                        help="Evaluation candidate budget; default 20 preserves the historical protocol.")
    args = parser.parse_args(argv)
    if args.candidate_top_k <= 0:
        parser.error("--candidate-top-k must be a positive integer")
    config = load_config(args.config)
    benchmark = load_benchmark(config)
    manifest = benchmark["manifest"]
    queries = benchmark["queries"]
    # The loader already checks manifest counts, annotations, quotes and asset bindings.
    scored_queries = [item for item in queries if item["answerable"]]
    excluded_queries = [
        {"query_id": item["query_id"], "excluded_reason": "unanswerable_no_relevant_ids"}
        for item in queries if not item["answerable"]
    ]
    if not scored_queries:
        raise ValueError("No answerable queries available for retrieval evaluation")
    warmup_item = scored_queries[0]
    if args.check_only:
        print(json.dumps({
            "benchmark_version": manifest["version"], "query_count": len(queries),
            "scored_count": len(scored_queries), "excluded_count": len(excluded_queries),
            "queries_path": str(benchmark["queries_path"]),
            "chunks_path": str(config.paths.chunks), "faiss_index": str(config.paths.faiss_index),
            "retrieval_mode": config.retrieval.mode, "reranker_enabled": config.reranker.enabled,
            "candidate_top_k": args.candidate_top_k, "warmup_query_id": warmup_item["query_id"],
        }, ensure_ascii=False, indent=2))
        return 0

    inputs = {
        "queries": benchmark["queries_path"], "manifest": benchmark["manifest_path"],
        "absence_evidence": benchmark["absence_path"],
    }
    asset_paths = {**inputs, "faiss_index": config.paths.faiss_index, "chunks": config.paths.chunks}
    asset_hashes = {name: sha256_file(path) for name, path in asset_paths.items()}
    if asset_hashes["queries"] != manifest["dataset_sha256"]:
        raise ValueError("Benchmark changed after validation")
    if json.loads(inputs["manifest"].read_text(encoding="utf-8-sig")) != manifest:
        raise ValueError("Benchmark manifest changed after validation")
    for name, expected in manifest.get("asset_binding", {}).items():
        if name in asset_hashes and asset_hashes[name] != expected:
            raise ValueError(f"Benchmark asset changed after validation: {name}")
    names = [path.name for path in inputs.values()]
    reserved = {"config.json", "per_query.json", "summary.json", "excluded_queries.json",
                "run_status.json", "failure.json", "total.csv"}
    if len(set(names)) != len(names) or set(names) & reserved:
        raise ValueError("Benchmark input filenames collide with run artifacts")
    if args.run_dir is None:
        run_id = datetime.now(timezone(timedelta(hours=8))).strftime("%Y%m%d-%H%M%S-%f")
        dataset = "sec" if manifest["version"].startswith("sec-") else "tinystories"
        split = manifest.get("split")
        group = split if dataset == "sec" and split in {"dev", "test"} else "retrieval"
        variant = config.retrieval.mode + ("-rerank" if config.reranker.enabled else "")
        args.run_dir = (Path("data/evaluation") / dataset / group
                        / f"{run_id}-{variant}-retrieval-{manifest['version']}")
    run_dir = resolve_project_path(args.run_dir)
    run_dir.mkdir(parents=True, exist_ok=False)
    json_path = run_dir / "per_query.json"
    all_results = []
    run_names = ["Without Rerank"]
    if config.reranker.enabled:
        run_names.append("With Rerank")
    # Pure retrieval evaluation reranks all candidates before metric cutoffs.
    # reranker.top_k/context.top_k select answer context in the application pipeline.
    config_record = {
        "evaluation_protocol": "retrieval-optional-rerank-v2",
        "retrieval_mode": config.retrieval.mode, "reranker_enabled": config.reranker.enabled,
        "experiments": run_names, "Retrieved_top_k": args.candidate_top_k,
        "Rerank_top_k": args.candidate_top_k if config.reranker.enabled else None,
        "Context_top_k": config.context.top_k,
        "Reranker": config.reranker.model_name if config.reranker.enabled else None,
        "Retriever": config.retrieval.embedding_model,
        "Max_Length": config.reranker.max_length if config.reranker.enabled else None,
        "Batch_size": config.reranker.batch_size if config.reranker.enabled else None,
        "Normalize_embeddings": config.retrieval.normalize_embeddings,
        "Faiss_Index_Path": str(config.paths.faiss_index),
        "Data_Chunks_Path": str(config.paths.chunks),
        "Query_count": len(scored_queries), "Total_query_count": len(queries),
        "Excluded_count": len(excluded_queries), "Queries_path": str(inputs["queries"]),
        "benchmark_version": manifest["version"],
        "config_source": str(resolve_project_path(args.config)), "asset_sha256": asset_hashes,
        "code_sha256": {"eval_retrieval.py": sha256_file(Path(__file__))},
        "metrics": ["Recall@1/3/5", "HitRate@5", "MRR@20"],
        "timing_note": "Preparation and one warmup are separate from scored query timings.",
    }
    phase, current_item, current_baseline_ids = "snapshot", None, []
    try:
        for name, path in inputs.items():
            copied = run_dir / path.name
            shutil.copy2(path, copied)
            if sha256_file(copied) != asset_hashes[name]:
                raise ValueError(f"Benchmark input changed during snapshot: {name}")
        write_json(run_dir / "config.json", config_record)
        write_json(run_dir / "excluded_queries.json", excluded_queries)
        write_json(json_path, all_results)
        write_json(run_dir / "run_status.json", {"status": "running", "completed_count": 0})

        phase = "prepare"
        retriever = DocumentRetriever(
            index_path=config.paths.faiss_index, chunks_path=config.paths.chunks,
            embedding_model=config.retrieval.embedding_model,
            normalize_embeddings=config.retrieval.normalize_embeddings, mode=config.retrieval.mode,
        )
        reranker = None
        if config.reranker.enabled:
            reranker = CrossEncoderReranker(model_name=config.reranker.model_name,
                max_length=config.reranker.max_length, batch_size=config.reranker.batch_size)
        start = perf_counter()
        retriever.prepare()
        retriever_load_seconds = perf_counter() - start
        reranker_load_seconds = None
        if reranker is not None:
            start = perf_counter()
            reranker.prepare()
            reranker_load_seconds = perf_counter() - start

        phase, current_item = "warmup", warmup_item
        start = perf_counter()
        candidates = retriever.retrieve(warmup_item["query"], top_k=args.candidate_top_k)
        if reranker is not None:
            reranker.rerank(warmup_item["query"], candidates, top_k=args.candidate_top_k)
        warmup_seconds = perf_counter() - start

        for item in scored_queries:
            phase, current_item, current_baseline_ids = "retrieve", item, []
            relevant = set(item["relevant_chunk_ids"])
            start = perf_counter()
            candidates = retriever.retrieve(item["query"], top_k=args.candidate_top_k)
            retrieval_seconds = perf_counter() - start
            current_baseline_ids = [r.chunk.chunk_id for r in candidates]
            rankings = {"Without Rerank": current_baseline_ids}
            rerank_seconds = None
            if reranker is not None:
                phase = "rerank"
                start = perf_counter()
                reranked = reranker.rerank(item["query"], candidates, top_k=args.candidate_top_k)
                rerank_seconds = perf_counter() - start
                rankings["With Rerank"] = [r.chunk.chunk_id for r in reranked]
            experiments = {
                name: score_ranking(ids, relevant, retrieval_seconds=retrieval_seconds,
                                    rerank_seconds=rerank_seconds if name == "With Rerank" else None)
                for name, ids in rankings.items()
            }
            record = {
                "query_id": item["query_id"], "query": item["query"],
                "relevant_chunk_ids": sorted(relevant), "baseline_ids": current_baseline_ids,
                "reranked_ids": rankings.get("With Rerank"), "metrics": experiments,
            }
            phase = "checkpoint"
            write_json(json_path, all_results + [record])
            all_results.append(record)
            write_json(run_dir / "run_status.json",
                       {"status": "running", "completed_count": len(all_results)})

        phase, current_item = "summarize", None
        summary_metrics = {
            name: {
                "mrr_at_20" if metric == "rr_at_20" else metric:
                    sum(r["metrics"][name][metric] for r in all_results) / len(all_results)
                for metric in METRIC_NAMES
            } for name in run_names
        }
        summary = {
            "scored_count": len(all_results), "excluded_count": len(excluded_queries),
            "retrieval_mode": config.retrieval.mode, "reranker_enabled": config.reranker.enabled,
            "retriever_load_seconds": retriever_load_seconds,
            "reranker_load_seconds": reranker_load_seconds,
            "warmup_query_id": warmup_item["query_id"], "warmup_seconds": warmup_seconds,
            "metrics": summary_metrics,
        }
        with (run_dir / "total.csv").open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle,
                fieldnames=["run", "recall_1", "recall_3", "recall_5", "hit_5", "mrr_at_20"])
            writer.writeheader()
            for name, metrics in summary_metrics.items():
                writer.writerow({"run": name, **metrics})
        write_json(run_dir / "summary.json", summary)
        write_json(run_dir / "run_status.json",
                   {"status": "complete", "completed_count": len(all_results)})
    except (Exception, KeyboardInterrupt) as error:
        # Preserve diagnostics and re-raise; a failed run must not look successful.
        failure = {
            "status": "interrupted" if isinstance(error, KeyboardInterrupt) else "failed",
            "phase": phase, "query_id": current_item["query_id"] if current_item else None,
            "query": current_item["query"] if current_item else None,
            "completed_count": len(all_results), "baseline_ids": current_baseline_ids,
            "error_type": type(error).__name__, "error": str(error),
        }
        write_json(run_dir / "failure.json", failure)
        write_json(run_dir / "run_status.json", failure)
        raise
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"Saved retrieval results to {run_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
