"""Exercise the real benchmark loader and evaluation entrypoint with fake models."""

import csv
import json
from types import SimpleNamespace

import pytest
import yaml

from rag_agent_system.evaluation.benchmark import sha256_file
from rag_agent_system.models import DocumentChunk, RetrievedChunk
from scripts import eval_retrieval as entry


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture
def case(tmp_path):
    paths = {name: tmp_path / filename for name, filename in {
        "chunks": "chunks.json", "faiss_index": "index.faiss",
        "queries": "queries.jsonl", "manifest": "manifest.json", "absence": "absence.json",
    }.items()}
    paths["chunks"].write_text(json.dumps([
        {"chunk_id": "a", "text": "Alpha evidence", "metadata": {"faiss_id": 0}},
        {"chunk_id": "b", "text": "Beta evidence", "metadata": {"faiss_id": 1}},
    ]), encoding="utf-8")
    paths["faiss_index"].write_bytes(b"fingerprinted placeholder; fake retriever never reads FAISS")
    queries = [
        {"query_id": "missing", "query": "Unknown", "answerable": False,
         "annotation_status": "reviewed", "relevant_chunk_ids": [], "evidence": [],
         "absence_evidence": {"file": "absence.json", "scope_chunk_ids": ["a", "b"]}},
        {"query_id": "alpha-case", "query": "Alpha", "answerable": True,
         "annotation_status": "reviewed", "relevant_chunk_ids": ["a"],
         "evidence": [{"chunk_id": "a", "quote": "Alpha evidence"}]},
        {"query_id": "beta-case", "query": "Beta", "answerable": True,
         "annotation_status": "reviewed", "relevant_chunk_ids": ["b"],
         "evidence": [{"chunk_id": "b", "quote": "Beta evidence"}]},
    ]
    paths["absence"].write_text(json.dumps([
        {"query_id": "missing", "annotation_status": "reviewed", "scope_chunk_ids": ["a", "b"]},
    ]), encoding="utf-8")
    raw_config = {
        "project": {}, "paths": {
            "chunks": str(paths["chunks"]), "faiss_index": str(paths["faiss_index"]),
            "benchmark_queries": str(paths["queries"]),
            "benchmark_manifest": str(paths["manifest"]), "absence_evidence": str(paths["absence"]),
        },
        "retrieval": {"embedding_model": "fake-model", "normalize_embeddings": True,
                      "top_k": 20, "mode": "dense"},
        "reranker": {"enabled": False, "model_name": "fake-reranker", "top_k": 5},
        "generation": {"model_name": "not-used"}, "context": {"top_k": 5},
    }
    config_path = tmp_path / "settings.yaml"

    def write():
        paths["queries"].write_text("".join(json.dumps(q) + "\n" for q in queries), encoding="utf-8")
        manifest = {
            "version": "synthetic-v1", "dataset_sha256": sha256_file(paths["queries"]),
            "corpus_chunk_count": 2, "question_count": len(queries),
            "answerable_count": sum(q["answerable"] for q in queries),
            "unanswerable_count": sum(not q["answerable"] for q in queries),
            "embedding_model": "fake-model", "normalize_embeddings": True,
            "asset_binding": {
                "chunks": sha256_file(paths["chunks"]),
                "faiss_index": sha256_file(paths["faiss_index"]),
                "absence_evidence": sha256_file(paths["absence"]),
            },
        }
        paths["manifest"].write_text(json.dumps(manifest), encoding="utf-8")
        config_path.write_text(yaml.safe_dump(raw_config), encoding="utf-8")

    write()
    return SimpleNamespace(paths=paths, queries=queries, raw=raw_config, write=write,
                           config=config_path, output=tmp_path / "run")


def install_models(monkeypatch, case, *, fail_phase=None, exception=RuntimeError):
    calls = []

    class Retriever:
        def __init__(self, **kwargs):
            # Config/checkpoints must exist before constructing any model backend.
            assert read_json(case.output / "config.json")["retrieval_mode"] == kwargs["mode"]
            assert read_json(case.output / "per_query.json") == []
            calls.append(("construct", kwargs["mode"]))

        def prepare(self):
            calls.append(("prepare", "retriever"))

        def retrieve(self, query, top_k):
            calls.append(("retrieve", query, top_k))
            if query == "Beta":
                assert len(read_json(case.output / "per_query.json")) == 1
                if fail_phase == "retrieve":
                    raise exception("controlled failure")
            ids = ["b", "a"] if query == "Alpha" else ["a", "b"]
            return [RetrievedChunk(DocumentChunk(i, i), 1.0 / rank, rank)
                    for rank, i in enumerate(ids, 1)]

    class Reranker:
        def __init__(self, **kwargs):
            assert case.raw["reranker"]["enabled"], "disabled reranker was constructed"
            calls.append(("construct", "reranker"))

        def prepare(self):
            calls.append(("prepare", "reranker"))

        def rerank(self, query, documents, top_k):
            calls.append(("rerank", query, top_k))
            if query == "Beta" and fail_phase == "rerank":
                raise exception("controlled failure")
            return list(reversed(documents))[:top_k]

    monkeypatch.setattr(entry, "DocumentRetriever", Retriever)
    monkeypatch.setattr(entry, "CrossEncoderReranker", Reranker)
    return calls


@pytest.mark.parametrize("mode,rerank", [("dense", False), ("dense", True), ("bm25", False)])
def test_small_benchmark_modes_and_optional_rerank(case, monkeypatch, mode, rerank):
    # The fake BM25 case only proves mode forwarding, not BM25 implementation.
    case.raw["retrieval"]["mode"] = mode
    case.raw["reranker"]["enabled"] = rerank
    case.write()
    calls = install_models(monkeypatch, case)
    assert entry.main(["--config", str(case.config), "--run-dir", str(case.output),
                       "--candidate-top-k", "7"]) == 0
    summary = read_json(case.output / "summary.json")
    config = read_json(case.output / "config.json")
    rows = read_json(case.output / "per_query.json")
    assert summary["scored_count"] == 2 and summary["excluded_count"] == 1
    assert summary["warmup_query_id"] == "alpha-case"
    assert summary["retrieval_mode"] == mode
    names = ["Without Rerank", "With Rerank"] if rerank else ["Without Rerank"]
    assert list(summary["metrics"]) == names
    assert summary["metrics"]["Without Rerank"]["mrr_at_20"] == 0.5
    assert config["Retrieved_top_k"] == 7
    assert config["Rerank_top_k"] == (7 if rerank else None)
    assert config["Total_query_count"] == 3 and config["Query_count"] == 2
    assert ("construct", mode) in calls
    assert [(c[1], c[2]) for c in calls if c[0] == "retrieve"] == [
        ("Alpha", 7), ("Alpha", 7), ("Beta", 7)]
    if rerank:
        assert summary["metrics"]["With Rerank"]["mrr_at_20"] == 1.0
        assert summary["reranker_load_seconds"] >= 0
        assert len([c for c in calls if c[0] == "rerank"]) == 3
    else:
        assert summary["reranker_load_seconds"] is None
        assert all(row["reranked_ids"] is None for row in rows)
        assert not any(c[0] == "rerank" or c == ("construct", "reranker") for c in calls)
    assert read_json(case.output / "run_status.json") == {"status": "complete", "completed_count": 2}
    assert not (case.output / "failure.json").exists()
    assert config["asset_sha256"]["queries"] == sha256_file(case.paths["queries"])
    with (case.output / "total.csv").open(encoding="utf-8-sig", newline="") as handle:
        assert [row["run"] for row in csv.DictReader(handle)] == names


def test_check_only_does_not_construct_models_or_create_output(case, monkeypatch, capsys):
    calls = install_models(monkeypatch, case)
    assert entry.main(["--config", str(case.config), "--check-only",
                       "--run-dir", str(case.output)]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["query_count"] == 3 and result["candidate_top_k"] == 20
    assert not calls and not case.output.exists()


def test_all_unanswerable_rejected_before_outputs_or_models(case, monkeypatch):
    case.queries[:] = case.queries[:1]
    case.write()
    calls = install_models(monkeypatch, case)
    with pytest.raises(ValueError, match="No answerable"):
        entry.main(["--config", str(case.config), "--run-dir", str(case.output)])
    assert not calls and not case.output.exists()


@pytest.mark.parametrize("phase,exception", [
    ("retrieve", RuntimeError), ("rerank", RuntimeError), ("retrieve", KeyboardInterrupt),
])
def test_failure_preserves_completed_questions_and_diagnostics(case, monkeypatch, phase, exception):
    case.raw["reranker"]["enabled"] = phase == "rerank"
    case.write()
    install_models(monkeypatch, case, fail_phase=phase, exception=exception)
    with pytest.raises(exception, match="controlled failure"):
        entry.main(["--config", str(case.config), "--run-dir", str(case.output)])
    assert [r["query_id"] for r in read_json(case.output / "per_query.json")] == ["alpha-case"]
    failure = read_json(case.output / "failure.json")
    assert failure["phase"] == phase and failure["query_id"] == "beta-case"
    assert failure["completed_count"] == 1
    assert failure["status"] == ("interrupted" if exception is KeyboardInterrupt else "failed")
    assert failure["baseline_ids"] == (["a", "b"] if phase == "rerank" else [])
    assert read_json(case.output / "run_status.json") == failure
    assert not (case.output / "summary.json").exists()


def test_asset_mismatch_stops_before_outputs(case, monkeypatch):
    case.paths["chunks"].write_text("[]", encoding="utf-8")
    calls = install_models(monkeypatch, case)
    with pytest.raises(ValueError, match="asset mismatch"):
        entry.main(["--config", str(case.config), "--run-dir", str(case.output)])
    assert not calls and not case.output.exists()


def test_existing_run_is_not_overwritten(case, monkeypatch):
    case.output.mkdir()
    marker = case.output / "original.txt"
    marker.write_text("keep", encoding="utf-8")
    calls = install_models(monkeypatch, case)
    with pytest.raises(FileExistsError):
        entry.main(["--config", str(case.config), "--run-dir", str(case.output)])
    assert marker.read_text(encoding="utf-8") == "keep"
    assert list(case.output.iterdir()) == [marker] and not calls
