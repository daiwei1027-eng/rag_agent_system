from typing import Any
def search_documents(
    query: str,
    top_k: int,
    *,
    retriever,
) -> list[dict[str, Any]]:
    """检索相关文档，并转换为可序列化的字典列表。"""
    retrieved_chunks = retriever.retrieve(query, top_k=top_k)
    output=[]
    for retrieved_chunk in retrieved_chunks:
        document = {
            "chunk_id": retrieved_chunk.chunk.chunk_id,
            "text": retrieved_chunk.chunk.text,
            "score": float(retrieved_chunk.score),
            "source": retrieved_chunk.chunk.source,
        }
        output.append(document)
    return output