import argparse
import json
from pathlib import Path
from rag_agent_system.config import load_config
from rag_agent_system.evaluation.benchmark import load_benchmark
import shutil
from rag_agent_system.pipeline import RAGPipeline
from rag_agent_system.retrieval import FaissRetriever, CrossEncoderReranker
from rag_agent_system.generation import (
    ContextBuilder,
    PromptBuilder,
    HuggingFaceGenerator,
)
from dataclasses import asdict
from time import perf_counter
from rag_agent_system.paths import resolve_project_path

parser = argparse.ArgumentParser(description="Run the five-case TinyStories RAG evaluation.")
parser.add_argument("--config", default="configs/default.yaml", help="Config selecting one data/benchmark version.")
parser.add_argument(
    "--run-dir", type=Path, required=True,
    help="New output directory; relative paths are resolved from the project root.",
)
args = parser.parse_args()
config = load_config(args.config)
benchmark = load_benchmark(config)
target_cases = []
target_ids = {"q001", "q005", "q007", "q038", "q042"}
target_path = benchmark["queries_path"]
run_dir = resolve_project_path(args.run_dir)
final_output=[]
run_dir.mkdir(parents=True, exist_ok=False)
for path in (target_path, benchmark["manifest_path"], benchmark["absence_path"]):
    shutil.copy2(path, run_dir / path.name)
with target_path.open("r", encoding="utf-8-sig") as f:
    for line in f:
        if not line.strip():
            continue
        item = json.loads(line)
        if item["query_id"] in target_ids:
            target_case = item
            target_cases.append(target_case)
found_ids = {item["query_id"] for item in target_cases}
missing_ids = target_ids - found_ids

if missing_ids:
    raise ValueError(f"缺少问题：{sorted(missing_ids)}")

pipeline = RAGPipeline(
        retriever=FaissRetriever(
            index_path=config.paths.faiss_index,
            chunks_path=config.paths.chunks,
            embedding_model=config.retrieval.embedding_model,
            normalize_embeddings=(
                config.retrieval.normalize_embeddings
            ),
        ),
        reranker=CrossEncoderReranker(
    model_name=config.reranker.model_name,
    max_length=config.reranker.max_length,
    batch_size=config.reranker.batch_size,
),
        rerank_top_k=20,
        context_top_k=5,
        context_builder=ContextBuilder(),
        prompt_builder=PromptBuilder(),
        generator=HuggingFaceGenerator(
            config.generation.model_name,
            max_new_tokens=config.generation.max_new_tokens,
            temperature=config.generation.temperature,
        ),
        top_k=50,
    )
for i,target_case in enumerate(target_cases):
    question = target_case["query"]
    query_id=target_case["query_id"]
    start = perf_counter()
    result = pipeline.query(target_case["query"])
    query_time = perf_counter() - start
    exp={
        "query_id":target_case["query_id"],
    "question":target_case["query"],
    "expected_answer":target_case["expected_answer"],
        "retrieved_candidates": [
            asdict(item) for item in result.retrieved_candidates
        ],
        "ranked_chunks": [
            asdict(item) for item in result.ranked_chunks
        ],
        "sources": [
            asdict(item) for item in result.sources
        ],
        "context_text":result.context_text,
        "prompt_text":result.prompt_text,
        "answer":result.answer,
        "query_time":query_time,
    }
    final_output.append(exp)
json_path = run_dir / f"per_query.json"

with json_path.open("x", encoding="utf-8") as f:
    json.dump(final_output, f, ensure_ascii=False, indent=2)
print(f"Saved {len(final_output)} results to {json_path}")
