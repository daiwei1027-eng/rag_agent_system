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
    benchmark_queries: Path | None = None
    benchmark_manifest: Path | None = None
    absence_evidence: Path | None = None


@dataclass(frozen=True, slots=True)
class RetrievalConfig:
    embedding_model: str
    normalize_embeddings: bool
    top_k: int = 20


@dataclass(frozen=True, slots=True)
class GenerationConfig:
    model_name: str
    max_new_tokens: int = 256
    temperature: float = 0.2
@dataclass(frozen=True, slots=True)
class RerankerConfig:
    enabled: bool
    model_name: str
    top_k: int = 5
    max_length: int = 512
    batch_size: int = 8


@dataclass(frozen=True, slots=True)
class ContextConfig:
    top_k: int = 5
@dataclass(frozen=True, slots=True)
class AgentConfig:
    model_name: str
    max_new_tokens: int
@dataclass(frozen=True, slots=True)
class AppConfig:
    name: str
    log_level: str
    paths: PathConfig
    retrieval: RetrievalConfig
    generation: GenerationConfig
    reranker: RerankerConfig
    context: ContextConfig
    agent: AgentConfig
def _section(raw: dict[str, Any], name: str) -> dict[str, Any]:
    value = raw.get(name)
    if not isinstance(value, dict):
        raise ValueError(f"Configuration section '{name}' must be a mapping.")
    return value
def _positive_int(
    section: dict[str, Any],
    key: str,
    default: int,
    section_name: str,
) -> int:
    value = section.get(key, default)

    if type(value) is not int or value <= 0:
        raise ValueError(
            f"{section_name}.{key} must be a positive integer."
        )

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
    reranker= _section(raw, "reranker")
    context = _section(raw, "context")
    # Older RAG configs have no agent section. Reuse their generation settings
    # until an explicit agent section is provided.
    agent = _section(raw, "agent") if "agent" in raw else generation

    top_k = _positive_int(retrieval, "top_k", 20, "retrieval")
    rerank_top_k = _positive_int(reranker, "top_k", 5, "reranker")
    max_length = _positive_int(reranker, "max_length", 512, "reranker")
    batch_size = _positive_int(reranker, "batch_size", 8, "reranker")
    context_top_k = _positive_int(context, "top_k", 5, "context")
    agent_max_new_tokens = _positive_int(agent, "max_new_tokens", 256, "agent")
    agent_model_name=agent.get("model_name")
    if not isinstance(agent_model_name, str):
        raise ValueError("agent.model_name must be a string.")
    if not agent_model_name.strip():
        raise ValueError("agent.model_name must be a non-empty string.")
    normalize_embeddings = retrieval.get("normalize_embeddings")
    if not isinstance(normalize_embeddings, bool):
        raise ValueError(
            "retrieval.normalize_embeddings must be true or false."
        )

    enabled = reranker.get("enabled")
    if not isinstance(enabled, bool):
        raise ValueError("reranker.enabled must be true or false.")

    model_name = reranker.get("model_name", "")
    if not isinstance(model_name, str):
        raise ValueError("reranker.model_name must be a string.")

    model_name = model_name.strip()
    if enabled and not model_name:
        raise ValueError(
            "reranker.model_name must be set when reranker is enabled."
        )

    if context_top_k > top_k:
        raise ValueError(
            "context.top_k must not exceed retrieval.top_k."
        )

    if enabled and not context_top_k <= rerank_top_k <= top_k:
        raise ValueError(
            "When reranker is enabled, require: "
            "context.top_k <= reranker.top_k <= retrieval.top_k."
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
            benchmark_queries=resolve_project_path(
                str(paths.get("benchmark_queries", "data/benchmark/tinystories_queries.jsonl")), root,
            ),
            benchmark_manifest=resolve_project_path(
                str(paths.get("benchmark_manifest", "data/benchmark/tinystories_benchmark_manifest.json")), root,
            ),
            absence_evidence=resolve_project_path(
                str(paths.get("absence_evidence", "data/benchmark/tinystories_absence_evidence.json")), root,
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
        reranker=RerankerConfig(
            enabled=enabled,
            model_name=model_name,
            top_k=rerank_top_k,
            max_length=max_length,
            batch_size=batch_size,
        ),
        context=ContextConfig(
            top_k=context_top_k,
        ),
        agent=AgentConfig(
            model_name=agent_model_name.strip(),
            max_new_tokens=agent_max_new_tokens,

        )
    )
