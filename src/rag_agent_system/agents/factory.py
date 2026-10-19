from rag_agent_system.agents.loop import Agent
from rag_agent_system.config import AppConfig
from rag_agent_system.tools.search_docments import search_documents
from rag_agent_system.tools.schemas import (
    CALCULATOR_SCHEMA,
    SEARCH_DOCUMENTS_SCHEMA,
    TIME_SCHEMA,
)
from typing import Any
from rag_agent_system.agents.llm_client import LocalLLMClient
from rag_agent_system.tools.calculator_tool import calculator
from rag_agent_system.tools.registry import ToolRegistry
from rag_agent_system.tools.time_tool import get_current_time
from rag_agent_system.retrieval import CrossEncoderReranker, FaissRetriever
def build_agent(config: AppConfig) -> Agent:
    reranker = None
    if config.reranker.enabled:
        reranker = CrossEncoderReranker(
            config.reranker.model_name,
            max_length=config.reranker.max_length,
            batch_size=config.reranker.batch_size,
        )
    retriever = FaissRetriever(
        index_path=config.paths.faiss_index,
        chunks_path=config.paths.chunks,
        embedding_model=config.retrieval.embedding_model,
        normalize_embeddings=config.retrieval.normalize_embeddings,
    )

    def search_handler(query: str, top_k: int) -> list[dict[str, Any]]:
        return search_documents(
            query,
            top_k,
            retriever=retriever,
            reranker=reranker,
            candidate_top_k=config.retrieval.top_k,
        )

    registry = ToolRegistry()
    registry.register(SEARCH_DOCUMENTS_SCHEMA, search_handler)
    registry.register(TIME_SCHEMA, get_current_time)
    registry.register(CALCULATOR_SCHEMA, calculator)
    client = LocalLLMClient(
        config.agent.model_name,
        max_new_tokens=config.agent.max_new_tokens,
    )
    agent = Agent(client, registry)
    return agent