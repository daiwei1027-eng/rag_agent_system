"""Dataset descriptions share one tool contract without sharing mutable schema state."""

import pytest

from rag_agent_system.tools.schemas import (
    SEARCH_DOCUMENTS_SCHEMA,
    build_search_documents_schema,
)
from rag_agent_system.tools.validation import validate_arguments


@pytest.mark.parametrize(
    "dataset,label,other", [("tinystories", "TinyStories", "SEC"),
                             ("sec", "SEC", "TinyStories")],
)
def test_dataset_description_preserves_search_contract(dataset, label, other):
    schema = build_search_documents_schema(dataset)

    assert schema["name"] == "search_documents"
    assert label in schema["description"] and other not in schema["description"]
    assert schema["parameters"] == SEARCH_DOCUMENTS_SCHEMA["parameters"]
    validate_arguments({"query": "Find evidence", "top_k": 5}, schema["parameters"])
    assert build_search_documents_schema() == SEARCH_DOCUMENTS_SCHEMA


def test_schema_copies_isolate_nested_changes_and_base_template():
    first = build_search_documents_schema("sec")
    other = build_search_documents_schema("tinystories")
    first["description"] = "modified"
    first["parameters"]["properties"]["top_k"]["maximum"] = 999
    first["parameters"]["required"].append("unexpected")

    for schema in [other, SEARCH_DOCUMENTS_SCHEMA, build_search_documents_schema("sec")]:
        assert schema["description"] != "modified"
        assert schema["parameters"]["properties"]["top_k"]["maximum"] == 10
        assert schema["parameters"]["required"] == ["query", "top_k"]


def test_unknown_dataset_is_rejected():
    with pytest.raises(ValueError, match="Unknown dataset"):
        build_search_documents_schema("unknown")
