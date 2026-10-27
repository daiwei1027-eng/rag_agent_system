"""HTTP dataset routing and Agent caching, without model initialization."""

import logging
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from rag_agent_system import api
from rag_agent_system.config import load_config


@pytest.fixture
def service(monkeypatch):
    created = {}

    class FakeAgent:
        def __init__(self, config, dataset):
            self.config = config
            self.dataset = dataset
            self.prompts = []

        def run(self, prompt):
            self.prompts.append(prompt)
            return {"status": "completed", "answer": self.dataset,
                    "trace": [], "error": None}

    def build(config, *, dataset):
        agent = FakeAgent(config, dataset)
        created[dataset] = agent
        return agent

    loader = Mock(wraps=api.load_config)
    builder = Mock(side_effect=build)
    monkeypatch.setattr(api, "load_config", loader)
    monkeypatch.setattr(api, "build_agent", builder)
    with TestClient(api.app, raise_server_exceptions=False) as client:
        # Startup reads the legacy config only for logging; count request loads separately.
        loader.reset_mock()
        yield SimpleNamespace(client=client, created=created, builder=builder,
                              loader=loader, build=build)


@pytest.mark.parametrize("dataset", [None, "tinystories", "sec"],
                         ids=["legacy-default", "explicit-stories", "explicit-sec"])
def test_request_selects_matching_config_agent_prompt_and_log(service, caplog, dataset):
    selected = dataset or "tinystories"
    payload = {"question": "  Find evidence.  "}
    if dataset is not None:
        payload["dataset"] = dataset
    caplog.set_level(logging.INFO, logger=api.__name__)

    response = service.client.post("/query", json=payload)

    assert response.status_code == 200
    assert response.json() == {"status": "completed", "answer": selected,
                               "trace": [], "error": None}
    path = Path("configs/SEC_v1.yaml" if selected == "sec" else "configs/chunking_v2.yaml")
    service.loader.assert_called_once_with(path)
    agent = service.created[selected]
    assert agent.config == load_config(path)
    service.builder.assert_called_once_with(agent.config, dataset=selected)
    assert api.app.state.agents == {selected: agent}
    assert len(agent.prompts) == 1
    assert agent.prompts[0].endswith("问题：Find evidence.")
    corpus, other = ("SEC", "TinyStories") if selected == "sec" else ("TinyStories", "SEC")
    assert corpus in agent.prompts[0] and other not in agent.prompts[0]
    assert any(f"dataset={selected}" in record.getMessage() for record in caplog.records)


def test_switching_datasets_reuses_their_separate_cached_agents(service):
    for dataset in ("sec", "tinystories", "sec", "tinystories"):
        response = service.client.post("/query", json={"question": "Find evidence.",
                                                       "dataset": dataset})
        assert response.status_code == 200
        assert response.json()["answer"] == dataset

    assert service.builder.call_count == service.loader.call_count == 2
    assert set(api.app.state.agents) == {"sec", "tinystories"}
    assert api.app.state.agents["sec"] is service.created["sec"]
    assert api.app.state.agents["tinystories"] is service.created["tinystories"]
    assert service.created["sec"] is not service.created["tinystories"]
    assert all(len(agent.prompts) == 2 for agent in service.created.values())


@pytest.mark.parametrize("payload", [
    {"question": "Find evidence.", "dataset": "unknown"},
    {"question": " \n\t ", "dataset": "sec"},
    {"dataset": "sec"},
], ids=["unknown-dataset", "blank-question", "missing-question"])
def test_invalid_requests_fail_before_agent_creation(service, payload):
    assert service.client.post("/query", json=payload).status_code == 422
    service.builder.assert_not_called()
    service.loader.assert_not_called()
    assert api.app.state.agents == {}


def test_health_does_not_create_agents(service):
    response = service.client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    service.builder.assert_not_called()
    assert api.app.state.agents == {}


def test_failed_agent_creation_leaves_cache_empty_and_allows_retry(service):
    attempts = []

    def fail_once(config, *, dataset):
        attempts.append(dataset)
        if len(attempts) == 1:
            raise RuntimeError("controlled Agent construction failure")
        return service.build(config, dataset=dataset)

    service.builder.side_effect = fail_once
    payload = {"question": "Find evidence.", "dataset": "sec"}
    assert service.client.post("/query", json=payload).status_code == 500
    assert api.app.state.agents == {}

    response = service.client.post("/query", json=payload)
    assert response.status_code == 200
    assert response.json()["answer"] == "sec"
    assert attempts == ["sec", "sec"]
    assert api.app.state.agents["sec"] is service.created["sec"]
