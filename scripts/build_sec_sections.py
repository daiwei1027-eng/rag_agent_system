"""Extract SEC sections without loading models or building a retrieval index."""

import argparse
import logging
from pathlib import Path

from rag_agent_system.ingestion.sec_build import build_sec_sections
from rag_agent_system.paths import resolve_project_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=Path("data/sec/manifest.draft.json"))
    parser.add_argument("--output-dir", type=Path, required=True, help="A new directory; existing outputs are never overwritten")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    try:
        manifest = build_sec_sections(
            resolve_project_path(args.manifest), resolve_project_path(args.output_dir),
        )
    except (ValueError, OSError) as error:
        parser.exit(1, f"SEC section build failed: {error}\n")
    print(f"Complete: {manifest['counts']}; output={args.output_dir}")


if __name__ == "__main__":
    main()
