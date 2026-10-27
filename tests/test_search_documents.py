import json

import pytest

from rag_agent_system.tools.search_docments import search_documents
from rag_agent_system.models import DocumentChunk, RetrievedChunk
class FakeRetriever:
    def __init__(self, results=None):
        self.results = [] if results is None else results
        self.calls = []

    def retrieve(self, query, top_k=3):
        self.calls.append((query, top_k))
        return self.results

def test_search_documents_returns_empty_list():
    retriever = FakeRetriever()
    output = search_documents(query="RAG", top_k=3, retriever=retriever)

    assert output == []
    assert retriever.calls == [("RAG", 3)]

def test_search_documents_converts_retrieved_chunk():
    chunk = DocumentChunk(
        chunk_id="chunk_001",
        text="RAG 将检索与生成结合。",
        source="rag_intro.txt",
    )
    item = RetrievedChunk(
        chunk=chunk,
        score=0.85,
        rank=1,
        rerank_score=0.9,
        rerank_rank=1,
    )
    retriever = FakeRetriever([item])
    output = search_documents(query="RAG", top_k=3, retriever=retriever)
    assert output == [{
            "chunk_id": "chunk_001",
            "text": "RAG 将检索与生成结合。",
            "score": 0.85,
            "source": "rag_intro.txt",
            "metadata": {},
            "rerank_score": 0.9,
            "rerank_rank": 1,
        }]
    assert retriever.calls == [("RAG", 3)]


@pytest.mark.parametrize("source,metadata", [
    ("sec", {"company": "Example", "ticker": "EX", "fiscal_year": 2025,
             "document_id": "ex-2025-10k", "section": "item_1",
             "source_url": "https://example.invalid/report",
             "source_spans": [{"block_index": 1, "start_char": 0, "end_char": 8}]}),
    ("tinystories", {"story_id": "story_000000", "source_index": 0}),
], ids=["sec", "tinystories"])
def test_search_documents_preserves_source_metadata(source, metadata):
    chunk = DocumentChunk("chunk_001", "Evidence", source=source, metadata=metadata)
    retriever = FakeRetriever([RetrievedChunk(chunk, score=0.8, rank=1)])

    output = search_documents("Evidence", 1, retriever=retriever)

    assert output[0]["metadata"] == metadata
    assert output[0]["metadata"] is not chunk.metadata
    assert json.loads(json.dumps(output))[0]["metadata"] == metadata
    output[0]["metadata"]["response_only"] = True
    assert "response_only" not in chunk.metadata
