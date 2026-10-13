"""Verify store compatibility and failure guards without downloading models."""

import json

import pytest

from rag_agent_system.ingestion import build_story_chunks, chunk_story, load_chunks
from rag_agent_system.retrieval import FaissRetriever


class CharacterTokenizer:
    """Small deterministic tokenizer for window/offset contract checks."""

    def __call__(self, text, **kwargs):
        return {
            "input_ids": self.encode(text, add_special_tokens=False),
            "offset_mapping": [(i, i + 1) for i in range(len(text))],
        }

    def encode(self, text, *, add_special_tokens, **kwargs):
        ids = [ord(char) for char in text]
        return [0, *ids, 0] if add_special_tokens else ids

    def decode(self, ids, **kwargs):
        return "".join(chr(token) for token in ids)


def test_short_long_store_schema_and_global_faiss_mapping(tmp_path):
    tokenizer = CharacterTokenizer()
    stories = ["Lily.", "abcdefghijklmnopq"]
    chunks = build_story_chunks(
        stories, tokenizer, embedding_tokenizer=tokenizer,
        max_tokens=8, overlap=2, source_start_index=12,
    )
    assert [c["text"] for c in chunks] == ["Lily.", "abcdefgh", "ghijklmn", "mnopq"]
    assert [c["chunk_id"] for c in chunks] == [
        "story_000012_chunk_000", "story_000013_chunk_000",
        "story_000013_chunk_001", "story_000013_chunk_002",
    ]
    assert len({c["chunk_id"] for c in chunks}) == len(chunks)
    metadata_keys = set(chunks[0]["metadata"])
    for i, chunk in enumerate(chunks):
        assert set(chunk) == {"chunk_id", "text", "source", "metadata"}
        assert set(chunk["metadata"]) == metadata_keys
        meta = chunk["metadata"]
        original = stories[meta["source_index"] - 12]
        assert chunk["text"] == original[meta["start_char"]:meta["end_char"]]
        assert meta["faiss_id"] == i
        assert meta["embedding_token_count"] <= 256
    path = tmp_path / "chunks.json"
    path.write_text(json.dumps(chunks), encoding="utf-8")
    store = load_chunks(path)
    mapping = FaissRetriever._build_id_mapping(store)
    assert mapping == {i: c["chunk_id"] for i, c in enumerate(chunks)}


def test_legacy_text_difference_requires_explicit_choice():
    class LowercaseDecoder(CharacterTokenizer):
        def decode(self, ids, **kwargs):
            return super().decode(ids).lower()

    tokenizer = LowercaseDecoder()
    with pytest.raises(ValueError, match="differs from legacy decode"):
        chunk_story("Lily.", "story", tokenizer, embedding_tokenizer=tokenizer)
    chunks = chunk_story(
        "Lily.", "story", tokenizer, embedding_tokenizer=tokenizer,
        require_legacy_text_match=False,
    )
    assert chunks[0]["text"] == "Lily."
    assert chunks[0]["metadata"]["legacy_decode_matches_original"] is False


def test_embedding_limit_includes_special_tokens():
    tokenizer = CharacterTokenizer()
    with pytest.raises(ValueError, match="embedding input has 10 tokens"):
        chunk_story(
            "abcdefgh", "story", tokenizer, embedding_tokenizer=tokenizer,
            max_tokens=8, overlap=2, embedding_max_tokens=8,
        )


@pytest.mark.parametrize("story, max_tokens, overlap", [
    (" ", 128, 32), ("story", True, 0), ("story", 8, 8),
])
def test_invalid_story_or_window_parameters(story, max_tokens, overlap):
    tokenizer = CharacterTokenizer()
    with pytest.raises(ValueError):
        chunk_story(
            story, "story", tokenizer, embedding_tokenizer=tokenizer,
            max_tokens=max_tokens, overlap=overlap,
        )
