from rag_agent_system.models import DocumentChunk, RetrievedChunk
from rag_agent_system.retrieval.reranker import CrossEncoderReranker
documents = [
    RetrievedChunk(
        chunk=DocumentChunk(chunk_id="A", text="Document A"),
        score=0.8,
        rank=1,
    ),
    RetrievedChunk(
        chunk=DocumentChunk(chunk_id="B", text="Document B"),
        score=0.7,
        rank=2,
    ),
    RetrievedChunk(
        chunk=DocumentChunk(chunk_id="C", text="Document C"),
        score=0.6,
        rank=3,
    )

]



class FakeCrossEncoder:
    def predict(self, pairs, *, batch_size, show_progress_bar):
        self.received_pairs = pairs
        return [0.2, 0.9, 0.4]

def test_ranker():
    query="TEST"
    crossencoder = CrossEncoderReranker(model_name="unused-in-test")
    fake_model = FakeCrossEncoder()
    crossencoder._model = fake_model
    reranked_chunks=crossencoder.rerank(query,documents,2)
    assert len(reranked_chunks) == 2
    assert reranked_chunks[0].chunk.chunk_id == "B"
    assert reranked_chunks[0].chunk.text == "Document B"
    assert reranked_chunks[0].rerank_rank == 1
    assert reranked_chunks[0].rerank_score == 0.9
    assert reranked_chunks[0].score == 0.7
    assert reranked_chunks[0].rank == 2
    assert reranked_chunks[1].rerank_score == 0.4
    assert reranked_chunks[1].chunk.chunk_id == "C"
    assert documents[0].rerank_score == None
    assert fake_model.received_pairs == [
        ("TEST", "Document A"),
        ("TEST", "Document B"),
        ("TEST", "Document C"),
    ]