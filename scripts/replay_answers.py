"""Stage 3 exercise: compare answers with the same saved tool evidence.

Implement the three functions below before running model inference.
Keep agents/prompts.py and the parent run unchanged.
"""

from __future__ import annotations

from time import perf_counter

from rag_agent_system.agents.llm_client import LocalLLMClient
import hashlib
import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Literal, TypedDict
from rag_agent_system.paths import project_root
from datetime import datetime

PARENT_RUN = project_root() / (
    "data/evaluation/stage2/"
    "20261013-143642-156957-agent-stage2-story-boundaries-qwen128-overlap32-v2-reviewed"
)


class ReplayResult(TypedDict):
    status: Literal["completed", "requested_tool", "model_error"]
    answer: str
    trace: list[dict[str, Any]]
    error: str | None


def load_parent_run(
    parent_dir: Path = PARENT_RUN,
) -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, Any]]:
    """Read the frozen run and fingerprint the files used as replay input."""
    records_path = parent_dir / "per_query.json"
    settings_path = parent_dir / "config.json"
    records = json.loads(records_path.read_text(encoding="utf-8-sig"))
    settings = json.loads(settings_path.read_text(encoding="utf-8-sig"))
    provenance = {
        "parent_run": str(parent_dir.resolve()),
        "parent_files_sha256": {
            path.name: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in (records_path, settings_path)
        },
    }
    return records, settings, provenance


def load_answer_request(record: dict[str, Any]) -> dict[str, Any]:
    result=record["result"]
    requests=record["model_requests"]
    trace = result["trace"]
    if not requests:
        raise ValueError("Empty requests list")
    request=requests[-1]
    if result["status"] != "completed":
        raise ValueError("Request status is not completed")
    if result["error"] is not None  :
        raise ValueError("Error in request")
    if not trace:
        raise ValueError("Empty trace")
    last_trace=trace[-1]
    if last_trace.get("tool_calls"):
        raise ValueError("Final response still requests tools")
    if last_trace["role"] != "assistant":
        raise ValueError("Assistant role is not in last trace")
    content = last_trace.get("content")
    if not isinstance(content, str) or not content.strip():
        raise ValueError("Final content must be a non-empty string")
    if request["messages"] != trace[:-1]:
        raise ValueError("Messages don't match trace!")
    return deepcopy(request)
def build_answer_variant(
    request: dict[str, Any], instruction: str,
) -> dict[str, Any]:
    if not isinstance(instruction, str) or not instruction.strip():
        raise ValueError("instruction must be a non-empty string")
    copy_messages=deepcopy(request)
    copy_messages["messages"].append({
        "role": "user",
        "content": instruction,
    })
    return copy_messages



def replay_once(client, request: dict[str, Any]) -> ReplayResult:
    trace = deepcopy(request["messages"])
    try:
        response = client.chat(
            request["messages"],
            request["tools"],
        )
    except (ValueError, OSError, RuntimeError) as exc:
        return {
            "status": "model_error",
            "answer": "",
            "trace": trace,
            "error": f"{type(exc).__name__}: {exc}"
        }

    if not isinstance(response, dict):
        return {
            "status": "model_error",
            "answer": "",
            "trace": trace,
            "error": "response is not a dict",
        }
    if response.get("role") != "assistant":
        return {
            "status": "model_error",
            "answer": "",
            "trace": trace,
            "error": "response role is not assistant",
        }
    tool_calls = response.get("tool_calls")
    if tool_calls is not None and not isinstance(tool_calls, list):
        return {
        "status": "model_error",
        "answer": "",
        "trace": trace,
        "error": "tool_calls is not a list",
    }
    if tool_calls:
        for tool_call in tool_calls:
            if not isinstance(tool_call, dict):
                return {
                    "status": "model_error",
                    "answer": "",
                    "trace": trace,
                    "error": "Tool call is not dict"
                }
            for field in ("id", "name", "arguments"):
                if field not in tool_call:
                    return {
                        "status": "model_error",
                        "answer": "",
                        "trace": trace,
                        "error": f"{field} Missing"
                    }
            if not isinstance(tool_call["arguments"], dict):
                return {
                    "status": "model_error",
                    "answer": "",
                    "trace": trace,
                    "error": "ID->str,name->str,arguments->dict"
                }
            if not (
                    isinstance(tool_call["name"], str)
                    and isinstance(tool_call["id"], str)
            ):
                return {
                    "status": "model_error",
                    "answer": "",
                    "trace": trace,
                    "error": "ID->str,name->str,arguments->dict"
                }
            if not (tool_call["id"].strip() and tool_call["name"].strip()):
                return {
                    "status": "model_error",
                    "answer": "",
                    "trace": trace,
                    "error": "ID or name is empty"
                }
        trace.append(deepcopy(response))
        return {
            "status": "requested_tool",
            "answer": "",
            "trace": trace,
            "error": None
        }
    content = response.get("content")
    if not isinstance(content, str) or not content.strip():
        return {
            "status": "model_error",
            "answer": "",
            "trace": trace,
            "error": "response content is empty or just not a string",
        }
    trace.append(deepcopy(response))
    return {
        "status": "completed",
        "answer": response["content"],
        "trace": trace,
        "error": None,
    }
def main() -> None:
    records, settings, provenance = load_parent_run()
    parent_llm = LocalLLMClient(
        model_name=settings["tokenizer and generation model"],
        max_new_tokens=settings["max_new_tokens"],
    )
    parent_llm._load_resources()
    instruction = (
        "请只回答问题所问的内容，不补充额外细节。"
        "回答中的事实必须由所引原文直接支持，并在句末注明对应的 chunk_id。"
        "若原文未说明所问信息，请明确回答“证据不足，原文未说明”。"
    )
    started_at = datetime.now().astimezone()
    config_snapshot = {
        "started_at": started_at.isoformat(),
        "model_name": settings["tokenizer and generation model"],
        "max_new_tokens": settings["max_new_tokens"],
        "do_sample": settings["do_sample"],
        "instruction": instruction,
        "provenance": provenance,
    }
    run_id = started_at.strftime("%Y%m%d-%H%M%S-%f")
    run_dir = (
            project_root()
            / "data/evaluation/stage3"
            / f"{run_id}-answer-replay-v1"
    )
    run_dir.mkdir(parents=True, exist_ok=False)
    with (run_dir / "config.json").open(
            "w", encoding="utf-8"
    ) as f:
        json.dump(config_snapshot, f, ensure_ascii=False, indent=2)
    exp=[]
    requests_snapshot = []
    for record in records:
        request=load_answer_request(record)
        a_request=deepcopy(request)
        b_request=build_answer_variant(a_request, instruction)
        for group, request in (("A", a_request), ("B", b_request)):
            requests_snapshot.append({
                "query_id": record["query_id"],
                "group": group,
                "request": request,
            })
            with (run_dir / "requests.json").open("w", encoding="utf-8") as f:
                json.dump(requests_snapshot, f, ensure_ascii=False, indent=2)
            start = perf_counter()
            result = replay_once(parent_llm, request)
            elapsed_seconds = perf_counter() - start
            exp.append({
                "query_id": record["query_id"],
                "group": group,
                "request": request,
                "elapsed_seconds": elapsed_seconds,
                "result": result,
            })
            with (run_dir / "per_query.json").open(
                    "w", encoding="utf-8"
            ) as f:
                json.dump(exp, f, ensure_ascii=False, indent=2)
    # 1. 根据父实验配置创建客户端，预加载一次
    # 2. 设置 B 组 instruction 和本次输出目录
    # 3. 遍历 records，构造 A、B 两份请求
    # 4. 每次调用前保存请求，在外层计时并调用 replay_once
    # 5. 保存结果、耗时和父实验来源


if __name__ == "__main__":
    main()