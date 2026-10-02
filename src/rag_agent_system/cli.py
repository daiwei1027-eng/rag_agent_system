"""Command-line interface for the Day 18 RAG baseline."""

import argparse
import logging
from collections.abc import Sequence

from rag_agent_system.config import load_config
from rag_agent_system.generation import ContextBuilder, HuggingFaceGenerator, PromptBuilder
from rag_agent_system.logging_config import configure_logging
from rag_agent_system.pipeline import RAGPipeline
from rag_agent_system.retrieval import FaissRetriever

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
    pipeline = RAGPipeline(
        retriever=FaissRetriever(
            index_path=config.paths.faiss_index,
            chunks_path=config.paths.chunks,
            embedding_model=config.retrieval.embedding_model,
            normalize_embeddings=(
                config.retrieval.normalize_embeddings
            ),
        ),
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
    for source in result.sources:
        print(f"[{source.rank}] chunk_id={source.chunk.chunk_id} score={source.score:.4f}")
    return 0
