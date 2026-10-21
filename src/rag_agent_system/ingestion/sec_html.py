"""Section extraction for the six inspected SEC HTML snapshots."""

from typing import Any
from urllib.parse import urlsplit

from bs4 import BeautifulSoup, Comment, NavigableString, Tag

# find_section_anchor
# collect_section_elements
# select_content_blocks
# is_noise_block
def find_section_anchor(
    soup: BeautifulSoup,
    title: str,
) -> str:
    links = soup.find_all("a",href=True)
    expected_title = " ".join(title.split())
    anchors: set[str] = set()
    for link in links:
        text = " ".join(link.get_text().split())
        if text != expected_title:
            continue
        else:
            anchor=urlsplit(link.get("href")).fragment
            if not anchor:
                raise ValueError(f"Missing URL fragment for title: {title}")
            if soup.find(id=anchor) is None:
                raise ValueError(f"Missing anchor for {link}")
            anchors.add(anchor)
    if len(anchors) != 1:
        raise ValueError(f"Found {len(anchors)} anchors for {title}")
    return anchors.pop()
def collect_section_elements(
    soup: BeautifulSoup,
    start_id: str,
    end_id: str,
) -> list[Tag]:
    result = []
    found_end = False
    start_heading = soup.find(id=start_id)
    end_heading = soup.find(id=end_id)
    if start_heading is None or end_heading is None:
        raise ValueError(f"Missing section boundary: {start_id} or {end_id}")
    for paragraph in start_heading.find_all_next():
        if paragraph is end_heading:
            found_end=True
            break
        result.append(paragraph)
    if not found_end:
        raise ValueError(f"End section {end_id} was not reached after {start_id}")
    return result
def select_content_blocks(elements: list[Tag]) -> list[Tag]:
    result = []
    for element in elements:
        if element.find_parent("table") is not None:
            continue
        if element.name == "table":
            result.append(element)
            continue
        if (
            element.name in {"p", "div", "li"}
            and element.find(["p", "div", "table", "ul", "ol", "li"]) is None
        ):
            result.append(element)
    return result
def is_noise_block(block: Tag, ticker: str) -> bool:
    text = " ".join(block.get_text(" ", strip=True).split())
    has_toc_link = any(
    " ".join(link.get_text().split()) == "Table of Contents"
    for link in block.find_all("a", href=True)
)
    if not text:
        return True
    if ticker == "MSFT":
        if block.find_parent("div", class_="main-content-container") is None:
            return True
    else:
        for ancestor in block.parents:
            style = ancestor.get("style", "")
            declarations = style.lower().replace(" ", "").split(";")
            if "position:absolute" in declarations and "bottom:0" in declarations:
                return True
    if ticker == "NVDA":
        if text == "Table of Contents" and has_toc_link:
            return True
    if ticker == "GOOG":
        if text == "Table of Contents Alphabet Inc." and has_toc_link:
            return True
    return False
def _plain_text(element: Tag) -> str:
    """Join inline fragments without splitting words; preserve br boundaries."""
    parts = []
    for descendant in element.descendants:
        if isinstance(descendant, Comment):
            continue
        if isinstance(descendant, NavigableString):
            if descendant.parent.name not in {"script", "style"}:
                parts.append(str(descendant))
        elif descendant.name == "br":
            parts.append(" ")
    return " ".join("".join(parts).split())


def _positive_span(cell: Tag, attribute: str, row_index: int) -> int:
    try:
        value = int(cell.get(attribute, "1"))
    except (TypeError, ValueError) as error:
        raise ValueError(f"Table row {row_index}: invalid {attribute}") from error
    if value <= 0:
        raise ValueError(f"Table row {row_index}: {attribute} must be positive")
    return value


def table_to_text(table: Tag) -> str:
    """Render a physical grid, preserving blank columns and merged cells.

    A colspan writes text in its first column and blank continuation columns.
    A rowspan repeats those values in each covered row. Empty layout rows are
    omitted after span placement. All emitted rows have the same column count.
    Nested tables and nonpositive spans are explicitly unsupported in v1.
    """
    if table.name != "table":
        raise ValueError("table_to_text requires a table element")
    if table.find("table") is not None:
        raise ValueError("Nested tables are not supported by SEC table renderer v1")

    # column -> (text, number of remaining rows covered by an earlier cell)
    pending: dict[int, tuple[str, int]] = {}
    grid: list[dict[int, str]] = []
    width = 0
    for row_index, row in enumerate(table.find_all("tr")):
        values = {column: text for column, (text, _) in pending.items()}
        following = {
            column: (text, remaining - 1)
            for column, (text, remaining) in pending.items()
            if remaining > 1
        }
        column = 0
        for cell in row.find_all(["td", "th"], recursive=False):
            while column in values:
                column += 1
            colspan = _positive_span(cell, "colspan", row_index)
            rowspan = _positive_span(cell, "rowspan", row_index)
            if any(column + offset in values for offset in range(colspan)):
                raise ValueError(f"Table row {row_index}: overlapping merged cells")
            text = _plain_text(cell)
            for offset in range(colspan):
                position = column + offset
                value = text if offset == 0 else ""
                values[position] = value
                if rowspan > 1:
                    following[position] = (value, rowspan - 1)
            column += colspan
        width = max(width, max(values, default=-1) + 1)
        grid.append(values)
        pending = following
    if pending:
        raise ValueError("Merged cells extend beyond the final table row")

    return "\n".join(
        " | ".join(values.get(column, "") for column in range(width))
        for values in grid
        if any(values.values())
    )


def serialize_block(block: Tag, block_index: int) -> dict[str, Any]:
    """Use the same four fields for text and table blocks."""
    if type(block_index) is not int or block_index < 0:
        raise ValueError("block_index must be a non-negative integer")
    if block.name not in {"p", "div", "li", "table"}:
        raise ValueError(f"Unsupported content block: {block.name}")
    block_type = "table" if block.name == "table" else "text"
    text = table_to_text(block) if block_type == "table" else _plain_text(block)
    if not text:
        raise ValueError(f"Block {block_index} has no rendered text")
    return {
        "block_index": block_index,
        "type": block_type,
        "text": text,
        # Parser serialization, not an exact byte slice of the original file.
        "source_html": str(block),
    }


SECTION_SPECS = (
    ("item_1", "Business", "Risk Factors"),
    ("item_1a", "Risk Factors", "Unresolved Staff Comments"),
    (
        "item_7",
        "Management’s Discussion and Analysis of Financial Condition and Results of Operations",
        "Quantitative and Qualitative Disclosures About Market Risk",
    ),
)


def extract_section(
    soup: BeautifulSoup,
    document: dict[str, Any],
    *,
    section: str,
    start_title: str,
    end_title: str,
) -> dict[str, Any]:
    """Extract a JSON-compatible section with source metadata and ordered blocks."""
    metadata_fields = (
        "company", "ticker", "fiscal_year", "period_end", "form_type",
        "accession_number", "source_file", "source_url",
    )
    required = {*metadata_fields, "document_id", "sha256"}
    missing = required - document.keys()
    if missing:
        raise ValueError(f"Section source missing fields: {sorted(missing)}")
    if document["ticker"] not in {"MSFT", "NVDA", "GOOG"}:
        raise ValueError(f"No inspected cleaning profile for {document['ticker']}")

    try:
        start_anchor = find_section_anchor(soup, start_title)
        end_anchor = find_section_anchor(soup, end_title)
        elements = collect_section_elements(soup, start_anchor, end_anchor)
        candidates = select_content_blocks(elements)
        blocks = [
            serialize_block(block, index)
            for index, block in enumerate(candidates)
            if not is_noise_block(block, document["ticker"])
        ]
    except ValueError as error:
        raise ValueError(f"{document['document_id']}/{section}: {error}") from error
    if not blocks:
        raise ValueError(f"{document['document_id']}/{section}: no content blocks")

    return {
        "section_id": f"{document['document_id']}:{section}",
        "document_id": document["document_id"],
        "section": section,
        "section_title": start_title,
        "start_anchor": start_anchor,
        "end_anchor": end_anchor,
        "metadata": {
            **{name: document[name] for name in metadata_fields},
            "source_sha256": document["sha256"],
        },
        # Indices refer to candidates before noise removal, so gaps are expected.
        "blocks": blocks,
        "stats": {
            "candidate_blocks": len(candidates),
            "removed_blocks": len(candidates) - len(blocks),
            "kept_blocks": len(blocks),
            "text_blocks": sum(block["type"] == "text" for block in blocks),
            "tables": sum(block["type"] == "table" for block in blocks),
        },
    }
