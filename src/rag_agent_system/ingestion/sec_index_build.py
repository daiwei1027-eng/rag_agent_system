"""Persist and verify a SEC index bound to frozen chunks and a local model."""

import hashlib
import json
import logging
import platform
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path
from time import perf_counter

import faiss
import numpy as np

from rag_agent_system.ingestion import faiss_build
from rag_agent_system.ingestion.chunk_store import load_chunks
from rag_agent_system.ingestion.faiss_build import build_flat_ip_index
from rag_agent_system.paths import project_root
from rag_agent_system.retrieval import faiss_retriever
from rag_agent_system.retrieval.faiss_retriever import FaissRetriever

logger = logging.getLogger(__name__)
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
SMOKE_QUERY = "What risks does NVIDIA discuss concerning export controls?"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while data := handle.read(1024 * 1024):
            digest.update(data)
    return digest.hexdigest()


def path_label(path: Path) -> str:
    try:
        return path.resolve().relative_to(project_root()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def build_sec_index(chunks_dir: Path, model_path: Path, output_dir: Path, *,
                    batch_size: int = 64, device: str | None = None) -> dict:
    """Build a fresh index bundle, leaving the completed chunk bundle untouched.

    A fresh existing retriever loads the saved index, chunks and local encoder.
    The small smoke query checks compatibility, not retrieval quality.
    """
    from sentence_transformers import SentenceTransformer

    chunks_dir, model_path, output_dir = (
        path.resolve() for path in (chunks_dir, model_path, output_dir)
    )
    if output_dir.exists():
        raise FileExistsError(f"Output directory already exists: {output_dir}")
    if type(batch_size) is not int or batch_size <= 0:
        raise ValueError("batch_size must be a positive integer")
    chunks_path = chunks_dir / "chunks.json"
    source_path = chunks_dir / "build_manifest.json"
    source_raw = source_path.read_bytes()
    source_manifest = json.loads(source_raw)
    chunks_hash = sha256_file(chunks_path)
    if (source_manifest["status"] != "complete" or
            source_manifest["files_sha256"]["chunks.json"] != chunks_hash):
        raise ValueError("Chunk bundle is incomplete or its chunks hash changed")
    expected_tokenizer = source_manifest["tokenizer"]
    if expected_tokenizer["model"] != MODEL_NAME:
        raise ValueError("Unsupported SEC embedding model")
    if model_path.name != expected_tokenizer["snapshot"]:
        raise ValueError("Local model snapshot does not match chunk build")
    for name, expected_hash in expected_tokenizer["files_sha256"].items():
        if sha256_file(model_path / name) != expected_hash:
            raise ValueError(f"Model/tokenizer file changed: {name}")
    # Bind the actual local weights and pooling configuration as well as tokenizer files.
    model_files = [p for p in model_path.rglob("*") if p.is_file() and (
        p.suffix in {".json", ".safetensors"} or p.name in {"vocab.txt", "pytorch_model.bin"}
    )]
    model_hashes = {p.relative_to(model_path).as_posix(): sha256_file(p) for p in model_files}
    if not any(name.endswith((".safetensors", "pytorch_model.bin")) for name in model_hashes):
        raise ValueError("Local snapshot has no model weights")
    chunks = list(load_chunks(chunks_path).values())
    start = perf_counter()
    encoder = SentenceTransformer(str(model_path), device=device, local_files_only=True)
    loaded_at = perf_counter()
    if encoder.max_seq_length != source_manifest["config"]["embedding_max_tokens"]:
        raise ValueError("Encoder input limit differs from chunk build")
    logger.info("Encoding %d SEC chunks on %s", len(chunks), encoder.device)
    index = build_flat_ip_index(chunks, encoder, batch_size=batch_size)
    encoded_at = perf_counter()
    vectors = index.reconstruct_n(0, index.ntotal)
    if index.ntotal != len(chunks) or index.d != encoder.get_embedding_dimension():
        raise ValueError("Unexpected index count or dimension")
    if not np.isfinite(vectors).all() or not np.allclose(
        np.linalg.norm(vectors, axis=1), 1.0, atol=1e-5
    ):
        raise ValueError("Invalid stored index vectors")
    # Independent small encoding catches a row-order mismatch without repeating the full build.
    sample_positions = sorted({0, len(chunks) // 2, len(chunks) - 1})
    sample_vectors = encoder.encode([chunks[i].text for i in sample_positions],
                    batch_size=batch_size, normalize_embeddings=True, convert_to_numpy=True)
    sample_vectors = np.ascontiguousarray(sample_vectors, dtype=np.float32)
    np.testing.assert_allclose(vectors[sample_positions], sample_vectors, atol=1e-5, rtol=1e-5)
    query_vector = encoder.encode([SMOKE_QUERY], normalize_embeddings=True, convert_to_numpy=True)
    query_vector = np.ascontiguousarray(query_vector, dtype=np.float32)
    k = min(5, index.ntotal)
    memory_scores, memory_ids = index.search(query_vector, k)

    if sha256_file(chunks_path) != chunks_hash or source_path.read_bytes() != source_raw:
        raise ValueError("Chunk inputs changed during index construction")
    for name, expected_hash in model_hashes.items():
        if sha256_file(model_path / name) != expected_hash:
            raise ValueError(f"Model file changed during encoding: {name}")
    output_dir.mkdir(parents=True, exist_ok=False)
    index_path = output_dir / "sec.faiss"
    faiss.write_index(index, str(index_path))
    restored = faiss.read_index(str(index_path))
    np.testing.assert_array_equal(restored.reconstruct_n(0, restored.ntotal), vectors)
    disk_scores, disk_ids = restored.search(query_vector, k)
    np.testing.assert_array_equal(disk_ids, memory_ids)
    np.testing.assert_array_equal(disk_scores, memory_scores)

    retriever = FaissRetriever(index_path=index_path, chunks_path=chunks_path,
                              embedding_model=str(model_path), normalize_embeddings=True)
    results = retriever.retrieve(SMOKE_QUERY, top_k=k)
    expected_ids = [chunks[int(i)].chunk_id for i in memory_ids[0]]
    if [r.chunk.chunk_id for r in results] != expected_ids:
        raise ValueError("Existing retriever returns different chunk IDs")
    np.testing.assert_allclose([r.score for r in results], memory_scores[0], atol=1e-6)
    norms = np.linalg.norm(vectors, axis=1)
    validation = {
        "checks": {"finite_unit_vectors": True, "input_order_sample_reencoded": True,
                   "all_saved_vectors_equal": True, "reload_search_equal": True,
                   "existing_retriever_disk_load_and_search": True},
        "count": index.ntotal, "dimension": index.d, "dtype": str(vectors.dtype),
        "max_norm_error": float(np.max(np.abs(norms - 1.0))),
        "sample_positions": sample_positions, "smoke_query": SMOKE_QUERY,
        "smoke_results": [{"chunk_id": r.chunk.chunk_id, "score": r.score, "rank": r.rank,
                           "ticker": r.chunk.metadata["ticker"],
                           "fiscal_year": r.chunk.metadata["fiscal_year"],
                           "section": r.chunk.metadata["section"]} for r in results],
        "scope": "Engineering smoke check with fresh local retriever/model load; not relevance judgments or benchmark results.",
    }
    validation_raw = (json.dumps(validation, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    (output_dir / "validation.json").write_bytes(validation_raw)
    (output_dir / "chunks_build_manifest.json").write_bytes(source_raw)
    manifest = {
        "schema_version": 1, "status": "complete",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "chunks": {"path": path_label(chunks_path), "sha256": chunks_hash,
                   "build_manifest_sha256": hashlib.sha256(source_raw).hexdigest()},
        "embedding_model": MODEL_NAME, "embedding_model_snapshot": model_path.name,
        "model_files_sha256": model_hashes, "normalize_embeddings": True,
        "embedding_max_tokens": encoder.max_seq_length, "batch_size": batch_size,
        "index_type": "IndexFlatIP", "dimension": index.d, "vector_count": index.ntotal,
        "faiss_id": "zero-based chunks list position, validated before encoding",
        "timing_seconds": {"model_load": loaded_at - start, "index_build": encoded_at - loaded_at,
                           "total_with_validation": perf_counter() - start},
        "environment": {"python": platform.python_version(), "device": str(encoder.device),
                        **{name: version(name) for name in ["torch", "sentence-transformers", "transformers", "numpy", "faiss-cpu"]}},
        "code_sha256": {"faiss_build.py": sha256_file(Path(faiss_build.__file__)),
                        "sec_index_build.py": sha256_file(Path(__file__)),
                        "faiss_retriever.py": sha256_file(Path(faiss_retriever.__file__))},
        "files_sha256": {"sec.faiss": sha256_file(index_path),
                         "validation.json": hashlib.sha256(validation_raw).hexdigest(),
                         "chunks_build_manifest.json": hashlib.sha256(source_raw).hexdigest()},
        "limitations": ["Chunks remain in the path recorded above; index and chunks must stay hash-bound.",
                        "Only three document vectors are independently reencoded; the smoke query uses a freshly loaded local retriever/model.",
                        "No metadata filtering, reranking or formal SEC benchmark was evaluated.",
                        "No cross-device bitwise reproduction claim is made."],
    }
    (output_dir / "index_build.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest
