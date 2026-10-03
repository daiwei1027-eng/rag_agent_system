"""Check CLI preference forwarding without loading retrieval or model resources."""

import pytest
from rag_agent_system.retrieval import (
    CrossEncoderReranker,
    FaissRetriever,
)
from rag_agent_system import cli
from rag_agent_system.models import RAGResult


@pytest.mark.parametrize("instruction", [None, "Answer briefly in Chinese."])
def test_cli_forwards_additional_instruction(monkeypatch, capsys, instruction):
    calls = []

    class FakePipeline:
        def __init__(self, **kwargs):
            pass

        def query(self, question, *, additional_instruction=None):
            calls.append((question, additional_instruction))
            return RAGResult(question=question, answer="Lily.", sources=())

    for name in (
            "FaissRetriever",
            "CrossEncoderReranker",
            "ContextBuilder",
            "PromptBuilder",
            "HuggingFaceGenerator",
    ):
        monkeypatch.setattr(cli, name, lambda *args, **kwargs: object())
    monkeypatch.setattr(cli, "RAGPipeline", FakePipeline)

    args = ["--question", "Who found the needle?"]
    if instruction is not None:
        args.extend(["--additional-instruction", instruction])

    assert cli.main(args) == 0
    assert calls == [("Who found the needle?", instruction)]
    assert "Lily." in capsys.readouterr().out
