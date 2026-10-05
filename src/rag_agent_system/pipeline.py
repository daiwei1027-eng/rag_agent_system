"""End-to-end RAG orchestration contract."""

from typing import Protocol

from rag_agent_system.models import RAGResult, RetrievedChunk

class Reranker(Protocol):
    def rerank(
        self,
        query: str,
        documents: list[RetrievedChunk],
        top_k: int,
    ) -> list[RetrievedChunk]: ...
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
        top_k: int = 20,
        rerank_top_k: int = 5,
        reranker: Reranker | None = None,
        context_top_k: int | None = None,
    ) -> None:
        if context_top_k is None:
            context_top_k = rerank_top_k if reranker is not None else top_k
        # 2. 校验三个数量
        for name, value in (
                ("top_k", top_k),
                ("rerank_top_k", rerank_top_k),
                ("context_top_k", context_top_k),
        ):
            if type(value) is not int or value <= 0:
                raise ValueError(f"{name} must be a positive integer.")

        # 3. 校验数量关系
        if context_top_k > top_k:
            raise ValueError("context_top_k must not exceed top_k.")

        if reranker is not None:
            if not context_top_k <= rerank_top_k <= top_k:
                raise ValueError(
                    "When reranker is enabled, require: "
                    "context_top_k <= rerank_top_k <= top_k."
                )
        self.retriever = retriever
        self.context_builder = context_builder
        self.prompt_builder = prompt_builder
        self.generator = generator
        self.top_k = top_k
        self.reranker = reranker
        self.rerank_top_k = rerank_top_k
        self.context_top_k = context_top_k

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
        candidates = self.retriever.retrieve(question, top_k=self.top_k)
        if self.reranker is not None:
            ranked = self.reranker.rerank(
                question,
                candidates,
                top_k=self.rerank_top_k,
            )
        else:
            ranked = candidates

        chunks = ranked[:self.context_top_k]
        context = self.context_builder.build(chunks)
        prompt = self.prompt_builder.build(
            question,
            context,
            additional_instruction=additional_instruction,
        )
        answer=self.generator.generate(prompt)
        return RAGResult(
            question=question,
            answer=answer,
            sources=tuple(chunks),
            retrieved_candidates=tuple(candidates),
            ranked_chunks=tuple(ranked),
            context_text=context,
            prompt_text=prompt,
        )

