import json
from pathlib import Path
import csv
from rag_agent_system.config import load_config
from rag_agent_system.evaluation.metrics import (
    recall_at_k,
    hit_rate_at_k,
    reciprocal_rank,
)
from rag_agent_system.retrieval.faiss_retriever import FaissRetriever
from rag_agent_system.retrieval.reranker import CrossEncoderReranker
queries_path = Path(r"C:\Users\admin\PycharmProjects\Deeplearning_Study\rag_agent_system\data\evaluation\tinystories_queries_draft.jsonl")

with queries_path.open("r", encoding="utf-8-sig") as f:
    queries = [json.loads(line) for line in f if line.strip()]

config = load_config()

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
json_path = Path(r"C:\Users\admin\PycharmProjects\Deeplearning_Study\rag_agent_system\data\evaluation\per_query.json")


for item in queries:
    query = item["query"]
    relevant_ids = set(item["relevant_chunk_ids"])
    candidates = retriever.retrieve(query, top_k=20)
    reranked = reranker.rerank(query, candidates, top_k=20)

    baseline_ids = [result.chunk.chunk_id for result in candidates]
    reranked_ids = [result.chunk.chunk_id for result in reranked]

    # TODO：分别计算两组 Recall@1/3/5、HitRate@5、RR@20
    # TODO：保存 query_id、两组排序 ID 和逐问题指标
    with_rerank_recall_1=recall_at_k(reranked_ids,relevant_ids,1)
    with_rerank_recall_3 = recall_at_k(reranked_ids, relevant_ids, 3)
    with_rerank_recall_5 = recall_at_k(reranked_ids, relevant_ids, 5)
    with_rerank_hit_5 = hit_rate_at_k(reranked_ids, relevant_ids, 5)
    with_rerank_relevance = [chunk_id in relevant_ids for chunk_id in reranked_ids]
    with_rr_20 = reciprocal_rank(with_rerank_relevance)
    without_rerank_recall_1 = recall_at_k(baseline_ids, relevant_ids, 1)
    without_rerank_recall_3 = recall_at_k(baseline_ids, relevant_ids, 3)
    without_rerank_recall_5 = recall_at_k(baseline_ids, relevant_ids, 5)
    without_rerank_hit_5 = hit_rate_at_k(baseline_ids, relevant_ids, 5)
    without_rerank_relevance = [chunk_id in relevant_ids for chunk_id in baseline_ids]
    without_rr_20 = reciprocal_rank(without_rerank_relevance)
    experiments={
        "With Rerank":{"recall_1":with_rerank_recall_1,
                       "recall_3": with_rerank_recall_3,
                       "recall_5": with_rerank_recall_5,
                       "hit_5": with_rerank_hit_5,
                       "rr_at_20": with_rr_20
                       }
        ,"Without Rerank":{"recall_1":without_rerank_recall_1,
                       "recall_3": without_rerank_recall_3,
                       "recall_5": without_rerank_recall_5,
                       "hit_5": without_rerank_hit_5,
                       "rr_at_20": without_rr_20
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

print(json.dumps(summary, ensure_ascii=False, indent=2))
json_path.parent.mkdir(parents=True, exist_ok=True)
with json_path.open("w", encoding="utf-8") as f:
    json.dump(all_results, f, ensure_ascii=False, indent=2)
print(f"Saved {len(all_results)} query results to {json_path}")
csv_path = Path(r"C:\Users\admin\PycharmProjects\Deeplearning_Study\rag_agent_system\data\evaluation\total.csv")
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
"Queries_path": str(queries_path)
                   }
config_path=Path(r"C:\Users\admin\PycharmProjects\Deeplearning_Study\rag_agent_system\data\evaluation\config.json")
config_path.parent.mkdir(parents=True, exist_ok=True)

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