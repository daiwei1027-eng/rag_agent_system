"""Bundle guards reject invalid runs before model construction or output writes."""

import json

import pytest

from rag_agent_system.ingestion.sec_index_build import build_sec_index


@pytest.mark.parametrize("case,error", [
    ("existing-output", FileExistsError),
    ("bad-batch", ValueError),
    ("stale-chunks", ValueError),
])
def test_invalid_build_does_not_write_outputs(tmp_path, case, error):
    output = tmp_path / "output"
    source = tmp_path / "chunks"
    source.mkdir()
    (source / "chunks.json").write_text("[]", encoding="utf-8")
    (source / "build_manifest.json").write_text(json.dumps({
        "status": "complete", "files_sha256": {"chunks.json": "0" * 64},
    }), encoding="utf-8")
    if case == "existing-output":
        output.mkdir()
        (output / "keep.txt").write_text("original", encoding="utf-8")
    with pytest.raises(error):
        build_sec_index(source, tmp_path / "no-model", output,
                        batch_size=0 if case == "bad-batch" else 64)
    if case == "existing-output":
        assert (output / "keep.txt").read_text(encoding="utf-8") == "original"
        assert len(list(output.iterdir())) == 1
    else:
        assert not output.exists()
