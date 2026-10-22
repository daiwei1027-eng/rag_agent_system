"""Encode frozen SEC chunks and save a verified, version-bound FAISS index."""

import argparse
import logging
from pathlib import Path

from rag_agent_system.ingestion.sec_index_build import build_sec_index
from rag_agent_system.paths import resolve_project_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chunks-dir", type=Path,
                        default=Path("data/sec/chunking_v1/20261021-minilm200-overlap32-v1"))
    parser.add_argument("--model-path", type=Path, required=True, help="Local MiniLM snapshot directory")
    parser.add_argument("--output-dir", type=Path, required=True, help="New directory, never overwritten")
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--device", default=None, help="Optional cpu/cuda; default is automatic selection")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    try:
        manifest = build_sec_index(resolve_project_path(args.chunks_dir), args.model_path,
                                  resolve_project_path(args.output_dir),
                                  batch_size=args.batch_size, device=args.device)
    except (ValueError, OSError, KeyError, AssertionError) as error:
        parser.exit(1, f"SEC index build failed: {error}\n")
    print(f"Complete: {manifest['vector_count']} vectors, {manifest['dimension']} dimensions; {args.output_dir}")


if __name__ == "__main__":
    main()
