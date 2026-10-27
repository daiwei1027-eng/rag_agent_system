"""Command-line interface for the Day 18 RAG baseline."""

import argparse
import logging
from collections.abc import Sequence

from rag_agent_system.config import load_config
from rag_agent_system.generation import ContextBuilder, HuggingFaceGenerator, PromptBuilder
from rag_agent_system.logging_config import configure_logging
from rag_agent_system.pipeline import RAGPipeline
from rag_agent_system.retrieval import (
    CrossEncoderReranker,
    FaissRetriever,
)
LOGGER = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Query the local Day 18 RAG baseline.")
    parser.add_argument("--question", "-q", help="Question to answer; prompts if omitted.")
    parser.add_argument("--config", default="configs/default.yaml", help="YAML config path.")
    parser.add_argument(
        "--additional-instruction",
        default=None,
        help="Optional answer preferences, such as language or length.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config = load_config(args.config)
    configure_logging(config.log_level)

    question = args.question or input("Question: ").strip()
    reranker=None
    if config.reranker.enabled:
        reranker=CrossEncoderReranker(model_name=config.reranker.model_name,
                                      max_length=config.reranker.max_length,
                                      batch_size=config.reranker.batch_size)

    pipeline = RAGPipeline(
        retriever=FaissRetriever(
            index_path=config.paths.faiss_index,
            chunks_path=config.paths.chunks,
            embedding_model=config.retrieval.embedding_model,
            normalize_embeddings=(
                config.retrieval.normalize_embeddings
            ),
            mode=config.retrieval.mode,
        ),
        reranker=reranker,
        rerank_top_k=config.reranker.top_k,
        context_top_k=config.context.top_k,
        context_builder=ContextBuilder(),
        prompt_builder=PromptBuilder(),
        generator=HuggingFaceGenerator(
            config.generation.model_name,
            max_new_tokens=config.generation.max_new_tokens,
            temperature=config.generation.temperature,
        ),
        top_k=config.retrieval.top_k,
    )

    try:
        result = pipeline.query(
            question,
            additional_instruction=args.additional_instruction,
        )
    except NotImplementedError as exc:
        LOGGER.error("%s", exc)
        return 2

    print(f"\nAnswer:\n{result.answer}\n\nSources:")
    for position,source in enumerate(result.sources,start=1):
        print(f"Original Rank{source.rank}Original Score {source.score}\n"
              f"Chunk_id:{source.chunk.chunk_id},Position:{position}\n"
              f"Text:{source.chunk.text}\n")
        if source.rerank_score is not None:
            print(f"Rerank Rank{source.rerank_rank}Rerank Score {source.rerank_score}\n")
    return 0