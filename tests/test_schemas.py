from rag_agent_system.tools.schemas import CALCULATOR_SCHEMA,SEARCH_DOCUMENTS_SCHEMA,TIME_SCHEMA
from rag_agent_system.tools.validation import validate_arguments
import pytest
def test_calculator_accepts_zero():
    para = {"operation": "add", "a": 0, "b": 2}
    validate_arguments(para, CALCULATOR_SCHEMA["parameters"])


def test_calculator_rejects_string_number():
    para = {"operation": "add", "a": "12", "b": 2}
    with pytest.raises(TypeError):
        validate_arguments(para, CALCULATOR_SCHEMA["parameters"])

def test_search_rejects_boolean_top_k():
    para = {"query": "RAG", "top_k": True}
    with pytest.raises(TypeError):
        validate_arguments(para, SEARCH_DOCUMENTS_SCHEMA["parameters"])

def test_time_rejects_numeric_timezone():
    para = {"timezone": 8}
    with pytest.raises(TypeError):
        validate_arguments(para, TIME_SCHEMA["parameters"])

@pytest.mark.parametrize("timezone", ["UTC", "Asia/Shanghai"])
def test_time_accepts_supported_timezone(timezone):
    validate_arguments(
        {"timezone": timezone},
        TIME_SCHEMA["parameters"],
    )
def test_time_rejects_unexpected_timezone():
    para = {"timezone": "abc"}
    with pytest.raises(ValueError):
        validate_arguments(para, TIME_SCHEMA["parameters"])
def test_calculator_rejects_unexpected_operation():
    para = {"operation": "power", "a": 2, "b": 2}
    with pytest.raises(ValueError):
        validate_arguments(para, CALCULATOR_SCHEMA["parameters"])
@pytest.mark.parametrize("top_k", [1,10,3])
def test_search_accepts_supported_query_top_k(top_k):
    validate_arguments(
        {"query": "RAG", "top_k": top_k},
        SEARCH_DOCUMENTS_SCHEMA["parameters"],
    )

@pytest.mark.parametrize("top_k", [0, 11])
def test_search_rejects_out_of_range_top_k(top_k):
    para = {"query": "RAG", "top_k": top_k}
    with pytest.raises(ValueError):
        validate_arguments(para, SEARCH_DOCUMENTS_SCHEMA["parameters"])
def test_search_rejects_empty_query():
    para = {"query": "", "top_k": 3}
    with pytest.raises(ValueError):
        validate_arguments(para, SEARCH_DOCUMENTS_SCHEMA["parameters"])

def test_rejects_non_dict_arguments():
    para = {"UTC"}
    with pytest.raises(TypeError):
        validate_arguments(para, SEARCH_DOCUMENTS_SCHEMA["parameters"])
def test_rejects_missing_required_argument():
    para = {"query": "RAG"}
    with pytest.raises(ValueError, match="top_k"):
        validate_arguments(para, SEARCH_DOCUMENTS_SCHEMA["parameters"])
def test_rejects_additional_argument():
    para = {"timezone": "UTC", "top_k": 3}
    with pytest.raises(ValueError, match="top_k"):
        validate_arguments(para, TIME_SCHEMA["parameters"])

