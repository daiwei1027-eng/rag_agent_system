"""BM25 acceptance with a hand-calculated corpus and no model inference."""

import json
import math
from unittest.mock import Mock

import pytest

from rag_agent_system.retrieval import faiss_retriever as module


@pytest.fixture
def engine(tmp_path, monkeypatch):
    path = tmp_path / "chunks.json"
    path.write_text(json.dumps([
        {"chunk_id": "a", "text": "cloud cloud revenue"},
        {"chunk_id": "b", "text": "cloud services"},
        {"chunk_id": "c", "text": "gaming revenue"},
    ]), encoding="utf-8")

    def forbidden(*args, **kwargs):
        pytest.fail("BM25 must not initialize a Dense model or read a FAISS index")

    monkeypatch.setattr(module, "SentenceTransformer", forbidden)
    monkeypatch.setattr(module.faiss, "read_index", forbidden)
    return module.DocumentRetriever(
        index_path=tmp_path / "nonexistent.faiss", chunks_path=path,
        embedding_model="must-not-load", normalize_embeddings=True, mode="bm25",
    )


def test_statistics_and_hand_calculated_scores(engine):
    results = engine.retrieve("CLOUD revenue", top_k=10)

    assert engine._bm25_chunk_ids == ["a", "b", "c"]
    assert engine._bm25_term_frequencies == [
        {"cloud": 2, "revenue": 1}, {"cloud": 1, "services": 1},
        {"gaming": 1, "revenue": 1},
    ]
    assert engine._bm25_document_lengths == [3, 2, 2]
    assert engine._bm25_document_frequency == {
        "cloud": 2, "revenue": 2, "services": 1, "gaming": 1,
    }
    assert engine._bm25_average_length == pytest.approx(7 / 3)

    # N=3, df(cloud)=df(revenue)=2, k1=1.5, b=.75.
    # For a, K_d=51/28; for b/c, K_d=75/56.
    expected = [math.log(1.6) * (140 / 107 + 70 / 79),
                math.log(1.6) * 140 / 131, math.log(1.6) * 140 / 131]
    assert [r.chunk.chunk_id for r in results] == ["a", "b", "c"]
    assert [r.score for r in results] == pytest.approx(expected, rel=1e-12)
    assert [r.rank for r in results] == [1, 2, 3]


def test_topk_unknown_words_query_deduplication_and_tokenizer_policy(engine):
    assert engine._tokenize_bm25(" Cloud\nREVENUE, 2025 ") == [
        "cloud", "revenue,", "2025",
    ]
    assert engine.retrieve("unknown", top_k=3) == []
    results = engine.retrieve("cloud revenue", top_k=2)
    assert [r.chunk.chunk_id for r in results] == ["a", "b"]
    assert [r.rank for r in results] == [1, 2]
    assert engine.retrieve("cloud cloud revenue", top_k=2) == results


def test_prepare_and_retrieve_reuse_bm25_resources_without_dense(engine, monkeypatch):
    loader = Mock(wraps=module.load_chunks)
    monkeypatch.setattr(module, "load_chunks", loader)

    engine.prepare()
    assert engine._bm25_ready
    engine.prepare()
    assert engine.retrieve("cloud", top_k=2)

    assert loader.call_count == 1
    assert engine._encoder is None and engine._index is None
    assert engine._faiss_id_to_chunk_id is None
