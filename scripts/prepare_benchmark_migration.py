"""Prepare story-scoped v2 evidence candidates; leave semantic review pending."""

from __future__ import annotations

import argparse
from bisect import bisect_right
from collections import Counter, defaultdict
from copy import deepcopy
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path

from rag_agent_system.paths import project_root, resolve_project_path


DEFAULT_BUNDLE = (
    "data/chunking_v2/20261013-141109-775427-qwen128-overlap32-story-boundaries"
)


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        while block := f.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def occurrences(text: str, quote: str) -> list[int]:
    positions = []
    start = 0
    while (position := text.find(quote, start)) >= 0:
        positions.append(position)
        start = position + 1
    return positions


def normalize_space(text: str) -> str:
    return " ".join(text.split())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle-dir", default=DEFAULT_BUNDLE)
    args = parser.parse_args()
    bundle = resolve_project_path(args.bundle_dir)
    old_dir = project_root() / "data/benchmark"
    manifest = read_json(bundle / "build_manifest.json")
    for name in ("source_stories.json", "tinystories_chunks.json", "tinystories.faiss"):
        if sha256(bundle / name) != manifest["files_sha256"][name]:
            raise ValueError(f"Bundle fingerprint mismatch: {name}")
    old_chunks_path = project_root() / "data/tinystories_chunks.json"
    if sha256(old_chunks_path) != manifest["old_asset_sha256"][old_chunks_path.name]:
        raise ValueError("Original chunks changed since source verification")
    old_manifest = read_json(old_dir / "tinystories_benchmark_manifest.json")
    queries_path = old_dir / "tinystories_queries.jsonl"
    if sha256(queries_path) != old_manifest["dataset_sha256"]:
        raise ValueError("Original benchmark fingerprint mismatch")
    queries = [json.loads(line) for line in queries_path.read_text(encoding="utf-8-sig").splitlines()
               if line.strip()]
    old_chunks = {item["chunk_id"]: item for item in read_json(old_chunks_path)}
    stories = read_json(bundle / "source_stories.json")
    chunks = read_json(bundle / "tinystories_chunks.json")
    if len(queries) != 45 or sum(q["answerable"] for q in queries) != 40:
        raise ValueError("Expected the fixed 45/40/5 benchmark")

    # Recreate each old token window's source position; do not guess from IDs alone.
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(
        manifest["chunk_tokenizer"], use_fast=True, local_files_only=True,
    )
    global_offsets = []
    story_starts = []
    base = 0
    for story in stories:
        story_starts.append(base)
        encoded = tokenizer(story["text"], add_special_tokens=False, truncation=False,
                            return_offsets_mapping=True)
        if len(encoded["input_ids"]) != story["retained_qwen_token_count"]:
            raise ValueError(f"Source token count changed: {story['story_id']}")
        global_offsets.extend((base + a, base + b) for a, b in encoded["offset_mapping"])
        base += len(story["text"])
    if len(global_offsets) != manifest["source_qwen_body_token_count"]:
        raise ValueError("Source token budget mismatch")
    full_text = "".join(story["text"] for story in stories)
    by_story = defaultdict(list)
    for chunk in chunks:
        by_story[chunk["metadata"]["story_id"]].append(chunk)
    draft = []
    reviews = []
    positive_story_ids = {}

    for query in queries:
        item = deepcopy(query)
        item["source_annotation_status"] = query["annotation_status"]
        item["annotation_status"] = "pending_migration_review"
        item["review_provenance"] = "Automatic source-span migration; semantic review pending."
        item["user_review_completed"] = False
        item.pop("user_review_date", None)
        if not query["answerable"]:
            draft.append(item)
            continue
        spans = []
        for evidence in query["evidence"]:
            old = old_chunks[evidence["chunk_id"]]
            quote = evidence["quote"]
            if not quote or quote not in old["text"]:
                raise ValueError(f"Legacy quote missing from its chunk: {query['query_id']}")
            start = old["metadata"]["faiss_id"] * 96
            end = min(start + 128, len(global_offsets))
            a, b = global_offsets[start][0], global_offsets[end - 1][1]
            found = occurrences(full_text[a:b], quote)
            if len(found) != 1:
                raise ValueError(f"Ambiguous source quote for {query['query_id']}: {found}")
            quote_start = a + found[0]
            story_index = bisect_right(story_starts, quote_start) - 1
            story = stories[story_index]
            local_start = quote_start - story_starts[story_index]
            local_end = local_start + len(quote)
            if local_end > len(story["text"]):
                raise ValueError(f"Evidence crosses source stories: {query['query_id']}")
            span = {"story_id": story["story_id"], "source_index": story_index,
                    "start_char": local_start, "end_char": local_end, "quote": quote}
            if span not in spans:
                spans.append(span)
        story_ids = sorted({span["story_id"] for span in spans})
        positive_story_ids[query["query_id"]] = story_ids
        candidate_evidence = []
        for span in spans:
            for chunk in by_story[span["story_id"]]:
                meta = chunk["metadata"]
                if meta["start_char"] <= span["start_char"] and span["end_char"] <= meta["end_char"]:
                    candidate_evidence.append({"chunk_id": chunk["chunk_id"], "quote": span["quote"]})
        item["relevant_chunk_ids"] = sorted({e["chunk_id"] for e in candidate_evidence})
        item["evidence"] = candidate_evidence
        item["migration"] = {
            "status": "quote_candidates_require_semantic_review" if candidate_evidence
                      else "quote_split_requires_review",
            "old_relevant_chunk_ids": query["relevant_chunk_ids"],
            "old_evidence": query["evidence"], "story_ids": story_ids, "source_spans": spans,
        }
        draft.append(item)
        reviews.append({
            "query_id": query["query_id"], "answerable": True,
            "question": query["query"], "expected_answer": query["expected_answer"],
            "status": item["migration"]["status"], "old_relevant_chunk_ids": query["relevant_chunk_ids"],
            "candidate_chunk_ids": item["relevant_chunk_ids"], "source_spans": spans,
            "candidate_documents": [c for sid in story_ids for c in by_story[sid]
                                    if c["chunk_id"] in item["relevant_chunk_ids"]],
            "all_target_story_documents": [c for sid in story_ids for c in by_story[sid]],
            "source_story_texts": [stories[s["source_index"]]["text"] for s in spans],
            "review_checks": ["Full answer and question conditions supported?",
                              "All sufficient single-chunk IDs included?",
                              "Correct target story and exact quote attribution?"],
        })

    old_absence = {q["query_id"]: q for q in read_json(old_dir / "tinystories_absence_evidence.json")}
    new_absence = []
    for item in draft:
        if item["answerable"]:
            continue
        previous = old_absence[item["query_id"]]
        story_ids = positive_story_ids[item["paired_with"]]
        if len(story_ids) != 1:
            raise ValueError(f"Negative control has ambiguous story: {item['query_id']}")
        documents = by_story[story_ids[0]]
        source_index = documents[0]["metadata"]["source_index"]
        text = stories[source_index]["text"]
        story_matches = normalize_space(text) == normalize_space(previous["story_text"])
        ids = [c["chunk_id"] for c in documents]
        item["absence_evidence"]["story_chunk_ids"] = ids
        item["relevant_chunk_ids"] = []
        item["evidence"] = []
        item["migration"] = {
            "status": "story_scope_requires_absence_review" if story_matches
                      else "legacy_story_text_difference_requires_review",
            "story_ids": story_ids,
            "old_story_chunk_ids": previous["story_chunk_ids"],
            "legacy_story_text_matches_ignoring_whitespace": story_matches,
        }
        keyword_matches = [c for c in chunks if all(
            word.lower() in c["text"].lower() for word in previous["search_keywords"]
        )]
        new_absence.append({
            "query_id": item["query_id"], "annotation_status": "pending_migration_review",
            "story_id": story_ids[0], "story_chunk_ids": ids, "story_text": text,
            "review_reason": previous["review_reason"], "search_keywords": previous["search_keywords"],
            "full_corpus_keyword_match_ids": [c["chunk_id"] for c in keyword_matches],
            "full_corpus_keyword_matches": [{"chunk_id": c["chunk_id"], "text": c["text"]}
                                           for c in keyword_matches],
            "limitation": previous["limitation"], "migration": item["migration"],
        })
        reviews.append({
            "query_id": item["query_id"], "answerable": False,
            "question": item["query"], "expected_answer": item["expected_answer"],
            "status": item["migration"]["status"], "candidate_chunk_ids": ids,
            "source_story_texts": [text], "all_target_story_documents": documents,
            "old_story_text": previous["story_text"],
            "review_checks": ["Correct complete target story?", "Requested information still absent?"],
        })
    reviews.sort(key=lambda row: row["query_id"])
    assert [q["query_id"] for q in draft] == [q["query_id"] for q in queries]
    assert all(a["query"] == b["query"] and a["expected_answer"] == b["expected_answer"]
               for a, b in zip(draft, queries))
    output = bundle / "benchmark_migration_draft"
    output.mkdir(exist_ok=False)
    (output / "tinystories_queries.jsonl").write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in draft), encoding="utf-8",
    )
    for name, value in (("tinystories_absence_evidence.json", new_absence),
                        ("migration_review.json", reviews)):
        (output / name).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    report = ["# 新证据标注迁移复核草稿", "", "全部条目等待人工复核，禁止直接用于正式评分。",
              "引文命中仅用于生成候选，不自动证明完整答案或人物/事件条件被支持。", "",
              "| ID | 可回答 | 状态 | 新证据候选/负例故事块 |", "|---|---|---|---|"]
    for row in reviews:
        report.append(f"| {row['query_id']} | {row['answerable']} | {row['status']} | "
                      f"{', '.join(row['candidate_chunk_ids']) or '无完整引文候选'} |")
    for row in reviews:
        report.extend(["", f"## {row['query_id']}", "", f"问题：{row['question']}", "",
                       f"预期答案：{row['expected_answer']}", "",
                       "检查：" + "；".join(row["review_checks"]), "", "### 原始目标故事", ""])
        for text in row["source_story_texts"]:
            report.extend(["```text", text, "```", ""])
        report.extend(["### 全部目标故事文段（候选外的文段也需检查）", ""])
        for chunk in row["all_target_story_documents"]:
            report.extend([f"**{chunk['chunk_id']}**", "", "```text", chunk["text"], "```", ""])
    (output / "migration_review.md").write_text("\n".join(report), encoding="utf-8")
    summary = {"created_at": datetime.now().astimezone().isoformat(),
               "status": "all_annotations_pending_semantic_review", "query_count": len(draft),
               "answerable_count": sum(q["answerable"] for q in draft),
               "status_counts": dict(Counter(row["status"] for row in reviews)),
               "old_benchmark_sha256": sha256(queries_path), "bundle_version": manifest["version"],
               "bundle_sha256": manifest["files_sha256"],
               "draft_files_sha256": {p.name: sha256(p) for p in output.iterdir() if p.is_file()}}
    (output / "migration_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary["status_counts"], ensure_ascii=False, indent=2))
    print(f"Saved pending review files to {output}")


if __name__ == "__main__":
    main()
