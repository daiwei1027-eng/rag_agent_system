"""Assembly checks: reviewed groups, traceable source rows and store compatibility."""

import copy
import hashlib
import json
import re

import pytest

from rag_agent_system.ingestion.chunk_store import load_chunks
from rag_agent_system.ingestion.sec_chunk_build import assemble_sec_chunks, build_sec_chunks
from rag_agent_system.ingestion.sec_chunking import chunk_table_block, compact_table_rows


class Tokenizer:
    def __call__(self, text, **kwargs):
        words = list(re.finditer(r"\S+", text))
        return {"input_ids": list(range(len(words))),
                "offset_mapping": [(w.start(), w.end()) for w in words]}

    def encode(self, text, *, add_special_tokens, truncation):
        assert truncation is False
        return list(range(len(text.split()) + (2 if add_special_tokens else 0)))


def fixture():
    section = {
        "section_id": "sample:item_7", "document_id": "sample", "section": "item_7",
        "section_title": "MD&A", "metadata": {"company": "Example", "ticker": "EX",
        "fiscal_year": 2025, "form_type": "10-K", "source_file": "raw/example.html"},
        "blocks": [{"block_index": 0, "type": "text", "text": "a b c d e"},
                   {"block_index": 3, "type": "table",
                    "text": "Year |  | 2025\nCloud |  | \nRevenue |  | 10\nCost |  | 3\nProfit |  | 7"}],
    }
    plan = {"section_id": section["section_id"], "block_index": 3,
            "text_sha256": hashlib.sha256(section["blocks"][1]["text"].encode()).hexdigest(),
            "mode": "reviewed-row-groups", "header_rows": [0],
            "groups": [{"context_rows": [1], "data_rows": [2, 3, 4]}]}
    return section, {"tables": [plan]}


def test_split_table_repeats_headers_and_group_with_source_offsets():
    section, config = fixture()
    before = copy.deepcopy((section, config))
    block = section["blocks"][1]
    chunks = chunk_table_block(section, block, Tokenizer(), plan=config["tables"][0], max_tokens=8)
    assert [c["metadata"]["table_row_indices"] for c in chunks] == [[0, 1, 2], [0, 1, 3], [0, 1, 4]]
    assert (section, config) == before
    for chunk in chunks:
        meta = chunk["metadata"]
        assert meta["table_columns"] == [0, 2]
        rows = [block["text"][s["start_char"]:s["end_char"]] for s in meta["source_spans"]]
        assert "\n".join(" | ".join(row.split(" | ")[i] for i in meta["table_columns"]) for row in rows) == chunk["text"]
        assert meta["header_rows"] == [0] and meta["context_rows"] == [1]
    whole = chunk_table_block(section, block, Tokenizer(), plan=config["tables"][0], max_tokens=100)
    assert len(whole) == 1
    assert whole[0]["metadata"]["table_row_indices"] == [0, 1, 2, 3, 4]


@pytest.mark.parametrize("failure", ["hash", "missing-row", "duplicate-row", "unreviewed"])
def test_bad_or_stale_plans_fail(failure):
    section, config = fixture()
    plan = config["tables"][0]
    if failure == "hash":
        plan["text_sha256"] = "0" * 64
    elif failure == "missing-row":
        plan["groups"][0]["data_rows"].pop()
    elif failure == "duplicate-row":
        plan["groups"][0]["data_rows"].append(4)
    else:
        plan["mode"] = "whole-table-only"
    with pytest.raises(ValueError):
        chunk_table_block(section, section["blocks"][1], Tokenizer(), plan=plan, max_tokens=8)


def test_unified_store_prefix_budget_and_deterministic_order(tmp_path):
    section, config = fixture()
    chunks, summary = assemble_sec_chunks([section], config, Tokenizer(), max_tokens=8,
                                         overlap_tokens=2, embedding_max_tokens=50)
    assert chunks == assemble_sec_chunks([section], config, Tokenizer(), max_tokens=8,
                                         overlap_tokens=2, embedding_max_tokens=50)[0]
    assert [c["metadata"]["faiss_id"] for c in chunks] == list(range(4))
    assert summary["chunk_types"] == {"text": 1, "table": 3}
    assert chunks[0]["text"][chunks[0]["metadata"]["content_start_char"]:] == "a b c d e"
    assert all(c["text"].startswith("Example (EX) | FY2025 | 10-K | ITEM 7: MD&A\n\n") for c in chunks)
    path = tmp_path / "chunks.json"
    path.write_text(json.dumps(chunks), encoding="utf-8")
    loaded = load_chunks(path)
    assert list(loaded) == [c["chunk_id"] for c in chunks]
    assert all(set(c) == {"chunk_id", "text", "source", "metadata"} for c in chunks)
    with pytest.raises(ValueError, match="Token limit"):
        assemble_sec_chunks([section], config, Tokenizer(), max_tokens=8,
                            overlap_tokens=2, embedding_max_tokens=8)


@pytest.mark.parametrize("failure", ["missing", "duplicate", "unused"])
def test_table_plan_assignment_is_exact(failure):
    section, config = fixture()
    if failure == "missing":
        config["tables"] = []
    elif failure == "duplicate":
        config["tables"].append(copy.deepcopy(config["tables"][0]))
    else:
        extra = copy.deepcopy(config["tables"][0])
        extra["block_index"] = 99
        config["tables"].append(extra)
    with pytest.raises(ValueError):
        assemble_sec_chunks([section], config, Tokenizer())


def test_build_refuses_overwrite_and_stale_inputs_before_writing(tmp_path):
    with pytest.raises(FileExistsError):
        build_sec_chunks(tmp_path / "missing", tmp_path / "plans", tmp_path, tmp_path)
    source = tmp_path / "sections.jsonl"
    source.write_text("{}\n")
    config = tmp_path / "plans.json"
    config.write_text(json.dumps({"schema_version": 1, "sections_sha256": "0" * 64}))
    output = tmp_path / "new"
    with pytest.raises(ValueError, match="SHA256"):
        build_sec_chunks(source, config, tmp_path, output)
    assert not output.exists()


def test_compaction_preserves_populated_column_positions():
    assert compact_table_rows(" |  | Year\na |  | 2025") == ([" | Year", "a | 2025"], [0, 2])
    with pytest.raises(ValueError, match="column counts"):
        compact_table_rows("a | b\nc")
