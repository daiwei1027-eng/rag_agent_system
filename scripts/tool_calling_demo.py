from rag_agent_system.tools.registry import ToolRegistry
from rag_agent_system.tools.calculator_tool import calculator
from rag_agent_system.tools.schemas import CALCULATOR_SCHEMA,SEARCH_DOCUMENTS_SCHEMA,TIME_SCHEMA
from rag_agent_system.tools.time_tool import get_current_time
from rag_agent_system.tools.search_docments import search_documents
from rag_agent_system.models import DocumentChunk,RetrievedChunk
import json
class FakeRetriever:
    def __init__(self, results):
        self.results = results
        self.calls = []

    def retrieve(self, query, top_k=3):
        self.calls.append((query, top_k))
        return self.results
def pipeline():
    def time_handler(timezone: str) -> str:
        return get_current_time(timezone_name=timezone)
    chunk = DocumentChunk(
        chunk_id="chunk_001",
        text="RAG 将检索与生成结合。",
        source="rag_intro.txt",
    )
    item = RetrievedChunk(chunk=chunk, score=0.85, rank=1)
    retriever = FakeRetriever([item])

    def search_handler(query: str, top_k: int):
        return search_documents(
            query,
            top_k,
            retriever=retriever,
        )
    tool_registry = ToolRegistry()
    tool_registry.register(CALCULATOR_SCHEMA,calculator)
    tool_registry.register(SEARCH_DOCUMENTS_SCHEMA,search_handler)
    tool_registry.register(TIME_SCHEMA,time_handler)


    search_tool_call = {
        "id": "call_001",
        "name": "search_documents",
        "arguments": {"query": "RAG", "top_k": 3},
    }
    time_tool_call = {
        "id": "call_002",
        "name": "time",
        "arguments": {"timezone": "UTC"},
    }
    calculator_tool_call = {
        "id": "call_003",
        "name": "calculator",
        "arguments": {"operation": "multiply", "a": 12, "b": 8},
    }
    calculator_tool_call_2 = {
        "id": "call_004",
        "name": "calculator",
        "arguments": {"operation": "divide", "a": 12, "b": 0},
    }
    search_result=tool_registry.execute_safe(search_tool_call)
    time_result=tool_registry.execute_safe(time_tool_call)
    calculator_result=tool_registry.execute_safe(calculator_tool_call)
    calculator_result_2=tool_registry.execute_safe(calculator_tool_call_2)
    tool_call=[search_tool_call, time_tool_call, calculator_tool_call, calculator_tool_call_2]
    results=[search_result, time_result, calculator_result, calculator_result_2]
    print(json.dumps(tool_call, ensure_ascii=False, indent=2))
    print(json.dumps(results, ensure_ascii=False, indent=2))
if __name__ == "__main__":
    pipeline()