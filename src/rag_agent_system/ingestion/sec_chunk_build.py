"""Assemble source-traceable SEC text/table chunks for the existing JSON store."""

import hashlib
import json
import logging
import platform
from collections import Counter
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path

from rag_agent_system.ingestion import sec_chunking
from rag_agent_system.ingestion.sec_chunking import chunk_text_run, chunk_table_block

logger = logging.getLogger(__name__)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def assemble_sec_chunks(sections: list[dict], table_config: dict, tokenizer, *,
                        max_tokens: int = 200, overlap_tokens: int = 32,
                        embedding_max_tokens: int = 256) -> tuple[list[dict], dict]:
    """Body limits exclude the derived prefix; full model inputs include it."""
    if type(embedding_max_tokens) is not int or embedding_max_tokens <= 0:
        raise ValueError("embedding_max_tokens must be a positive integer")
    plans = {}
    for plan in table_config["tables"]:
        key = (plan["section_id"], plan["block_index"])
        if key in plans:
            raise ValueError(f"Duplicate table plan: {key}")
        plans[key] = plan
    used = set()
    chunks = []
    sources = {}
    block_count = Counter()
    for section in sections:
        sid = section["section_id"]
        if sid in sources:
            raise ValueError(f"Duplicate section ID: {sid}")
        sources[sid] = {}
        for block in section["blocks"]:
            bi = block["block_index"]
            if bi in sources[sid] or block["type"] not in {"text", "table"}:
                raise ValueError(f"Invalid or duplicate block: {sid}/{bi}")
            sources[sid][bi] = block
            block_count[block["type"]] += 1
        section_chunks = chunk_text_run(section, tokenizer, max_tokens=max_tokens,
                                        overlap_tokens=overlap_tokens)
        for block in section["blocks"]:
            if block["type"] != "table":
                continue
            key = (sid, block["block_index"])
            if key not in plans:
                raise ValueError(f"Missing table plan: {key}")
            used.add(key)
            section_chunks.extend(chunk_table_block(section, block, tokenizer,
                                  plan=plans[key], max_tokens=max_tokens))
        section_chunks.sort(key=lambda c: (c["metadata"]["source_spans"][0]["block_index"],
                                           c["metadata"]["chunk_index"]))
        chunks.extend(section_chunks)
        logger.info("%s: %d chunks", sid, len(section_chunks))
    if used != set(plans):
        raise ValueError("Table configuration contains unused plans")
    if not chunks or len({c["chunk_id"] for c in chunks}) != len(chunks):
        raise ValueError("Empty corpus or duplicate chunk IDs")

    coverage = {}
    for faiss_id, chunk in enumerate(chunks):
        meta = chunk["metadata"]
        sid = f"{meta['document_id']}:{meta['section']}"
        spans = meta["source_spans"]
        block = sources[sid][spans[0]["block_index"]]
        slices = []
        for span in spans:
            if (span["block_index"] != block["block_index"] or
                    not 0 <= span["start_char"] < span["end_char"] <= len(block["text"])):
                raise ValueError("Invalid source span")
            value = block["text"][span["start_char"]:span["end_char"]]
            if meta["block_type"] == "table":
                cells = value.split(" | ")
                value = " | ".join(cells[i] for i in meta["table_columns"])
            slices.append(value)
        reconstructed = "\n".join(slices)
        if reconstructed != chunk["text"]:
            raise ValueError("Chunk body does not match its source spans")
        key = (sid, block["block_index"])
        coverage.setdefault(key, []).append(meta)
        body_tokens = len(tokenizer.encode(chunk["text"], add_special_tokens=False, truncation=False))
        prefix = (f"{meta['company']} ({meta['ticker']}) | FY{meta['fiscal_year']} | "
                  f"{meta['form_type']} | {meta['section'].replace('_', ' ').upper()}: "
                  f"{meta['section_title']}\n\n")
        chunk["text"] = prefix + chunk["text"]
        full_tokens = len(tokenizer.encode(chunk["text"], add_special_tokens=True, truncation=False))
        if body_tokens > max_tokens or full_tokens > embedding_max_tokens:
            raise ValueError(f"Token limit exceeded: {chunk['chunk_id']} ({body_tokens}/{full_tokens})")
        meta.update(faiss_id=faiss_id, token_count=body_tokens,
                    embedding_token_count=full_tokens, content_start_char=len(prefix))

    # Check every source block, text coverage and table data-row multiplicity.
    for sid, blocks in sources.items():
        for bi, block in blocks.items():
            metas = coverage.get((sid, bi), [])
            if not metas:
                raise ValueError(f"Uncovered source block: {sid}/{bi}")
            if block["type"] == "text":
                ranges = [m["source_spans"][0] for m in metas]
                end = 0
                for span in ranges:
                    if span["start_char"] > end and block["text"][end:span["start_char"]].strip():
                        raise ValueError("Text coverage gap")
                    end = max(end, span["end_char"])
                if end != len(block["text"]) or ranges[0]["start_char"] != 0:
                    raise ValueError("Incomplete text coverage")
            else:
                plan = plans[(sid, bi)]
                repeated = set(plan["header_rows"])
                for group in plan["groups"]:
                    repeated.update(group["context_rows"])
                counts = Counter(i for m in metas for i in m["table_row_indices"])
                if set(counts) != set(range(len(block["text"].split("\n")))):
                    raise ValueError("Incomplete table row coverage")
                if any(n != 1 for i, n in counts.items() if i not in repeated):
                    raise ValueError("Duplicate table data row")
    summary = {
        "documents": len({s["document_id"] for s in sections}), "sections": len(sections),
        "source_blocks": dict(block_count), "chunks": len(chunks),
        "chunk_types": dict(Counter(c["metadata"]["block_type"] for c in chunks)),
        "max_body_tokens": max(c["metadata"]["token_count"] for c in chunks),
        "max_embedding_tokens": max(c["metadata"]["embedding_token_count"] for c in chunks),
        "checks": {"unique_ids": True, "source_reconstruction": True,
                   "block_and_row_coverage": True, "token_limits": True,
                   "contiguous_faiss_ids": True},
    }
    return chunks, summary


def build_sec_chunks(sections_path: Path, table_plans_path: Path, tokenizer_path: Path,
                     output_dir: Path, *, max_tokens: int = 200,
                     overlap_tokens: int = 32) -> dict:
    """Validate in memory, then write a fresh bundle; completion marker is last."""
    from transformers import AutoTokenizer

    if output_dir.exists():
        raise FileExistsError(f"Output directory already exists: {output_dir}")
    raw = sections_path.read_bytes()
    plans_raw = table_plans_path.read_bytes()
    config = json.loads(plans_raw)
    if type(config["schema_version"]) is not int or config["schema_version"] != 1:
        raise ValueError("Unsupported table plan schema")
    if digest(raw) != config["sections_sha256"]:
        raise ValueError("Table plans do not match sections SHA256")
    parent_raw = (sections_path.parent / "build_manifest.json").read_bytes()
    parent = json.loads(parent_raw)
    if (parent["status"] != "complete" or
            parent["files_sha256"][sections_path.name] != digest(raw)):
        raise ValueError("Sections bundle is incomplete or changed")
    model_config = json.loads((tokenizer_path / "sentence_bert_config.json").read_bytes())
    limit = model_config["max_seq_length"]
    tokenizer = AutoTokenizer.from_pretrained(str(tokenizer_path), local_files_only=True)
    sections = [json.loads(line) for line in raw.decode("utf-8").splitlines() if line.strip()]
    chunks, summary = assemble_sec_chunks(sections, config, tokenizer, max_tokens=max_tokens,
                           overlap_tokens=overlap_tokens, embedding_max_tokens=limit)
    files = {
        "chunks.json": (json.dumps(chunks, ensure_ascii=False, indent=2) + "\n").encode("utf-8"),
        "summary.json": (json.dumps(summary, ensure_ascii=False, indent=2) + "\n").encode("utf-8"),
        "table_plans.json": plans_raw, "sections_build_manifest.json": parent_raw,
    }
    fingerprints = {p.name: digest(p.read_bytes()) for p in tokenizer_path.iterdir()
                    if p.is_file() and (p.suffix == ".json" or p.name == "vocab.txt")}
    manifest = {
        "schema_version": 1, "status": "complete",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "input": {"sections_sha256": digest(raw), "table_plans_sha256": digest(plans_raw),
                  "sections_build_manifest_sha256": digest(parent_raw)},
        "config": {"max_body_tokens": max_tokens, "text_overlap_tokens": overlap_tokens,
                   "embedding_max_tokens": limit, "text_strategy": "independent-block-windows",
                   "table_strategy": "reviewed-headers-and-groups-whole-rows",
                   "prefix": "company (ticker) | FYyear | form | ITEM label: title + two newlines",
                   "source_spans": "block.text half-open offsets; table rows projected by table_columns",
                   "content_start_char": "prefix length in final chunk.text",
                   "faiss_id": "global zero-based output order; no index built"},
        "tokenizer": {"model": "sentence-transformers/all-MiniLM-L6-v2",
                      "snapshot": tokenizer_path.name, "files_sha256": fingerprints},
        "environment": {"python": platform.python_version(), "transformers": version("transformers"),
                        "tokenizers": version("tokenizers")},
        "code_sha256": {"sec_chunking.py": digest(Path(sec_chunking.__file__).read_bytes()),
                        "sec_chunk_build.py": digest(Path(__file__).read_bytes())},
        "counts": summary, "files_sha256": {name: digest(value) for name, value in files.items()},
        "limitations": ["Row roles apply only to the hash-bound reviewed corpus.",
                        "Physical table rendering does not infer financial relationships or external footnotes.",
                        "Independent blocks can lose cross-paragraph context; retrieval quality is unmeasured.",
                        "No embeddings, retrieval index or benchmark evaluation was run."],
    }
    if sections_path.read_bytes() != raw or table_plans_path.read_bytes() != plans_raw:
        raise ValueError("Inputs changed during chunk build")
    output_dir.mkdir(parents=True, exist_ok=False)
    for name, value in files.items():
        (output_dir / name).write_bytes(value)
    (output_dir / "build_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest
