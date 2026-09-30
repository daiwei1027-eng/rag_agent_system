from rag_agent_system.config import load_config
from rag_agent_system.retrieval import FaissRetriever


def main() -> None:
    config = load_config()

    retriever = FaissRetriever(
        index_path=config.paths.faiss_index,
        chunks_path=config.paths.chunks,
        embedding_model=config.retrieval.embedding_model,
        normalize_embeddings=config.retrieval.normalize_embeddings,
    )

    results = retriever.retrieve(
        "A girl finds a needle and her mother helps sew a button.",
        top_k=3,
    )

    for result in results:
        print(f"\nRank: {result.rank}")
        print(f"Score: {result.score:.4f}")
        print(f"Chunk ID: {result.chunk.chunk_id}")
        print(f"Source: {result.chunk.source}")
        print(result.chunk.text[:400])


if __name__ == "__main__":
    main()