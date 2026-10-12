from typing import Any
def search_documents(
    query: str,
    top_k: int,
    *,
    retriever,
    reranker=None,
    candidate_top_k: int | None = None,
) -> list[dict[str, Any]]:
    """检索相关文档，并转换为可序列化的字典列表。"""
    if reranker is not None:
        if type(candidate_top_k) is not int or candidate_top_k < top_k:
            raise ValueError("candidate_top_k must be an integer >= top_k")
        chunks = retriever.retrieve(query, top_k=candidate_top_k)
        chunks = reranker.rerank(query, documents=chunks, top_k=top_k)
    else:
        chunks = retriever.retrieve(query, top_k=top_k)
    output = []
    for retrieved_chunk in chunks:
        document = {
            "chunk_id": retrieved_chunk.chunk.chunk_id,
            "text": retrieved_chunk.chunk.text,
            "score": float(retrieved_chunk.score),
            "source": retrieved_chunk.chunk.source,
            "rerank_score": (
                float(retrieved_chunk.rerank_score)
                if retrieved_chunk.rerank_score is not None else None
            ),
            "rerank_rank": retrieved_chunk.rerank_rank,
        }
        output.append(document)
    return output
