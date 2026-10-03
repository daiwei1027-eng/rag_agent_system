from rag_agent_system.config import load_config
from rag_agent_system.retrieval.faiss_retriever import FaissRetriever
from rag_agent_system.retrieval.reranker import CrossEncoderReranker
from rag_agent_system.models import  RetrievedChunk
from rag_agent_system.generation.context import ContextBuilder
from rag_agent_system.generation.prompt import PromptBuilder
from rag_agent_system.generation.generator import HuggingFaceGenerator
from rag_agent_system.pipeline import RAGPipeline
from time import time
import json
from dataclasses import asdict
from pathlib import Path


def main()-> None:
    config = load_config()
    faisstriever = FaissRetriever(index_path=config.paths.faiss_index, chunks_path=config.paths.chunks,
                                  embedding_model=config.retrieval.embedding_model,
                                  normalize_embeddings=config.retrieval.normalize_embeddings)
    crossencoderreranker = CrossEncoderReranker(model_name=config.reranker.model_name,
                                                max_length=config.reranker.max_length,
                                                batch_size=config.reranker.batch_size)
    class FixedRetriever:
        def __init__(self, candidates: list[RetrievedChunk]):
            self.candidates = tuple(candidates)

        def retrieve(
                self,
                query: str,
                top_k: int = 20,
        ) -> list[RetrievedChunk]:
            return list(self.candidates[:top_k])

    question = "Who found a needle and asked her mother to sew a button?"
    retrieved_chunks=faisstriever.retrieve(question, top_k=config.retrieval.top_k)
    fixed_retriever = FixedRetriever(retrieved_chunks)
    context_builder = ContextBuilder()
    prompter = PromptBuilder()
    generator = HuggingFaceGenerator(
        model_name=config.generation.model_name,
        max_new_tokens=config.generation.max_new_tokens,
        temperature=0,
    )

    with_pipeline=RAGPipeline(fixed_retriever,context_builder,prompter,generator,top_k=config.retrieval.top_k,rerank_top_k=config.reranker.top_k,
                              reranker=crossencoderreranker,context_top_k=config.context.top_k,)
    without_pipeline = RAGPipeline(
        retriever=fixed_retriever,
        context_builder=context_builder,
        prompt_builder=prompter,
        generator=generator,
        top_k=config.retrieval.top_k,
        rerank_top_k=config.reranker.top_k,
        reranker=None,
        context_top_k=config.context.top_k,
    )
    start = time()
    before = without_pipeline.query(question)
    Without_Rerank_Query_time=time() - start
    start = time()
    after = with_pipeline.query(question)
    With_Rerank_Query_time = time() - start
    print(f"Without query time: {Without_Rerank_Query_time:.4f} s")
    print(f"With query time: {With_Rerank_Query_time:.4f} s")
    experiment = {
        "question": question,
        "config": {"Temperature":generator.temperature,
                   "Retrieved_top_k":config.retrieval.top_k,
                   "Rerank_top_k":config.reranker.top_k,
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
                   },

        "retrieved_candidates": [{
            "With_Rerank_Query_candidates": [asdict(candidate)
                                             for candidate in after.retrieved_candidates],
            "Without_Rerank_Query_candidates": [asdict(candidate)
                                             for candidate in before.retrieved_candidates]
        }],
        "without_reranker": {
            "answer": before.answer,
            "query_seconds": Without_Rerank_Query_time,
            "sources": [asdict(source) for source in before.sources]
        },
        "with_reranker": {
            "answer": after.answer,
            "query_seconds": With_Rerank_Query_time,
            "sources": [asdict(source) for source in after.sources]
        },
        "timing_scope": (
            "Query includes first model loading; "
            "excludes original FAISS retrieval."
        ),
    }
    for label, result in (
            ("without reranker", before),
            ("with reranker", after),
    ):
        print(f"\n{label}\nAnswer: {result.answer}")
        for position, source in enumerate(result.sources, start=1):
            print(f"Original Rank{source.rank}Original Score {source.score}\n"
                  f"Chunk_id:{source.chunk.chunk_id},Position:{position}\n"
                  f"Text:{source.chunk.text}\n")

            if source.rerank_score is not None:
                print(f"Rerank Rank{source.rerank_rank}Rerank Score {source.rerank_score}\n")

    project_dir = Path(__file__).resolve().parents[1]
    output_dir = project_dir / "data"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / f"compare_reranking_{time()}.json"

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(experiment, file, ensure_ascii=False, indent=2)

    print(f"Saved to: {output_path}")

if __name__ == "__main__":
    main()