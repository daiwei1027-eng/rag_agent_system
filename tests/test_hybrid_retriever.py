"""RRF fusion acceptance with fixed backend rankings and no model loading."""

from pathlib import Path

import pytest

from rag_agent_system.models import DocumentChunk, RetrievedChunk
from rag_agent_system.retrieval import DocumentRetriever


@pytest.mark.parametrize(
    "dense_ids,bm25_ids,top_k,expected_ids,expected_scores",
    [
        (["a", "b", "c"], ["b", "c"], 3, ["b", "c", "a"],
         [1 / 62 + 1 / 61, 1 / 63 + 1 / 62, 1 / 61]),
        (["a", "b"], [], 2, ["a", "b"], [1 / 61, 1 / 62]),
        ([], ["b", "a"], 2, ["b", "a"], [1 / 61, 1 / 62]),
        ([], [], 2, [], []),
        (["b", "c"], ["a", "c"], 2, ["c", "a"], [2 / 62, 1 / 61]),
    ],
    ids=["overlap-adds-ranks", "bm25-empty", "dense-empty", "both-empty",
         "ties-and-final-topk"],
)
def test_rrf_fusion_scores_deduplication_budgets_and_empty_branches(
    monkeypatch, dense_ids, bm25_ids, top_k, expected_ids, expected_scores,
):
    engine = DocumentRetriever(
        index_path=Path("not-loaded.faiss"), chunks_path=Path("not-loaded.json"),
        embedding_model="not-loaded", normalize_embeddings=True, mode="hybrid",
    )
    chunks = {cid: DocumentChunk(cid, f"text {cid}", source="sec",
                                 metadata={"document_id": "fixture"})
              for cid in set(dense_ids + bm25_ids)}
    calls = []

    def backend(name, ids, raw_score):
        def retrieve(query, top_k):
            calls.append((name, query, top_k))
            return [RetrievedChunk(chunks[cid], raw_score / rank, rank)
                    for rank, cid in enumerate(ids[:top_k], start=1)]
        return retrieve

    # Deliberately incomparable raw score scales: fusion must use ranks only.
    monkeypatch.setattr(engine, "_retrieve_dense", backend("dense", dense_ids, 1000.0))
    monkeypatch.setattr(engine, "_retrieve_bm25", backend("bm25", bm25_ids, 0.001))

    results = engine.retrieve(" query ", top_k=top_k)

    assert calls == [("dense", "query", top_k), ("bm25", "query", top_k)]
    assert [r.chunk.chunk_id for r in results] == expected_ids
    assert [r.score for r in results] == pytest.approx(expected_scores, rel=1e-12)
    assert [r.rank for r in results] == list(range(1, len(results) + 1))
    assert len(results) <= top_k
    assert len({r.chunk.chunk_id for r in results}) == len(results)
    assert all(r.chunk is chunks[r.chunk.chunk_id] for r in results)
    assert all(r.rerank_score is None and r.rerank_rank is None for r in results)
