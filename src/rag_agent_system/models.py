"""Shared, dependency-light data contracts for the RAG system."""

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class DocumentChunk:
    """A persisted source chunk from the Day 17 document store."""

    chunk_id: str
    text: str
    source: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class RetrievedChunk:
    """A source chunk returned by retrieval, including rank and similarity score."""

    chunk: DocumentChunk
    score: float
    rank: int


@dataclass(frozen=True, slots=True)
class RAGResult:
    """The public result returned by the end-to-end pipeline."""

    question: str
    answer: str
    sources: tuple[RetrievedChunk, ...]

