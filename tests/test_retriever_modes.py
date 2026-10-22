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


@pytest.mark.parametrize("mode", ["bm25", "hybrid"])
def test_unimplemented_modes_do_not_load_or_fall_back_to_dense(mode, monkeypatch):
    engine = retriever(mode=mode)

    def forbidden():
        raise AssertionError("Non-dense branch loaded dense resources")

    monkeypatch.setattr(engine, "_load_dense_resources", forbidden)
    with pytest.raises(NotImplementedError):
        engine.retrieve("query", top_k=2)
    with pytest.raises(NotImplementedError):
        engine._load_resources()
    assert engine._encoder is None and engine._index is None


@pytest.mark.parametrize("query,top_k", [("  ", 2), ("query", True)])
def test_common_validation_runs_before_dispatch(query, top_k):
    with pytest.raises(ValueError):
        retriever(mode="bm25").retrieve(query, top_k=top_k)
