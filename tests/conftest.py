"""Make src-layout imports available without requiring an editable install."""

import sys
from pathlib import Path

import pytest
import yaml

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


@pytest.fixture
def entrypoint_case(tmp_path):
    """Create isolated configs for CLI/factory wiring, without model assets."""
    from types import SimpleNamespace

    from rag_agent_system.config import load_config
    from rag_agent_system.models import DocumentChunk, RetrievedChunk

    def make(mode, rerank):
        raw = {
            "project": {"name": "entrypoint-test", "log_level": "INFO"},
            "paths": {"faiss_index": str(tmp_path / "unused.faiss"),
                      "chunks": str(tmp_path / "unused-chunks.json")},
            "retrieval": {"embedding_model": "fake-embedding", "mode": mode,
                          "normalize_embeddings": False, "top_k": 20},
            "reranker": {"enabled": rerank, "model_name": "fake-reranker",
                         "max_length": 128, "batch_size": 2, "top_k": 3},
            "context": {"top_k": 2},
            "generation": {"model_name": "fake-generator", "max_new_tokens": 13,
                           "temperature": 0.0},
            "agent": {"model_name": "fake-agent", "max_new_tokens": 17},
        }
        path = tmp_path / "settings.yaml"
        path.write_text(yaml.safe_dump(raw), encoding="utf-8")
        candidates = [RetrievedChunk(DocumentChunk(cid, f"Evidence {cid}", source="sec"),
                                     score=1 / rank, rank=rank)
                      for rank, cid in enumerate(("a", "b", "c"), start=1)]
        return SimpleNamespace(path=path, config=load_config(path), candidates=candidates)

    return make

