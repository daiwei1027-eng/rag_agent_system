from typing import  Any
from pathlib import Path
import json
import hashlib

def validate_local_manifest(
    manifest_path: Path,
) -> list[dict[str, Any]]:
    with manifest_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise TypeError("manifest must be a dict")
    missing = {"schema_version", "documents"} - payload.keys()
    if missing:
        raise ValueError(f"manifest missing fields: {sorted(missing)}")
    if type(payload["schema_version"]) is not int :
        raise TypeError("schema_version must be a int")
    if payload["schema_version"] != 1:
        raise ValueError("Schema version wrong.")
    if not isinstance(payload["documents"], list):
        raise ValueError("Document list wrong.")
    if not payload["documents"]:
        raise ValueError("Document list empty.")
    documents=payload["documents"]
    document_ids=[]
    document_source_files=[]
    manifest_resolve_path=manifest_path.resolve().parent
    raw_dir = (manifest_resolve_path / "raw").resolve()
    for position, document in enumerate(documents):

        if not isinstance(document, dict):
            raise ValueError("Document must be a dictionary.")
        missing = {
            "document_id", "source_file", "size_bytes", "sha256"
        } - document.keys()
        if missing:
            raise ValueError(
                f"Document at position {position} missing fields: {sorted(missing)}"
            )
        if not isinstance(document["document_id"], str):
            raise ValueError("Document id must be a string.")
        if not document["document_id"].strip():
            raise ValueError("Document id is empty.")
        if document["document_id"] in document_ids:
            raise ValueError("Document ID already exists")
        if not isinstance(document["source_file"], str):
            raise ValueError("Source file must be a string.")
        if not document["source_file"].strip():
            raise ValueError("Document source file is empty.")
        if type(document["size_bytes"]) is not int:
            raise ValueError("Size bytes must be an integer.")
        if document["size_bytes"] <= 0:
            raise ValueError("Size bytes must be positive.")
        expected_sha256 = document["sha256"]

        if (
                not isinstance(expected_sha256, str)
                or len(expected_sha256) != 64
                or any(c not in "0123456789abcdefABCDEF" for c in expected_sha256)
        ):
            raise ValueError(
                f"{document['document_id']}: SHA256 must contain 64 hexadecimal characters"
            )
        resolve_document_path = (manifest_resolve_path / document["source_file"]).resolve()
        if resolve_document_path in document_source_files:
            raise ValueError("Document source file already exists")
        if not resolve_document_path.is_file():
            raise ValueError("Source file does not exist.")
        if resolve_document_path.suffix.lower() != ".html":
            raise ValueError("Source file does not end with .html.")
        if not resolve_document_path.is_relative_to(raw_dir):
            raise ValueError("source_file must be inside raw/")
        real_size_bytes=resolve_document_path.stat().st_size
        if real_size_bytes != document["size_bytes"]:
            raise ValueError("Size bytes does not match.")
        with resolve_document_path.open("rb") as handle:
            actual_sha256 = hashlib.sha256(handle.read()).hexdigest()
        if actual_sha256 != document["sha256"].lower():
            raise ValueError(
                f"{document['document_id']}: SHA256 does not match"
            )
        document_source_files.append(resolve_document_path)
        document_ids.append(document["document_id"])
    return documents
