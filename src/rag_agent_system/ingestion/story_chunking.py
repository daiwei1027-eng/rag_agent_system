"""Story-local token windows compatible with the existing chunk-store schema."""

from collections.abc import Iterable
from typing import Any


def chunk_story(
    story: str,
    story_id: str,
    tokenizer,
    max_tokens: int = 128,
    overlap: int = 32,
    *,
    embedding_tokenizer,
    embedding_max_tokens: int = 256,
    source_index: int = 0,
    faiss_start: int = 0,
    require_legacy_text_match: bool = True,
) -> list[dict[str, Any]]:
    """Cut one story, preserving original text and checking its embedding length.

    max_tokens/overlap count BODY tokens with the supplied chunk tokenizer.
    embedding_max_tokens includes the embedding tokenizer's special tokens.
    faiss_start is the first vector position for this story in the final list.
    Strict legacy matching exposes text changes beyond story-local windowing.
    """
    if not isinstance(story, str) or not story.strip():
        raise ValueError("story must be a non-empty string")
    if not isinstance(story_id, str) or not story_id.strip():
        raise ValueError("story_id must be a non-empty string")
    for name, value in (
        ("max_tokens", max_tokens),
        ("embedding_max_tokens", embedding_max_tokens),
    ):
        if type(value) is not int or value <= 0:
            raise ValueError(f"{name} must be a positive integer")
    if type(overlap) is not int or not 0 <= overlap < max_tokens:
        raise ValueError("overlap must be an integer in [0, max_tokens)")
    for name, value in (("source_index", source_index), ("faiss_start", faiss_start)):
        if type(value) is not int or value < 0:
            raise ValueError(f"{name} must be a non-negative integer")
    if type(require_legacy_text_match) is not bool:
        raise ValueError("require_legacy_text_match must be a boolean")

    encoded = tokenizer(
        story,
        add_special_tokens=False,
        truncation=False,
        return_offsets_mapping=True,
    )
    token_ids = encoded["input_ids"]
    offsets = encoded["offset_mapping"]
    if not token_ids or len(offsets) != len(token_ids):
        raise ValueError(f"Invalid token IDs or offset mapping for {story_id}")

    chunks = []
    step = max_tokens - overlap
    # Short and long stories use the same construction path and dictionary schema.
    for chunk_index, start in enumerate(range(0, len(token_ids), step)):
        end = min(start + max_tokens, len(token_ids))
        start_char = 0 if start == 0 else offsets[start][0]
        end_char = len(story) if end == len(token_ids) else offsets[end - 1][1]
        if not 0 <= start_char < end_char <= len(story):
            raise ValueError(f"Invalid character range for {story_id}, chunk {chunk_index}")
        text = story[start_char:end_char]
        legacy_text = tokenizer.decode(token_ids[start:end], skip_special_tokens=True)
        legacy_matches = text == legacy_text
        if require_legacy_text_match and not legacy_matches:
            raise ValueError(
                f"{story_id}, chunk {chunk_index}: original slice differs from legacy decode; "
                "inspect the boundary before treating this as a story-boundary-only experiment"
            )
        if not text.strip():
            raise ValueError(f"Empty chunk for {story_id}, chunk {chunk_index}")

        body_count = len(tokenizer.encode(text, add_special_tokens=False, truncation=False))
        embedding_count = len(
            embedding_tokenizer.encode(text, add_special_tokens=True, truncation=False)
        )
        if embedding_count > embedding_max_tokens:
            raise ValueError(
                f"{story_id}, chunk {chunk_index}: embedding input has {embedding_count} "
                f"tokens, exceeding {embedding_max_tokens}; text was not truncated"
            )
        chunks.append({
            "chunk_id": f"{story_id}_chunk_{chunk_index:03d}",
            "text": text,
            "source": "tinystories",
            "metadata": {
                "faiss_id": faiss_start + chunk_index,
                "story_id": story_id,
                "source_index": source_index,
                "chunk_index": chunk_index,
                "start_char": start_char,
                "end_char": end_char,
                "window_token_count": end - start,
                "token_count": body_count,
                "embedding_token_count": embedding_count,
                "legacy_decode_matches_original": legacy_matches,
            },
        })
        if end == len(token_ids):
            break
    return chunks


def build_story_chunks(
    stories: Iterable[str],
    tokenizer,
    *,
    embedding_tokenizer,
    max_tokens: int = 128,
    overlap: int = 32,
    embedding_max_tokens: int = 256,
    source_start_index: int = 0,
    require_legacy_text_match: bool = True,
) -> list[dict[str, Any]]:
    """Build a flat store with globally unique IDs and consecutive FAISS labels.

    Pass a preselected, contiguous source range in its original order. This
    function does not select a corpus budget or silently skip malformed stories.
    Embed and save this exact returned list order when constructing the index.
    """
    if isinstance(stories, str):
        raise ValueError("stories must contain story strings, not be one string")
    if type(source_start_index) is not int or source_start_index < 0:
        raise ValueError("source_start_index must be a non-negative integer")
    chunks = []
    for source_index, story in enumerate(stories, start=source_start_index):
        chunks.extend(chunk_story(
            story,
            f"story_{source_index:06d}",
            tokenizer,
            max_tokens=max_tokens,
            overlap=overlap,
            embedding_tokenizer=embedding_tokenizer,
            embedding_max_tokens=embedding_max_tokens,
            source_index=source_index,
            faiss_start=len(chunks),
            require_legacy_text_match=require_legacy_text_match,
        ))
    if not chunks:
        raise ValueError("No stories supplied")
    return chunks
