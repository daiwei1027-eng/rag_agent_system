"""Load the Day 17 JSON document store into typed chunks."""

import json
from pathlib import Path
from typing import Any

from rag_agent_system.models import DocumentChunk
from rag_agent_system.paths import require_file


def load_chunks(path: Path) -> dict[str, DocumentChunk]:
    """Load a list of chunk objects and index them by stable string ID."""

    require_file(path, label="chunk store")
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    if not isinstance(payload, list):
        raise ValueError("chunks.json must contain a JSON list.")

    chunks: dict[str, DocumentChunk] = {}
    for position, item in enumerate(payload):
        if not isinstance(item, dict):
            raise ValueError(f"Chunk at position {position} must be an object.")
        chunk = _parse_chunk(item, position)
        if chunk.chunk_id in chunks:
            raise ValueError(f"Duplicate chunk_id: {chunk.chunk_id}")
        chunks[chunk.chunk_id] = chunk
    return chunks


def _parse_chunk(item: dict[str, Any], position: int) -> DocumentChunk:
    chunk_id = item.get("chunk_id", item.get("id"))
    text = item.get("text")
    if chunk_id is None or not isinstance(text, str) or not text.strip():
        raise ValueError(f"Chunk at position {position} requires an ID and non-empty text.")
    metadata = item.get("metadata", {})
    if not isinstance(metadata, dict):
        raise ValueError(f"Chunk metadata at position {position} must be an object.")
    return DocumentChunk(
        chunk_id=str(chunk_id),
        text=text,
        source=str(item["source"]) if item.get("source") is not None else None,
        metadata=metadata,
    )

