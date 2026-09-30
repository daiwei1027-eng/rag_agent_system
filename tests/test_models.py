from rag_agent_system.evaluation.metrics import reciprocal_rank
from rag_agent_system.models import DocumentChunk, RetrievedChunk


def test_retrieved_chunk_keeps_source_identity() -> None:
    chunk = DocumentChunk(chunk_id="doc-7", text="KV cache reuses key/value tensors.")

    result = RetrievedChunk(chunk=chunk, score=0.91, rank=1)

    assert result.chunk.chunk_id == "doc-7"
    assert result.rank == 1


def test_reciprocal_rank_uses_first_relevant_result() -> None:
    assert reciprocal_rank([False, True, True]) == 0.5
    assert reciprocal_rank([False, False]) == 0.0

