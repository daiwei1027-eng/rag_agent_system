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
            "rerank_score": 0.9,
            "rerank_rank": 1,
        }]
    assert retriever.calls == [("RAG", 3)]
