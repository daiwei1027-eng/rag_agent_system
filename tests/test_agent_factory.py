"""Agent factory wiring through the real registry and document-search handler."""

from unittest.mock import Mock

import pytest

from rag_agent_system.agents import factory


@pytest.mark.parametrize("mode", ["dense", "bm25", "hybrid"])
@pytest.mark.parametrize("rerank", [False, True], ids=["plain", "reranked"])
def test_agent_factory_connects_configured_mode_and_search_tool(
    monkeypatch, entrypoint_case, mode, rerank,
):
    case = entrypoint_case(mode, rerank)
    config = case.config
    retriever = Mock()
    retriever.retrieve.side_effect = lambda query, top_k: case.candidates[:top_k]
    retriever_type = Mock(return_value=retriever)
    reranker = Mock()
    reranker.rerank.side_effect = (
        lambda query, documents, top_k: list(reversed(documents))[:top_k]
    )
    reranker_type = Mock(return_value=reranker)
    client = Mock()
    client_type = Mock(return_value=client)
    monkeypatch.setattr(factory, "FaissRetriever", retriever_type)
    monkeypatch.setattr(factory, "CrossEncoderReranker", reranker_type)
    monkeypatch.setattr(factory, "LocalLLMClient", client_type)

    agent = factory.build_agent(config)
    observation = agent.registry.execute({
        "id": "search-1", "name": "search_documents",
        "arguments": {"query": "Find evidence.", "top_k": 2},
    })

    retriever_type.assert_called_once_with(
        index_path=config.paths.faiss_index, chunks_path=config.paths.chunks,
        embedding_model="fake-embedding", normalize_embeddings=False, mode=mode,
    )
    assert agent.llm is client
    client_type.assert_called_once_with("fake-agent", max_new_tokens=17)
    client.chat.assert_not_called()
    assert {schema["name"] for schema in agent.registry.get_schemas()} == {
        "search_documents", "time", "calculator",
    }
    assert observation["ok"] is True
    if rerank:
        reranker_type.assert_called_once_with(
            "fake-reranker", max_length=128, batch_size=2,
        )
        retriever.retrieve.assert_called_once_with("Find evidence.", top_k=20)
        reranker.rerank.assert_called_once_with(
            "Find evidence.", documents=case.candidates, top_k=2,
        )
        expected_ids = ["c", "b"]
    else:
        reranker_type.assert_not_called()
        retriever.retrieve.assert_called_once_with("Find evidence.", top_k=2)
        expected_ids = ["a", "b"]
    assert [item["chunk_id"] for item in observation["result"]] == expected_ids


def test_dataset_agents_receive_separate_search_schemas(monkeypatch, entrypoint_case):
    case = entrypoint_case("dense", False)
    for name in ("FaissRetriever", "CrossEncoderReranker", "LocalLLMClient"):
        monkeypatch.setattr(factory, name, Mock())

    stories = factory.build_agent(case.config)
    sec = factory.build_agent(case.config, dataset="sec")

    def search_schema(agent):
        return next(schema for schema in agent.registry.get_schemas()
                    if schema["name"] == "search_documents")

    story_schema = search_schema(stories)
    sec_schema = search_schema(sec)
    assert "TinyStories" in story_schema["description"]
    assert "SEC" in sec_schema["description"]
    assert "TinyStories" not in sec_schema["description"]
    sec_schema["parameters"]["properties"]["top_k"]["maximum"] = 999
    assert story_schema["parameters"]["properties"]["top_k"]["maximum"] == 10


def test_factory_rejects_unknown_dataset_before_components(monkeypatch, entrypoint_case):
    case = entrypoint_case("dense", False)
    constructors = [Mock() for _ in range(3)]
    for name, constructor in zip(
        ("FaissRetriever", "CrossEncoderReranker", "LocalLLMClient"), constructors,
    ):
        monkeypatch.setattr(factory, name, constructor)

    with pytest.raises(ValueError, match="Unknown dataset"):
        factory.build_agent(case.config, dataset="unknown")
    for constructor in constructors:
        constructor.assert_not_called()
