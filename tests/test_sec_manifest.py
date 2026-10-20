"""Local SEC input validation, without models or network access."""

import copy
import hashlib
import json
from pathlib import Path

import pytest

from rag_agent_system.ingestion.sec_manifest import validate_local_manifest


@pytest.fixture
def local_manifest(tmp_path):
    raw = tmp_path / "raw"
    raw.mkdir()
    content = b"<html>SEC example</html>"
    (raw / "sample.html").write_bytes(content)
    (raw / "sample.txt").write_bytes(content)
    (tmp_path / "outside.html").write_bytes(content)
    payload = {
        "schema_version": 1,
        "documents": [{
            "document_id": "sample-2025-10k",
            "source_file": "raw/sample.html",
            "size_bytes": len(content),
            "sha256": hashlib.sha256(content).hexdigest(),
        }],
    }
    path = tmp_path / "manifest.json"

    def save(value):
        path.write_text(json.dumps(value), encoding="utf-8")
        return path

    return payload, save


def test_valid_local_manifest_accepts_uppercase_digest(local_manifest):
    payload, save = local_manifest
    payload["documents"][0]["sha256"] = payload["documents"][0]["sha256"].upper()
    assert validate_local_manifest(save(payload)) == payload["documents"]


@pytest.mark.parametrize("case", [
    "root_type", "version_bool", "version_float", "wrong_version",
    "documents_type", "empty_documents", "record_type", "blank_id",
    "blank_path", "size_bool", "size_mismatch", "hash_type", "hash_format",
    "hash_mismatch", "missing_file", "wrong_extension", "outside_raw",
    "duplicate_id", "duplicate_resolved_path",
])
def test_invalid_local_manifest(local_manifest, case):
    payload, save = local_manifest
    document = payload["documents"][0]
    if case == "root_type":
        payload = []
    elif case in ("version_bool", "version_float", "wrong_version"):
        payload["schema_version"] = {
            "version_bool": True, "version_float": 1.0, "wrong_version": 2,
        }[case]
    elif case == "documents_type":
        payload["documents"] = {}
    elif case == "empty_documents":
        payload["documents"] = []
    elif case == "record_type":
        payload["documents"] = [None]
    elif case in ("duplicate_id", "duplicate_resolved_path"):
        duplicate = copy.deepcopy(document)
        if case == "duplicate_resolved_path":
            duplicate.update(document_id="another-id", source_file="raw/./sample.html")
        payload["documents"].append(duplicate)
    else:
        field, value = {
            "blank_id": ("document_id", " "),
            "blank_path": ("source_file", " "),
            "size_bool": ("size_bytes", True),
            "size_mismatch": ("size_bytes", document["size_bytes"] + 1),
            "hash_type": ("sha256", None),
            "hash_format": ("sha256", "z" * 64),
            "hash_mismatch": ("sha256", "0" * 64),
            "missing_file": ("source_file", "raw/missing.html"),
            "wrong_extension": ("source_file", "raw/sample.txt"),
            "outside_raw": ("source_file", "raw/../outside.html"),
        }[case]
        document[field] = value
    with pytest.raises((ValueError, TypeError)):
        validate_local_manifest(save(payload))


@pytest.mark.parametrize("location,field", [
    ("root", "schema_version"), ("document", "size_bytes"),
])
def test_missing_field_has_validation_error(local_manifest, location, field):
    payload, save = local_manifest
    target = payload if location == "root" else payload["documents"][0]
    del target[field]
    with pytest.raises((ValueError, TypeError), match=field):
        validate_local_manifest(save(payload))
