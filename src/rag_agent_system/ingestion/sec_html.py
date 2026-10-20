from urllib.parse import urlsplit

from bs4 import BeautifulSoup, Tag

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