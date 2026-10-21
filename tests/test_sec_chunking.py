"""The independent-text-block chunking contract, without model downloads."""

import copy
import json
import re

import pytest

from rag_agent_system.ingestion.sec_chunking import chunk_text_run, pack_table_rows


def word_tokenizer(text, **kwargs):
    """One token per word gives explicit, readable boundary expectations."""
    words = list(re.finditer(r"\S+", text))
    return {
        "input_ids": list(range(len(words))),
        "offset_mapping": [(word.start(), word.end()) for word in words],
    }


def section_for(text):
    return {
        "document_id": "sample-2025-10k", "section": "item_1a",
        "section_title": "Risk Factors",
        "metadata": {"company": "Example", "ticker": "MSFT", "fiscal_year": 2025},
        "blocks": [{"block_index": 7, "type": "text", "text": text}],
    }


@pytest.mark.parametrize("text,overlap,expected", [
    ("one", 1, ["one"]),
    ("one two three", 1, ["one two three"]),
    ("one two three four", 1, ["one two three", "three four"]),
    ("one two three four five", 1, ["one two three", "three four five"]),
    ("one two three four", 0, ["one two three", "four"]),
    ("one two three four", 2, ["one two three", "two three four"]),
    ("  α β γ δ  ", 1, ["  α β γ", "γ δ  "]),
])
def test_windows_and_original_character_ranges(text, overlap, expected):
    section = section_for(text)
    chunks = chunk_text_run(section, word_tokenizer, max_tokens=3, overlap_tokens=overlap)
    assert [chunk["text"] for chunk in chunks] == expected
    assert len({chunk["chunk_id"] for chunk in chunks}) == len(expected)
    for index, chunk in enumerate(chunks):
        assert set(chunk) == {"chunk_id", "text", "source", "metadata"}
        assert chunk["source"] == "sec"
        assert chunk["metadata"]["chunk_index"] == index
        span, = chunk["metadata"]["source_spans"]
        assert span["block_index"] == 7
        assert text[span["start_char"]:span["end_char"]] == chunk["text"]
    assert json.loads(json.dumps(chunks)) == chunks


@pytest.mark.parametrize("max_tokens,overlap", [
    (0, 0), (-1, 0), (True, 0), (1.5, 0), (3, -1), (3, 3), (3, True),
])
def test_invalid_window_parameters(max_tokens, overlap):
    with pytest.raises(ValueError):
        chunk_text_run(section_for("one"), word_tokenizer, max_tokens=max_tokens, overlap_tokens=overlap)


def test_independent_blocks_tables_and_metadata_isolation():
    section = section_for("one two")
    section["blocks"].extend([
        {"block_index": 8, "type": "table", "text": "year | value"},
        {"block_index": 9, "type": "text", "text": "three four"},
    ])
    before = copy.deepcopy(section)
    chunks = chunk_text_run(section, word_tokenizer, max_tokens=3, overlap_tokens=1)
    assert [chunk["text"] for chunk in chunks] == ["one two", "three four"]
    assert [chunk["metadata"]["source_spans"][0]["block_index"] for chunk in chunks] == [7, 9]
    assert len({chunk["chunk_id"] for chunk in chunks}) == 2
    assert all(chunk["metadata"]["document_id"] == section["document_id"] for chunk in chunks)
    assert all(chunk["metadata"]["ticker"] == "MSFT" for chunk in chunks)
    chunks[0]["metadata"]["ticker"] = "changed"
    chunks[0]["metadata"]["source_spans"][0]["start_char"] = 99
    assert chunks[1]["metadata"]["ticker"] == "MSFT"
    assert chunks[1]["metadata"]["source_spans"][0]["start_char"] == 0
    assert section == before


def test_empty_text_and_invalid_tokenizer_offsets_fail():
    with pytest.raises(ValueError, match="token IDs"):
        chunk_text_run(section_for(""), word_tokenizer)

    def invalid_offsets(text, **kwargs):
        return {"input_ids": [1], "offset_mapping": []}

    with pytest.raises(ValueError, match="offset mapping"):
        chunk_text_run(section_for("one"), invalid_offsets)


def test_text_function_allows_no_text_blocks():
    section = section_for("one")
    section["blocks"] = [{"block_index": 8, "type": "table", "text": "year | value"}]
    assert chunk_text_run(section, word_tokenizer) == []


class RowTokenizer:
    def encode(self, text, *, add_special_tokens, truncation):
        assert add_special_tokens is False
        assert truncation is False
        return re.findall(r"\S+", text)


@pytest.mark.parametrize("rows,headers,budget,expected", [
    (["Year", "2024", "2025"], [0], 4, [[0, 1, 2]]),
    (["Year", "2024", "2025"], [0], 3, [[0, 1, 2]]),
    (["a b", "c d", "e"], [], 3, [[0], [1, 2]]),
    (["H1", "H2", "a", "b", "c"], [0, 1], 4, [[0, 1, 2, 3], [0, 1, 4]]),
    (["H", "a b", "c d"], [0], 3, [[0, 1], [0, 2]]),
    ([], [], 3, []),
    (["", "  "], [], 3, []),
])
def test_table_row_groups(rows, headers, budget, expected):
    before = (rows.copy(), headers.copy())
    groups = pack_table_rows(rows, RowTokenizer(), header_rows=headers, max_tokens=budget)
    assert groups == expected
    assert (rows, headers) == before
    if not groups:
        return
    data = [index for group in groups for index in group if index not in headers]
    assert data == [index for index in range(len(rows)) if index not in headers]
    for group in groups:
        assert len(RowTokenizer().encode(
            "\n".join(rows[index] for index in group),
            add_special_tokens=False, truncation=False,
        )) <= budget
    if len(groups) > 1:
        assert all(group[:len(headers)] == headers for group in groups)
        assert all(any(index not in headers for index in group) for group in groups)


@pytest.mark.parametrize("rows,headers,budget,message", [
    (["too many header words", "a"], [0], 3, "headers exceed"),
    (["header words", "data words"], [0], 3, "row 1"),
    (["one two three"], [], 2, "row 0"),
])
def test_table_unfittable_headers_or_rows_fail(rows, headers, budget, message):
    with pytest.raises(ValueError, match=message):
        pack_table_rows(rows, RowTokenizer(), header_rows=headers, max_tokens=budget)


@pytest.mark.parametrize("rows,headers,budget,message", [
    (["a"], [], True, "positive integer"),
    (["a"], [], 0, "positive integer"),
    (["a"], [], 1.5, "positive integer"),
    (["a"], [True], 3, "integer row indices"),
    (["a"], [1], 3, "out-of-range"),
    (["a"], [0, 0], 3, "unique"),
    (["a", "b"], [1, 0], 3, "source order"),
    ([None], [], 3, "list of strings"),
])
def test_table_invalid_configuration(rows, headers, budget, message):
    with pytest.raises(ValueError, match=message):
        pack_table_rows(rows, RowTokenizer(), header_rows=headers, max_tokens=budget)
