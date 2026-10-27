"""Check CLI preference forwarding without loading retrieval or model resources."""

from unittest.mock import Mock

import pytest
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


@pytest.mark.parametrize("mode", ["dense", "bm25", "hybrid"])
@pytest.mark.parametrize("rerank", [False, True], ids=["plain", "reranked"])
def test_cli_connects_configured_mode_reranker_and_pipeline(
    monkeypatch, capsys, entrypoint_case, mode, rerank,
):
    case = entrypoint_case(mode, rerank)
    config = case.config
    retriever = Mock()
    retriever.retrieve.return_value = case.candidates
    retriever_type = Mock(return_value=retriever)
    reranker = Mock()
    reranker.rerank.return_value = list(reversed(case.candidates))
    reranker_type = Mock(return_value=reranker)
    generator = Mock()
    generator.generate.return_value = "Supported answer."
    generator_type = Mock(return_value=generator)
    monkeypatch.setattr(cli, "FaissRetriever", retriever_type)
    monkeypatch.setattr(cli, "CrossEncoderReranker", reranker_type)
    monkeypatch.setattr(cli, "HuggingFaceGenerator", generator_type)

    assert cli.main(["--config", str(case.path), "--question", "Find evidence."]) == 0

    retriever_type.assert_called_once_with(
        index_path=config.paths.faiss_index, chunks_path=config.paths.chunks,
        embedding_model="fake-embedding", normalize_embeddings=False, mode=mode,
    )
    retriever.retrieve.assert_called_once_with("Find evidence.", top_k=20)
    generator_type.assert_called_once_with(
        "fake-generator", max_new_tokens=13, temperature=0.0,
    )
    if rerank:
        reranker_type.assert_called_once_with(
            model_name="fake-reranker", max_length=128, batch_size=2,
        )
        reranker.rerank.assert_called_once_with("Find evidence.", case.candidates, top_k=3)
        included, excluded = ("b", "c"), "a"
    else:
        reranker_type.assert_not_called()
        included, excluded = ("a", "b"), "c"

    prompt = generator.generate.call_args.args[0]
    assert all(f"Evidence {cid}" in prompt for cid in included)
    assert f"Evidence {excluded}" not in prompt
    assert generator.generate.call_count == 1
    assert "Supported answer." in capsys.readouterr().out
