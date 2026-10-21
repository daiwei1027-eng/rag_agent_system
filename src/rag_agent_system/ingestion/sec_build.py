"""Build a versioned section bundle from validated local SEC snapshots."""

import hashlib
import json
import logging
import platform
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup

from rag_agent_system.ingestion import sec_html, sec_manifest
from rag_agent_system.ingestion.sec_html import SECTION_SPECS, extract_section
from rag_agent_system.ingestion.sec_manifest import validate_local_manifest
from rag_agent_system.paths import project_root

logger = logging.getLogger(__name__)


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _path_label(path: Path) -> str:
    try:
        return path.relative_to(project_root()).as_posix()
    except ValueError:
        return path.as_posix()


def build_sec_sections(manifest_path: Path, output_dir: Path) -> dict[str, Any]:
    """Validate and parse all inputs before creating a fresh output directory.

    Original HTML stays under the input manifest's raw directory. The output
    contains a manifest snapshot and its original path base, not copied HTML.
    build_manifest.json is written last to mark a completed bundle.
    """
    manifest_path = manifest_path.resolve()
    output_dir = output_dir.resolve()
    if output_dir.exists():
        raise FileExistsError(f"Output directory already exists: {output_dir}")
    manifest_bytes = manifest_path.read_bytes()
    documents = validate_local_manifest(manifest_path)
    if manifest_path.read_bytes() != manifest_bytes:
        raise ValueError("Input manifest changed during validation")

    sections = []
    sources = []
    for document in documents:
        source_path = (manifest_path.parent / document["source_file"]).resolve()
        raw = source_path.read_bytes()
        if _digest(raw) != document["sha256"].lower():
            raise ValueError(f"Source changed during build: {document['document_id']}")
        soup = BeautifulSoup(raw, "html.parser")
        sources.append({
            "document_id": document["document_id"],
            "source_file": document["source_file"],
            "source_sha256": _digest(raw),
            "parser_detected_encoding": soup.original_encoding,
        })
        for section, start_title, end_title in SECTION_SPECS:
            record = extract_section(
                soup, document, section=section,
                start_title=start_title, end_title=end_title,
            )
            sections.append(record)
            logger.info(
                "%s: candidates=%d kept=%d tables=%d",
                record["section_id"], record["stats"]["candidate_blocks"],
                record["stats"]["kept_blocks"], record["stats"]["tables"],
            )
    if manifest_path.read_bytes() != manifest_bytes:
        raise ValueError("Input manifest changed during extraction")

    section_ids = [record["section_id"] for record in sections]
    if len(set(section_ids)) != len(section_ids):
        raise ValueError("Duplicate section IDs")
    jsonl = "".join(
        json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n"
        for record in sections
    ).encode("utf-8")
    summary = []
    for record in sections:
        text_blocks = [block for block in record["blocks"] if block["type"] == "text"]
        summary.append({
            "section_id": record["section_id"],
            **record["stats"],
            "first_text_preview": text_blocks[0]["text"][:240] if text_blocks else None,
            "last_text_preview": text_blocks[-1]["text"][:240] if text_blocks else None,
        })
    summary_bytes = (json.dumps(summary, ensure_ascii=False, indent=2) + "\n").encode("utf-8")

    code_paths = {
        "sec_html.py": Path(sec_html.__file__),
        "sec_manifest.py": Path(sec_manifest.__file__),
        "sec_build.py": Path(__file__),
    }
    build_manifest = {
        "schema_version": 1,
        "status": "complete",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "input_manifest": {
            "original_path": _path_label(manifest_path),
            "source_file_base": _path_label(manifest_path.parent),
            "snapshot": "input_manifest.json",
            "sha256": _digest(manifest_bytes),
        },
        "sources": sources,
        "config": {
            "html_parser": "html.parser",
            "section_specs": [list(spec) for spec in SECTION_SPECS],
            "cleaning_profile": "inspected-msft-nvda-goog-v1",
            "block_index": "candidate position before noise removal; gaps allowed",
            "table_renderer": "physical-grid-v1",
            "colspan": "text in first column, blank continuation columns",
            "rowspan": "repeat text and colspan placeholders in covered rows",
            "empty_table_rows": "omitted after span placement",
            "unsupported_tables": "nested tables, nonpositive or overlapping spans",
            "source_html": "BeautifulSoup serialization, not original byte offsets",
        },
        "environment": {"python": platform.python_version(), "beautifulsoup4": version("beautifulsoup4")},
        "code_sha256": {name: _digest(path.read_bytes()) for name, path in code_paths.items()},
        "counts": {
            "documents": len(documents),
            "sections": len(sections),
            "blocks": sum(len(record["blocks"]) for record in sections),
            "tables": sum(record["stats"]["tables"] for record in sections),
        },
        "files_sha256": {
            "sections.jsonl": _digest(jsonl),
            "summary.json": _digest(summary_bytes),
            "input_manifest.json": _digest(manifest_bytes),
        },
        "limitations": [
            "The input manifest is a provenance snapshot; resolve source_file from source_file_base.",
            "A completed build does not certify full content coverage or financial table semantics.",
            "Physical column positions are preserved; header roles, units and logical column groups are not inferred.",
            "No SEC chunks, retrieval index or benchmark is created by this command.",
        ],
    }
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(exist_ok=False)
    (output_dir / "sections.jsonl").write_bytes(jsonl)
    (output_dir / "summary.json").write_bytes(summary_bytes)
    (output_dir / "input_manifest.json").write_bytes(manifest_bytes)
    (output_dir / "build_manifest.json").write_text(
        json.dumps(build_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8",
    )
    return build_manifest
