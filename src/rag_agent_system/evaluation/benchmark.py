"""Validate that reviewed questions and retrieval assets belong to one version."""

import hashlib
import json
from pathlib import Path

from rag_agent_system.config import AppConfig
from rag_agent_system.ingestion import load_chunks
from rag_agent_system.paths import project_root


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        while block := file.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def read_scope(record: dict) -> list[str]:
    if "scope_chunk_ids" in record and "story_chunk_ids" in record:
        raise ValueError("Ambiguous absence evidence scope")
    scope = record.get("scope_chunk_ids", record.get("story_chunk_ids"))
    if (
        not isinstance(scope, list)
        or not scope
        or any(not isinstance(chunk_id, str) for chunk_id in scope)
    ):
        raise ValueError("Absence evidence scope must be a non-empty list of chunk IDs")
    return scope


def load_benchmark(config: AppConfig) -> dict:
    root = project_root() / "data/benchmark"
    queries_path = config.paths.benchmark_queries or root / "tinystories_queries.jsonl"
    manifest_path = config.paths.benchmark_manifest or root / "tinystories_benchmark_manifest.json"
    absence_path = config.paths.absence_evidence or root / "tinystories_absence_evidence.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    if sha256_file(queries_path) != manifest["dataset_sha256"]:
        raise ValueError("Benchmark hash does not match manifest")
    paths = {"chunks": config.paths.chunks, "faiss_index": config.paths.faiss_index,
             "absence_evidence": absence_path}
    binding = manifest.get("asset_binding")
    if binding is not None:
        for name, path in paths.items():
            if name not in binding or sha256_file(path) != binding[name]:
                raise ValueError(f"Benchmark asset mismatch: {name}")
        if config.retrieval.embedding_model != manifest["embedding_model"]:
            raise ValueError("Benchmark embedding model mismatch")
        if config.retrieval.normalize_embeddings != manifest["normalize_embeddings"]:
            raise ValueError("Benchmark embedding normalization mismatch")
    else:
        legacy_chunks = [file for file in manifest.get("files", [])
                         if Path(file["path"].replace("\\", "/")).name == config.paths.chunks.name]
        if len(legacy_chunks) != 1 or sha256_file(config.paths.chunks) != legacy_chunks[0]["sha256"]:
            raise ValueError("Benchmark asset mismatch: chunks")
    queries = [json.loads(line) for line in queries_path.read_text(encoding="utf-8-sig").splitlines()
               if line.strip()]
    chunks = load_chunks(config.paths.chunks)
    if len(chunks) != manifest["corpus_chunk_count"]:
        raise ValueError("Benchmark corpus chunk count mismatch")
    absence = json.loads(absence_path.read_text(encoding="utf-8-sig"))
    absence_by_id = {item["query_id"]: item for item in absence}
    if len(absence_by_id) != len(absence):
        raise ValueError("Duplicate absence evidence query ID")
    seen = set()
    for item in queries:
        query_id = item["query_id"]
        if query_id in seen:
            raise ValueError(f"Duplicate query ID: {query_id}")
        seen.add(query_id)
        if item["annotation_status"] != "reviewed":
            raise ValueError(f"Unreviewed query: {query_id}")
        relevant = item["relevant_chunk_ids"]
        if type(item["answerable"]) is not bool or item["answerable"] != bool(relevant):
            raise ValueError(f"Inconsistent annotation: {query_id}")
        if not isinstance(relevant, list) or any(not isinstance(i, str) or i not in chunks for i in relevant):
            raise ValueError(f"Unknown relevant chunk ID: {query_id}")
        for evidence in item["evidence"]:
            chunk_id = evidence["chunk_id"]
            if chunk_id not in relevant or not evidence["quote"] or evidence["quote"] not in chunks[chunk_id].text:
                raise ValueError(f"Invalid evidence quote or chunk: {query_id}")
        if not item["answerable"]:
            external = absence_by_id.get(query_id)
            if external is None:
                raise ValueError(f"Missing absence evidence: {query_id}")
            scope = read_scope(item["absence_evidence"])
            external_scope = read_scope(external)
            if scope != external_scope:
                raise ValueError(f"Inconsistent absence evidence: {query_id}")
            if item["absence_evidence"]["file"] != absence_path.name:
                raise ValueError(f"Absence evidence file mismatch: {query_id}")
            if any(chunk_id not in chunks for chunk_id in scope):
                raise ValueError(f"Unknown absence scope chunk ID: {query_id}")
            if binding is not None and external.get("annotation_status") != "reviewed":
                raise ValueError(f"Unreviewed absence evidence: {query_id}")
    positives = sum(item["answerable"] for item in queries)
    if (len(queries), positives, len(queries) - positives) != (
        manifest["question_count"], manifest["answerable_count"], manifest["unanswerable_count"],
    ):
        raise ValueError("Benchmark question counts do not match manifest")
    return {"queries": queries, "manifest": manifest, "queries_path": queries_path,
            "manifest_path": manifest_path, "absence_path": absence_path}
