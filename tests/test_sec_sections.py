"""Merged table rendering and the persisted SEC section contract."""

import hashlib
import json

import pytest
from bs4 import BeautifulSoup

from rag_agent_system.ingestion.sec_build import build_sec_sections
from rag_agent_system.ingestion.sec_html import SECTION_SPECS, serialize_block, table_to_text


def table(html):
    return BeautifulSoup(html, "html.parser").find("table")


@pytest.mark.parametrize("html,expected", [
    (
        "<table><tr><th>Year</th><th>Revenue</th></tr><tr><td>2025</td><td>100</td></tr></table>",
        "Year | Revenue\n2025 | 100",
    ),
    ("<table><tr><td>A</td><td></td><td>B</td></tr></table>", "A |  | B"),
    (
        '<table><tr><th colspan="2">Year</th><th>Total</th></tr><tr><td>A</td><td>B</td><td>C</td></tr></table>',
        "Year |  | Total\nA | B | C",
    ),
    (
        '<table><tr><td>2024</td><td rowspan="2">Cloud</td><td>100</td></tr><tr><td>2025</td><td>120</td></tr></table>',
        "2024 | Cloud | 100\n2025 | Cloud | 120",
    ),
    (
        '<table><tr><td colspan="2" rowspan="3">A</td><td>B</td></tr><tr><td>C</td></tr><tr><td>D</td></tr></table>',
        "A |  | B\nA |  | C\nA |  | D",
    ),
    (
        '<table><tr><td colspan="2"></td></tr><tr><td><span>20</span><span>25</span><br>year</td><td>100</td></tr></table>',
        "2025 year | 100",
    ),
])
def test_table_grid_rendering(html, expected):
    assert table_to_text(table(html)) == expected


@pytest.mark.parametrize("attribute,value", [
    ("colspan", "0"), ("rowspan", "0"), ("colspan", "bad"), ("rowspan", "-1"),
])
def test_invalid_span_is_explicit(attribute, value):
    with pytest.raises(ValueError, match=attribute):
        table_to_text(table(f'<table><tr><td {attribute}="{value}">A</td></tr></table>'))


@pytest.mark.parametrize("html,message", [
    ('<table><tr><td rowspan="2">A</td></tr></table>', "beyond"),
    ('<table><tr><td><table><tr><td>A</td></tr></table></td></tr></table>', "Nested"),
    (
        '<table><tr><td>A</td><td rowspan="2">B</td></tr><tr><td colspan="2">C</td></tr></table>',
        "overlapping",
    ),
])
def test_unsupported_table_does_not_silently_flatten(html, message):
    with pytest.raises(ValueError, match=message):
        table_to_text(table(html))


@pytest.mark.parametrize("html,kind,expected", [
    ("<p>B<span>USINESS</span><br>next</p>", "text", "BUSINESS next"),
    ("<table><tr><td>2025</td><td>100</td></tr></table>", "table", "2025 | 100"),
])
def test_block_schema_and_source_html(html, kind, expected):
    block = BeautifulSoup(html, "html.parser").find()
    record = serialize_block(block, 4)
    assert record == {
        "block_index": 4, "type": kind, "text": expected, "source_html": str(block),
    }
    assert json.loads(json.dumps(record)) == record


@pytest.fixture
def source_manifest(tmp_path):
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    titles = list(dict.fromkeys(title for _, start, end in SECTION_SPECS for title in (start, end)))
    anchors = {title: f"anchor-{index}" for index, title in enumerate(titles)}
    links = "".join(f'<a href="#{anchors[title]}">{title}</a>' for title in titles)
    body = []
    for title in titles:
        body.append(f'<p id="{anchors[title]}">{title}</p>')
        body.append(f"<p>{title} example.</p>")
        if title == "Business":
            body.append('<p></p><table><tr><th colspan="2">Year</th></tr><tr><td>2025</td><td>100</td></tr></table>')
    html = f'<html><body>{links}<div class="main-content-container">{"".join(body)}</div></body></html>'
    source = raw_dir / "sample.html"
    source.write_bytes(html.encode("utf-8"))
    document = {
        "document_id": "sample-2025-10k", "company": "Example", "ticker": "MSFT",
        "fiscal_year": 2025, "period_end": "2025-06-30", "form_type": "10-K",
        "accession_number": "0000000000-25-000001", "source_file": "raw/sample.html",
        "source_url": "https://example.test/sample.html",
        "size_bytes": source.stat().st_size,
        "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
    }
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({"schema_version": 1, "documents": [document]}), encoding="utf-8")
    return manifest, source


def test_build_roundtrip_reproducibility_and_no_overwrite(source_manifest, tmp_path):
    manifest, _ = source_manifest
    first_dir, second_dir = tmp_path / "first", tmp_path / "second"
    build = build_sec_sections(manifest, first_dir)
    build_sec_sections(manifest, second_dir)
    sections = [json.loads(line) for line in (first_dir / "sections.jsonl").read_text(encoding="utf-8").splitlines()]
    assert len(sections) == 3
    assert [block["block_index"] for block in sections[0]["blocks"]] == [0, 2]
    assert sections[0]["blocks"][1]["type"] == "table"
    assert all(record["metadata"]["source_sha256"] for record in sections)
    assert all(record["start_anchor"] != record["end_anchor"] for record in sections)
    assert (first_dir / "input_manifest.json").read_bytes() == manifest.read_bytes()
    assert (first_dir / "sections.jsonl").read_bytes() == (second_dir / "sections.jsonl").read_bytes()
    for name, expected in build["files_sha256"].items():
        assert hashlib.sha256((first_dir / name).read_bytes()).hexdigest() == expected
    before = (first_dir / "sections.jsonl").read_bytes()
    with pytest.raises(FileExistsError):
        build_sec_sections(manifest, first_dir)
    assert (first_dir / "sections.jsonl").read_bytes() == before


def test_invalid_source_creates_no_output(source_manifest, tmp_path):
    manifest, source = source_manifest
    source.write_bytes(source.read_bytes() + b"changed")
    output = tmp_path / "failed-build"
    with pytest.raises(ValueError):
        build_sec_sections(manifest, output)
    assert not output.exists()
