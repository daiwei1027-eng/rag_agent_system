def chunk_text_run(
    section_record: dict,
    tokenizer,
    *,
    max_tokens: int = 200,
    overlap_tokens: int = 32,
) -> list[dict]:
    blocks = section_record["blocks"]

    base_metadata = {
        **section_record["metadata"],
        "document_id": section_record["document_id"],
        "section": section_record["section"],
        "section_title": section_record["section_title"],
    }

    chunks = []
    if type(max_tokens) is not int or not max_tokens > 0:
        raise ValueError("Max tokens must be a positive integer")
    if type(overlap_tokens) is not int or not 0 <= overlap_tokens < max_tokens:
        raise ValueError("overlap must be an integer in [0, max_tokens)")
    for block in blocks:
        if block["type"]!="text":
            continue
        text = block["text"]
        encoded=tokenizer(text,
        add_special_tokens=False,
        truncation=False,
        return_offsets_mapping=True,)
        token_ids = encoded["input_ids"]
        offsets = encoded["offset_mapping"]
        if not token_ids or len(offsets) != len(token_ids):
            raise ValueError(f"Invalid token IDs or offset mapping")
        step=max_tokens-overlap_tokens
        for chunk_index, start in enumerate(range(0, len(token_ids), step)):
            end = min(start + max_tokens, len(token_ids))
            start_char = 0 if start == 0 else offsets[start][0]
            end_char = len(text) if end == len(token_ids) else offsets[end - 1][1]
            if not 0 <= start_char < end_char <= len(text):
                raise ValueError(f"Invalid character range")
            processed_text = text[start_char:end_char]
            chunks.append({
                "chunk_id": (
                    f"{base_metadata['document_id']}_"
                    f"{base_metadata['section']}_"
                    f"b{block['block_index']:04d}_c{chunk_index:03d}"
                ),
                "text": processed_text,
                "source": "sec",
                "metadata": {
                    **base_metadata,
                    "block_type": "text",
                    "chunk_index": chunk_index,
                    "source_spans": [{
                        "block_index": block["block_index"],
                        "start_char": start_char,
                        "end_char": end_char,
                    }],
                },
            })

            if end == len(token_ids):
                break

    return chunks


def compact_table_rows(text: str) -> tuple[list[str], list[int]]:
    """Remove only columns empty in every row; retain all populated columns."""
    grid = [row.split(" | ") for row in text.split("\n")]
    if len({len(row) for row in grid}) != 1:
        raise ValueError("Table grid has inconsistent column counts")
    columns = [i for i in range(len(grid[0])) if any(row[i].strip() for row in grid)]
    if not columns:
        raise ValueError("Table has no populated columns")
    return [" | ".join(row[i] for i in columns) for row in grid], columns


def chunk_table_block(section_record: dict, block: dict, tokenizer, *, plan: dict,
                      max_tokens: int = 200) -> list[dict]:
    """Apply a reviewed, hash-bound row plan and retain original row offsets."""
    import hashlib
    from collections import Counter

    if type(max_tokens) is not int or max_tokens <= 0:
        raise ValueError("Max tokens must be a positive integer")
    if plan.get("mode") not in {"whole-table-only", "reviewed-row-groups"}:
        raise ValueError("Unknown table plan mode")
    if hashlib.sha256(block["text"].encode("utf-8")).hexdigest() != plan["text_sha256"]:
        raise ValueError("Table plan hash does not match source text")
    rows, columns = compact_table_rows(block["text"])
    headers = plan["header_rows"]
    groups = plan["groups"]
    if not isinstance(headers, list) or not isinstance(groups, list) or not groups:
        raise ValueError("Table plan requires header and nonempty group lists")
    # Validate even plans for tables that currently fit in one chunk.
    all_roles = headers.copy()
    for group in groups:
        all_roles.extend(group["context_rows"] + group["data_rows"])
        if not group["data_rows"]:
            raise ValueError("Table group must include data rows")
    if (any(type(i) is not int for i in all_roles)
            or Counter(all_roles) != Counter(range(len(rows)))):
        raise ValueError("Table plan must assign every source row exactly once")
    if headers != list(range(len(headers))):
        raise ValueError("Table headers must be leading rows in source order")
    if all_roles != list(range(len(rows))):
        raise ValueError("Table groups must follow source order")

    count = lambda value: len(tokenizer.encode(value, add_special_tokens=False, truncation=False))
    if count("\n".join(rows)) <= max_tokens:
        selections = [(list(range(len(rows))), headers, [])]
    else:
        if plan.get("mode") == "whole-table-only":
            raise ValueError("Unreviewed table splitting requires an explicit row plan")
        selections = []
        for group in groups:
            context = group["context_rows"]
            original_indices = headers + context + group["data_rows"]
            local_rows = [rows[i] for i in original_indices]
            local_headers = list(range(len(headers) + len(context)))
            packed = pack_table_rows(local_rows, tokenizer, header_rows=local_headers,
                                     max_tokens=max_tokens)
            selections.extend(([original_indices[i] for i in selection], headers, context)
                              for selection in packed)

    original_rows = block["text"].split("\n")
    offsets = []
    position = 0
    for row in original_rows:
        offsets.append((position, position + len(row)))
        position += len(row) + 1
    metadata = {**section_record["metadata"],
                "document_id": section_record["document_id"],
                "section": section_record["section"],
                "section_title": section_record["section_title"]}
    result = []
    for index, (indices, header_indices, context_indices) in enumerate(selections):
        result.append({
            "chunk_id": (f"{section_record['document_id']}_{section_record['section']}_"
                         f"b{block['block_index']:04d}_c{index:03d}"),
            "text": "\n".join(rows[i] for i in indices), "source": "sec",
            "metadata": {**metadata, "block_type": "table", "chunk_index": index,
                         "table_row_indices": indices, "header_rows": header_indices,
                         "context_rows": context_indices, "table_columns": columns,
                         "table_rendering": "drop-globally-empty-columns-v1",
                         "source_spans": [
                             {"block_index": block["block_index"], "start_char": offsets[i][0],
                              "end_char": offsets[i][1]} for i in indices]},
        })
    return result
def pack_table_rows(
    rows: list[str],
    tokenizer,
    *,
    header_rows: list[int],
    max_tokens: int = 200,
) -> list[list[int]]:
    """Pack complete rows, repeating explicitly supplied headers when split.

    The returned indices reference the original ``rows``. Data rows stay in
    source order and occur exactly once; each split group starts with the same
    headers. This function does not infer header roles or construct chunk JSON.
    The budget excludes any document prefix and tokenizer special tokens.
    """
    if type(max_tokens) is not int or not max_tokens > 0:
        raise ValueError("Max tokens must be a positive integer")
    if not isinstance(rows, list) or any(not isinstance(row, str) for row in rows):
        raise ValueError("rows must be a list of strings")
    if not isinstance(header_rows, list) or any(type(index) is not int for index in header_rows):
        raise ValueError("header_rows must be a list of integer row indices")
    if any(not 0 <= index < len(rows) for index in header_rows):
        raise ValueError("header_rows contains an out-of-range row index")
    if header_rows != sorted(set(header_rows)):
        raise ValueError("header_rows must be unique and in source order")
    if not rows or not any(row.strip() for row in rows):
        return []

    def token_count(indices: list[int]) -> int:
        text = "\n".join(rows[index] for index in indices)
        return len(tokenizer.encode(
            text, add_special_tokens=False, truncation=False,
        ))

    all_indices = list(range(len(rows)))
    if token_count(all_indices) <= max_tokens:
        return [all_indices]
    if token_count(header_rows) > max_tokens:
        raise ValueError(f"Table headers exceed max_tokens={max_tokens}")

    header_set = set(header_rows)
    data_indices = [index for index in all_indices if index not in header_set]
    chunks: list[list[int]] = []
    current_indices = header_rows.copy()
    current_data_count = 0

    for row_index in data_indices:
        candidate_indices = current_indices + [row_index]
        if token_count(candidate_indices) <= max_tokens:
            current_indices = candidate_indices
            current_data_count += 1
            continue

        # A row rejected from the previous group must still fit in a fresh one.
        single_row_indices = header_rows + [row_index]
        if token_count(single_row_indices) > max_tokens:
            raise ValueError(
                f"Table row {row_index} with headers exceeds max_tokens={max_tokens}"
            )
        if current_data_count:
            chunks.append(current_indices)
        current_indices = single_row_indices
        current_data_count = 1

    if current_data_count:
        chunks.append(current_indices)
    return chunks
