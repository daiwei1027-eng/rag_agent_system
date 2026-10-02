"""End-to-end RAG orchestration contract."""

from typing import Protocol

from rag_agent_system.models import RAGResult, RetrievedChunk


class Retriever(Protocol):
    def retrieve(self, query: str, top_k: int = 3) -> list[RetrievedChunk]: ...


class ContextBuilderProtocol(Protocol):
    def build(self, chunks: list[RetrievedChunk]) -> str: ...


class PromptBuilderProtocol(Protocol):
    def build(
        self,
        question: str,
        context: str,
        *,
        additional_instruction: str | None = None,
    ) -> str: ...


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

    def query(
            self,
            question: str,
            *,
            additional_instruction: str | None = None,) -> RAGResult:
        if not isinstance(question, str):
            raise TypeError("question must be a string.")

        question = question.strip()
        if not question:
            raise ValueError("question cannot be empty.")

        chunks=self.retriever.retrieve(question, top_k=self.top_k)
        context=self.context_builder.build(chunks)
        prompt = self.prompt_builder.build(
            question,
            context,
            additional_instruction=additional_instruction,
        )
        answer=self.generator.generate(prompt)
        return RAGResult(question=question, answer=answer,sources=tuple(chunks))

