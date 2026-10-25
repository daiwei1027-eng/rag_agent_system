"""Mode routing preserves dense behavior and never silently falls back to dense."""

from pathlib import Path

import faiss
import numpy as np
import pytest

from rag_agent_system.models import DocumentChunk
from rag_agent_system.retrieval import DocumentRetriever, FaissRetriever


def retriever(**kwargs):
    return DocumentRetriever(index_path=Path("not-loaded.faiss"),
                             chunks_path=Path("not-loaded.json"),
                             embedding_model="not-loaded", normalize_embeddings=True,
                             **kwargs)


def test_default_dense_alias_and_existing_search_behavior():
    assert FaissRetriever is DocumentRetriever
    engine = retriever()
    assert engine.mode == "dense"
    engine._index = faiss.IndexFlatIP(2)
    engine._index.add(np.eye(2, dtype=np.float32))
    engine._chunks = {"a": DocumentChunk("a", "alpha"), "b": DocumentChunk("b", "beta")}
    engine._faiss_id_to_chunk_id = {0: "a", 1: "b"}

    class Encoder:
        def encode(self, texts, **kwargs):
            assert texts == ["alpha"]
            assert kwargs == {"normalize_embeddings": True, "convert_to_numpy": True}
            return np.array([[1, 0]], dtype=np.float32)

    engine._encoder = Encoder()
    results = engine.retrieve("  alpha  ", top_k=5)
    assert [r.chunk.chunk_id for r in results] == ["a", "b"]
    assert [r.rank for r in results] == [1, 2]
    assert [r.score for r in results] == [1, 0]


@pytest.mark.parametrize("mode", ["hybird", None, True])
def test_unknown_mode_rejected_at_construction(mode):
    with pytest.raises(ValueError, match="mode"):
        retriever(mode=mode)


def test_hybrid_prepare_dispatches_to_both_resource_loaders(monkeypatch):
    engine = retriever(mode="hybrid")
    calls = []

    monkeypatch.setattr(engine, "_load_dense_resources", lambda: calls.append("dense"))
    monkeypatch.setattr(engine, "_load_bm25_resources", lambda: calls.append("bm25"))
    engine.prepare()
    assert sorted(calls) == ["bm25", "dense"]


@pytest.mark.parametrize("query,top_k", [("  ", 2), ("query", True)])
def test_common_validation_runs_before_dispatch(query, top_k):
    with pytest.raises(ValueError):
        retriever(mode="bm25").retrieve(query, top_k=top_k)
