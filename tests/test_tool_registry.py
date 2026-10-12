from rag_agent_system.tools.registry import ToolRegistry
from rag_agent_system.tools.calculator_tool import calculator
from rag_agent_system.tools.schemas import CALCULATOR_SCHEMA,SEARCH_DOCUMENTS_SCHEMA,TIME_SCHEMA
from rag_agent_system.tools.time_tool import get_current_time
import pytest
from datetime import datetime, timedelta
from rag_agent_system.models import DocumentChunk,RetrievedChunk
from rag_agent_system.tools.search_docments import search_documents
def test_execute_rejects_invalid_arguments_before_calling_handler():
    calls = []

    def fake_calculator(**arguments):
        calls.append(arguments)
        return 96
    tool_call = {
        "id": "call_001",
        "name": "calculator",
        "arguments": {"operation": "multiply", "a": "12", "b": 8},
    }
    tool_registry = ToolRegistry()
    tool_registry.register(CALCULATOR_SCHEMA, fake_calculator)

    with pytest.raises(TypeError, match="a"):
        tool_registry.execute(tool_call)
    assert calls == []
def test_correctly_registry():
    tool_registry = ToolRegistry()
    tool_registry.register(CALCULATOR_SCHEMA,calculator)
    schemas=tool_registry.get_schemas()
    assert schemas==[CALCULATOR_SCHEMA]
def test_twice_registry():
    tool_registry = ToolRegistry()
    tool_registry.register(CALCULATOR_SCHEMA, calculator)
    with pytest.raises(ValueError,match="already registered"):
        tool_registry.register(CALCULATOR_SCHEMA, calculator)
def test_uncallable_handler():
    tool_registry = ToolRegistry()
    with pytest.raises(TypeError,match="must be callable"):
        tool_registry.register(CALCULATOR_SCHEMA, "calculator")
    assert tool_registry.get_schemas() == []
def test_execute_calculator():
    tool_call = {
        "id": "call_001",
        "name": "calculator",
        "arguments": {"operation": "multiply", "a": 12, "b": 8},
    }
    tool_registry = ToolRegistry()
    tool_registry.register(CALCULATOR_SCHEMA, calculator)
    result=tool_registry.execute(tool_call)
    assert result == {
        "tool_call_id": "call_001",
        "name": "calculator",
        "ok": True,
        "result": 96,
    }
def test_execute_rejects_unknown_tool():
    tool_registry = ToolRegistry()
    tool_call = {
        "id": "call_unknown",
        "name": "unknown_tool",
        "arguments": {},
    }
    tool_registry.register(CALCULATOR_SCHEMA, calculator)
    with pytest.raises(ValueError,match="is not registered"):
        tool_registry.execute(tool_call)
def test_execute_time_returns_utc_observation():
    tool_call = {
        "id": "call_001",
        "name": "time",
        "arguments": {"timezone_name": "UTC"},
    }
    tool_registry = ToolRegistry()
    tool_registry.register(TIME_SCHEMA, get_current_time)
    result=tool_registry.execute(tool_call)
    assert result["tool_call_id"] == "call_001"
    assert result["name"]=="time"
    assert result["ok"] is True
    parsed = datetime.fromisoformat(result["result"])
    assert parsed.utcoffset() == timedelta(0)
class FakeRetriever:
    def __init__(self, results):
        self.results = results
        self.calls = []

    def retrieve(self, query, top_k=3):
        self.calls.append((query, top_k))
        return self.results
def test_search_documents():
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
    tool_call = {
    "id": "call_search",
    "name": "search_documents",
    "arguments": {"query": "RAG", "top_k": 3},
}
    tool_registry = ToolRegistry()
    tool_registry.register(SEARCH_DOCUMENTS_SCHEMA, search_handler)
    result=tool_registry.execute(tool_call)
    assert result == {
        "tool_call_id": "call_search",
        "name": "search_documents",
        "ok": True,
        "result": [{
            "chunk_id": "chunk_001",
            "text": "RAG 将检索与生成结合。",
            "score": 0.85,
            "source": "rag_intro.txt",
            "rerank_score": None,
            "rerank_rank": None,
        }],
    }
    assert retriever.calls==[("RAG", 3)]

def test_execute_safe_calculator():
    tool_call = {
        "id": "call_001",
        "name": "calculator",
        "arguments": {"operation": "multiply", "a": 12, "b": 8},
    }
    tool_registry = ToolRegistry()
    tool_registry.register(CALCULATOR_SCHEMA, calculator)
    result=tool_registry.execute_safe(tool_call)
    assert result == {
        "tool_call_id": "call_001",
        "name": "calculator",
        "ok": True,
        "result": 96,
    }
def test_execute_safe_returns_division_by_zero_error():
    tool_call = {
        "id": "call_001",
        "name": "calculator",
        "arguments": {"operation": "divide", "a": 12, "b": 0},
    }
    tool_registry = ToolRegistry()
    tool_registry.register(CALCULATOR_SCHEMA, calculator)

    result = tool_registry.execute_safe(tool_call)

    assert result["tool_call_id"] == "call_001"
    assert result["name"] == "calculator"
    assert result["ok"] is False
    assert result["error"]["type"] == "ValueError"
    assert "nonzero" in result["error"]["message"]
    assert "result" not in result
def test_execute_unsafe_calculator():
    tool_call = {
        "id": "call_001",
        "name": "calculator",
        "arguments": {"operation": "multiply", "a": "12", "b": 8},
    }
    tool_registry = ToolRegistry()
    tool_registry.register(CALCULATOR_SCHEMA, calculator)
    result=tool_registry.execute_safe(tool_call)
    assert result["tool_call_id"] == "call_001"
    assert result["name"] == "calculator"
    assert result["ok"] is False
    assert result["error"]["type"] == "TypeError"
    assert "result" not in result
def test_execute_unsafe_unknown_tool():
    tool_call = {
        "id": "call_001",
        "name": "unknown",
        "arguments": {"operation": "multiply", "a": "12", "b": 8},
    }
    tool_registry = ToolRegistry()
    tool_registry.register(CALCULATOR_SCHEMA, calculator)
    result = tool_registry.execute_safe(tool_call)
    assert result["tool_call_id"] == "call_001"
    assert result["name"] == "unknown"
    assert result["ok"] is False
    assert result["error"]["type"] == "ValueError"
    assert "result" not in result
def test_execute_safe_rejects_list_call():
    tool_call = [{
        "id": "call_001",
        "name": "calculator",
        "arguments": {"operation": "multiply", "a": 12, "b": 8},}
    ]
    tool_registry = ToolRegistry()
    tool_registry.register(CALCULATOR_SCHEMA, calculator)
    result = tool_registry.execute_safe(tool_call)
    assert result["tool_call_id"] is None
    assert result["name"] is None
    assert result["ok"] is False
    assert result["error"]["type"] == "TypeError"
    assert result["error"]["message"] == "Tool call must be a dict"
    assert "result" not in result
@pytest.mark.parametrize(
    "tool_call,expected_error,message",
    [
        ([], TypeError, "Tool call must be a dict"),
        (
            {"name": "calculator", "arguments": {}},
            ValueError,
            "Missing tool call field: id",
        ),
        (
            {"id": "call_001", "arguments": {}},
            ValueError,
            "Missing tool call field: name",
        ),
        (
            {"id": "call_001", "name": "calculator"},
            ValueError,
            "Missing tool call field: arguments",
        ),
        (
            {"id": "call_001", "name": "calculator", "arguments": []},
            TypeError,
            "Arguments for tool must be a dict",
        ),
        (
            {"id": 123, "name": "calculator", "arguments": {}},
            TypeError,
            "Id and Name must be strings",
        ),
        (
            {"id": "call_001", "name": 123, "arguments": {}},
            TypeError,
            "Id and Name must be strings",
        ),
        (
            {"id": "", "name": "calculator", "arguments": {}},
            ValueError,
            "Id and Name must not be empty",
        ),
        (
            {"id": "call_001", "name": "   ", "arguments": {}},
            ValueError,
            "Id and Name must not be empty",
        ),
    ],
)
def test_execute_rejects_invalid_call_format(
    tool_call, expected_error, message
):
    registry = ToolRegistry()

    with pytest.raises(expected_error, match=message):
        registry.execute(tool_call)


def test_execute_safe_rejects_list_call():
    registry = ToolRegistry()

    result = registry.execute_safe([
        {
            "id": "call_001",
            "name": "calculator",
            "arguments": {"operation": "multiply", "a": 12, "b": 8},
        }
    ])

    assert result == {
        "tool_call_id": None,
        "name": None,
        "ok": False,
        "error": {
            "type": "TypeError",
            "message": "Tool call must be a dict",
        },
    }


def test_execute_safe_handles_empty_call():
    registry = ToolRegistry()

    result = registry.execute_safe({})

    assert result == {
        "tool_call_id": None,
        "name": None,
        "ok": False,
        "error": {
            "type": "ValueError",
            "message": "Missing tool call field: id",
        },
    }
