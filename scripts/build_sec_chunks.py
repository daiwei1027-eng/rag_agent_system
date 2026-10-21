"""Build versioned SEC chunks with a local MiniLM tokenizer, without an index."""

import argparse
import logging
from pathlib import Path

from rag_agent_system.ingestion.sec_chunk_build import build_sec_chunks
from rag_agent_system.paths import resolve_project_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sections", type=Path, default=Path("data/sec/processed/20261021-sections-v1/sections.jsonl"))
    parser.add_argument("--table-plans", type=Path, default=Path("data/sec/table_plans.v1.json"))
    parser.add_argument("--tokenizer-path", type=Path, required=True, help="Local MiniLM snapshot directory")
    parser.add_argument("--output-dir", type=Path, required=True, help="New directory; never overwritten")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    try:
        manifest = build_sec_chunks(resolve_project_path(args.sections),
                    resolve_project_path(args.table_plans), args.tokenizer_path.resolve(),
                    resolve_project_path(args.output_dir))
    except (ValueError, OSError, KeyError) as error:
        parser.exit(1, f"SEC chunk build failed: {error}\n")
    print(f"Complete: {manifest['counts']}; output={args.output_dir}")


if __name__ == "__main__":
    main()
