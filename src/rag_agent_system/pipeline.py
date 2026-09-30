"""End-to-end RAG orchestration contract."""

from typing import Protocol

from rag_agent_system.models import RAGResult, RetrievedChunk


class Retriever(Protocol):
    def retrieve(self, query: str, top_k: int = 3) -> list[RetrievedChunk]: ...


class ContextBuilderProtocol(Protocol):
    def build(self, chunks: list[RetrievedChunk]) -> str: ...


class PromptBuilderProtocol(Protocol):
    def build(self, question: str, context: str) -> str: ...


class Generator(Protocol):
    def generate(self, prompt: str) -> str: ...


class RAGPipeline:
    """Coordinate retrieval, prompt preparation, generation, and source reporting."""

    def __init__(
        self,
        retriever: Retriever,
        context_builder: ContextBuilderProtocol,
        prompt_builder: PromptBuilderProtocol,
        generator: Generator,
        *,
        top_k: int = 3,
    ) -> None:
        self.retriever = retriever
        self.context_builder = context_builder
        self.prompt_builder = prompt_builder
        self.generator = generator
        self.top_k = top_k

    def query(self, question: str) -> RAGResult:
        """Answer a question and return the evidence used.

        TODO(DAY18): validate the question and connect retrieve -> context -> prompt ->
        generate. Return an immutable ``RAGResult`` with the retrieved sources.
        """

        raise NotImplementedError("TODO(DAY18): implement RAGPipeline.query")

