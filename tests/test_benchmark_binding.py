"""Reject mixed versions and invalid annotations before any model inference."""

from dataclasses import replace
import json
from types import SimpleNamespace

import pytest

from rag_agent_system.config import PathConfig
from rag_agent_system.evaluation.benchmark import load_benchmark, read_scope, sha256_file


@pytest.fixture
def bundle(tmp_path):
    paths = PathConfig(
        faiss_index=tmp_path / "index.faiss", chunks=tmp_path / "chunks.json",
        benchmark_queries=tmp_path / "queries.jsonl", benchmark_manifest=tmp_path / "manifest.json",
        absence_evidence=tmp_path / "absence.json",
    )
    paths.faiss_index.write_bytes(b"test index fingerprint; no inference")
    paths.chunks.write_text(json.dumps([
        {"chunk_id": "new-a", "text": "Lily found a needle.", "metadata": {"faiss_id": 0}},
        {"chunk_id": "new-b", "text": "Her mother sewed the shirt.", "metadata": {"faiss_id": 1}},
    ]), encoding="utf-8")
    queries = [
        {"query_id": "q001", "query": "Who found a needle?", "annotation_status": "reviewed",
         "answerable": True, "relevant_chunk_ids": ["new-a"],
         "evidence": [{"chunk_id": "new-a", "quote": "Lily found a needle."}]},
        {"query_id": "q041", "query": "What needle manufacturer?", "annotation_status": "reviewed",
         "answerable": False, "relevant_chunk_ids": [], "evidence": [],
         "absence_evidence": {"file": "absence.json", "story_chunk_ids": ["new-a", "new-b"]}},
    ]
    absence = [{"query_id": "q041", "annotation_status": "reviewed",
                "story_chunk_ids": ["new-a", "new-b"]}]

    def write():
        paths.benchmark_queries.write_text("".join(json.dumps(q) + "\n" for q in queries), encoding="utf-8")
        paths.absence_evidence.write_text(json.dumps(absence), encoding="utf-8")
        manifest = {
            "dataset_sha256": sha256_file(paths.benchmark_queries), "corpus_chunk_count": 2,
            "question_count": 2, "answerable_count": 1, "unanswerable_count": 1,
            "asset_binding": {name: sha256_file(path) for name, path in {
                "faiss_index": paths.faiss_index, "chunks": paths.chunks,
                "absence_evidence": paths.absence_evidence,
            }.items()},
            "embedding_model": "test-model", "normalize_embeddings": True,
        }
        paths.benchmark_manifest.write_text(json.dumps(manifest), encoding="utf-8")

    write()
    config = SimpleNamespace(paths=paths, retrieval=SimpleNamespace(
        embedding_model="test-model", normalize_embeddings=True,
    ))
    return config, queries, absence, write


@pytest.mark.parametrize("query_key,external_key", [
    ("story_chunk_ids", "story_chunk_ids"),
    ("scope_chunk_ids", "scope_chunk_ids"),
    ("scope_chunk_ids", "story_chunk_ids"),
    ("story_chunk_ids", "scope_chunk_ids"),
])
def test_matching_bundle_loads_without_models(bundle, query_key, external_key):
    config, queries, absence, write = bundle
    record = queries[1]["absence_evidence"]
    record[query_key] = record.pop("story_chunk_ids")
    absence[0][external_key] = absence[0].pop("story_chunk_ids")
    write()
    assert load_benchmark(config)["queries"] == queries


@pytest.mark.parametrize("asset", ["chunks", "faiss_index", "benchmark_queries"])
def test_reject_mixed_version_files(bundle, asset, tmp_path):
    config, _, _, _ = bundle
    wrong = tmp_path / "other-version"
    wrong.write_text("wrong version", encoding="utf-8")
    config.paths = replace(config.paths, **{asset: wrong})
    with pytest.raises(ValueError, match="hash|asset mismatch"):
        load_benchmark(config)


@pytest.mark.parametrize("fault, error", [
    ("pending", "Unreviewed query"), ("unknown_id", "Unknown relevant chunk"),
    ("quote", "Invalid evidence quote"), ("negative_scope", "Unknown absence scope chunk"),
])
def test_reject_invalid_labels_even_with_updated_fingerprints(bundle, fault, error):
    config, queries, absence, write = bundle
    if fault == "pending":
        queries[0]["annotation_status"] = "pending_migration_review"
    elif fault == "unknown_id":
        queries[0]["relevant_chunk_ids"] = ["old-0"]
    elif fault == "quote":
        queries[0]["evidence"][0]["quote"] = "unsupported claim"
    else:
        queries[1]["absence_evidence"]["story_chunk_ids"] = ["old-0"]
        absence[0]["story_chunk_ids"] = ["old-0"]
    write()
    with pytest.raises(ValueError, match=error):
        load_benchmark(config)


@pytest.mark.parametrize("record,error", [
    ({}, "non-empty list"),
    ({"scope_chunk_ids": []}, "non-empty list"),
    ({"scope_chunk_ids": "new-a"}, "non-empty list"),
    ({"scope_chunk_ids": [1]}, "non-empty list"),
    ({"scope_chunk_ids": ["new-a"], "story_chunk_ids": ["new-a"]}, "Ambiguous"),
])
def test_invalid_or_ambiguous_scope_rejected(record, error):
    with pytest.raises(ValueError, match=error):
        read_scope(record)


@pytest.mark.parametrize("fault,error", [
    ("missing", "Missing absence evidence"),
    ("different", "Inconsistent absence evidence"),
])
def test_missing_or_different_external_scope_rejected(bundle, fault, error):
    config, queries, absence, write = bundle
    record = queries[1]["absence_evidence"]
    record["scope_chunk_ids"] = record.pop("story_chunk_ids")
    if fault == "missing":
        absence.clear()
    else:
        absence[0].pop("story_chunk_ids")
        absence[0]["scope_chunk_ids"] = ["new-a"]
    write()
    with pytest.raises(ValueError, match=error):
        load_benchmark(config)
