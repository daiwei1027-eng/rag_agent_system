"""Typed YAML configuration loading."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from rag_agent_system.paths import project_root, resolve_project_path


@dataclass(frozen=True, slots=True)
class PathConfig:
    faiss_index: Path
    chunks: Path


@dataclass(frozen=True, slots=True)
class RetrievalConfig:
    embedding_model: str
    normalize_embeddings: bool
    top_k: int = 3


@dataclass(frozen=True, slots=True)
class GenerationConfig:
    model_name: str
    max_new_tokens: int = 256
    temperature: float = 0.2


@dataclass(frozen=True, slots=True)
class AppConfig:
    name: str
    log_level: str
    paths: PathConfig
    retrieval: RetrievalConfig
    generation: GenerationConfig


def _section(raw: dict[str, Any], name: str) -> dict[str, Any]:
    value = raw.get(name)
    if not isinstance(value, dict):
        raise ValueError(f"Configuration section '{name}' must be a mapping.")
    return value


def load_config(path: str | Path | None = None) -> AppConfig:
    """Load and minimally validate project configuration from YAML."""

    root = project_root()
    config_path = resolve_project_path(path or "configs/default.yaml", root)
    if not config_path.is_file():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with config_path.open("r", encoding="utf-8") as handle:
        raw = yaml.safe_load(handle) or {}
    if not isinstance(raw, dict):
        raise ValueError("Configuration root must be a mapping.")

    project = _section(raw, "project")
    paths = _section(raw, "paths")
    retrieval = _section(raw, "retrieval")
    generation = _section(raw, "generation")

    top_k = int(retrieval.get("top_k", 3))

    if top_k < 1:
        raise ValueError(
            "retrieval.top_k must be at least 1."
        )

    normalize_embeddings = retrieval.get(
        "normalize_embeddings"
    )

    if not isinstance(normalize_embeddings, bool):
        raise ValueError(
            "retrieval.normalize_embeddings "
            "must be true or false."
        )

    return AppConfig(
        name=str(
            project.get("name", "rag-agent-system")
        ),
        log_level=str(
            project.get("log_level", "INFO")
        ).upper(),
        paths=PathConfig(
            faiss_index=resolve_project_path(
                str(paths["faiss_index"]),
                root,
            ),
            chunks=resolve_project_path(
                str(paths["chunks"]),
                root,
            ),
        ),
        retrieval=RetrievalConfig(
            embedding_model=str(
                retrieval["embedding_model"]
            ),
            normalize_embeddings=normalize_embeddings,
            top_k=top_k,
        ),
        generation=GenerationConfig(
            model_name=str(
                generation["model_name"]
            ),
            max_new_tokens=int(
                generation.get("max_new_tokens", 256)
            ),
            temperature=float(
                generation.get("temperature", 0.2)
            ),
        ),
    )
