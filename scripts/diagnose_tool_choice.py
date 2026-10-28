"""Replay q001's first v1/v3 requests with one shared local model client."""

from __future__ import annotations
from rag_agent_system.agents.prompts import build_agent_prompt
import json
from copy import deepcopy
from datetime import datetime
from pathlib import Path

from rag_agent_system.paths import project_root


def load_first_request(run_dir: Path, query_id: str) -> dict:
    with (run_dir / "per_query.json").open(encoding="utf-8") as f:
        records = json.load(f)
    matches = [record for record in records if record["query_id"] == query_id]
    if len(matches) != 1:
        raise ValueError(f"Expected exactly one {query_id} record in {run_dir}")
    record = matches[0]
    request = record["model_requests"][0]
    if request["messages"] != [{"role": "user", "content": record["prompt"]}]:
        raise ValueError(f"Unexpected first-request messages in {run_dir}")
    return request


def load_inputs() -> tuple[list[dict], dict]:
    base = project_root() / "data/archive/evaluation/historical/stage2"
    runs = (
        ("v1", base / "20261012-160851-010726-agent-v1"),
        ("v3", base / "20261013-090905-274020-agent-v3"),
    )
    inputs = []
    settings = []
    for version, run_dir in runs:
        request = load_first_request(run_dir, "q001")
        with (run_dir / "config.json").open(encoding="utf-8") as f:
            config = json.load(f)
        settings.append({
            "model_name": config["tokenizer and generation model"],
            "max_new_tokens": config["max_new_tokens"],
            "do_sample": config["do_sample"],
        })
        inputs.append({"version": version, "source_run": run_dir.name, "request": request})
    if settings[0] != settings[1] or settings[0]["do_sample"] is not False:
        raise ValueError("Historical generation settings must match and use do_sample=False")
    if inputs[0]["request"]["tools"] != inputs[1]["request"]["tools"]:
        raise ValueError("Historical tool definitions differ")
    return inputs, settings[0]


def main() -> None:
    inputs, settings = load_inputs()
    # Import only when running inference; reading saved inputs needs no model resources.
    question = (
        "Who found a needle in her room and wanted her mother "
        "to sew a button on her shirt?"
    )

    # 用历史 v1 请求复制出对照输入，只替换提示词。
    new_request = deepcopy(inputs[0]["request"])
    new_request["messages"][0]["content"] = build_agent_prompt(question)

    inputs[1] = {
        "version": "v1_citation",
        "source_run": "current PROMPT_TEMPLATE",
        "request": new_request,
    }
    from rag_agent_system.agents.llm_client import LocalLLMClient

    run_id = datetime.now().astimezone().strftime("%Y%m%d-%H%M%S-%f")
    run_dir = project_root() / "data/local/diagnostics" / f"{run_id}-tool-choice-diagnostic"
    run_dir.mkdir(parents=True, exist_ok=False)
    record = {
        "created_at": datetime.now().astimezone().isoformat(),
        "query_id": "q001",
        "scope": "First model response only; tools are not executed.",
        "generation": settings,
        "inputs": inputs,
        "results": [],
    }
    output_path = run_dir / "diagnostic.json"

    def save_record() -> None:
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(record, f, ensure_ascii=False, indent=2)

    save_record()
    # Both requests share this client and its lazily loaded model/tokenizer.
    client = LocalLLMClient(
        settings["model_name"], max_new_tokens=settings["max_new_tokens"]
    )
    client._load_resources()
    for item in inputs:
        request = deepcopy(item["request"])
        try:
            response = client.chat(request["messages"], request["tools"])
        except ValueError as exc:
            result = {"version": item["version"], "error": str(exc)}
        else:
            result = {
                "version": item["version"],
                "response": response,
                "requested_search": any(
                    call["name"] == "search_documents"
                    for call in response.get("tool_calls", [])
                ),
            }
        record["results"].append(result)
        save_record()
        # ASCII escapes keep the Windows console safe; the JSON file retains UTF-8.
        print(json.dumps(result, ensure_ascii=True, indent=2))
    print(f"Saved diagnostic to {output_path}")


if __name__ == "__main__":
    main()
