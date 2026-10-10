"""Local Qwen adapter for the Agent's ``LLMClient.chat`` contract."""
import json
from typing import Any
import torch
from transformers import AutoTokenizer,  AutoModelForCausalLM
import re
class LocalLLMClient:
    """Turn multi-message, tool-aware local generation into Agent messages."""

    def __init__(self, model_name: str, *, max_new_tokens:int) -> None:
        if not isinstance(model_name, str) or not model_name.strip():
            raise ValueError("model_name must be a non-empty string")
        if type(max_new_tokens) is not int or max_new_tokens <= 0:
            raise ValueError("max_new_tokens must be a positive integer")
        self.max_new_tokens = max_new_tokens
        self.model_name = model_name.strip()
        self._device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self._tokenizer = None
        self._model = None
        self._tool_call_counter=0

    def _load_resources(self) -> None:
        if self._model is not None and self._tokenizer is not None:
            return
        else:
            self._tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                local_files_only=True,
            )
            self._model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                local_files_only=True,
            )
            self._model.to(self._device)
            self._model.eval()

    def _generate_text(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
    ) -> str:
        self._load_resources()
        formatted_tools = [
            {"type": "function", "function": schema}
            for schema in tools
        ]
        formatted_prompt = self._tokenizer.apply_chat_template(
            messages,
            tools=formatted_tools,
            tokenize=False,
            add_generation_prompt=True,
        )

        inputs = self._tokenizer(
            formatted_prompt,
            return_tensors="pt",
            add_special_tokens=False,
        ).to(self._device)
        with torch.inference_mode():
            output = self._model.generate(
                **inputs,
                max_new_tokens=self.max_new_tokens,
                do_sample=False,
            )
        input_length = inputs["input_ids"].shape[1]
        new_tokens = output[0, input_length:]
        answer = self._tokenizer.decode(new_tokens, skip_special_tokens=True)
        return answer

    def chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
    ) -> dict[str, Any]:
        raw_response = self._generate_text(messages, tools)
        expected_output={
    "role": "assistant",
    "content": "",
    "tool_calls": [
    ],
}
        opening_count = raw_response.count("<tool_call>")
        closing_count = raw_response.count("</tool_call>")
        pattern = re.compile(r"<tool_call>\s*(.*?)\s*</tool_call>", re.DOTALL)
        matches = list(pattern.finditer(raw_response))
        if len(matches)==opening_count==closing_count>0:
            for match in matches:
                call = json.loads(match.group(1))
                if not isinstance(call, dict):
                    raise ValueError("Tool call must be a JSON object")
                name = call.get("name")
                if not isinstance(name, str) or not name.strip():
                    raise ValueError("Tool call name must be a non-empty string")
                arguments = call.get("arguments")
                if not isinstance(arguments, dict):
                    raise ValueError("Tool call arguments must be an object")
                expected={
                    "id":"call"+str(self._tool_call_counter),
                    "name":call["name"],
                    "arguments":call["arguments"],
                }
                expected_output["tool_calls"].append(expected)
                self._tool_call_counter+=1
            return expected_output
        elif len(matches)==closing_count==opening_count==0:
            if not raw_response.strip():
                raise ValueError("Tool response is Empty!")
            return {"role":"assistant","content":raw_response.strip()}
        else:
            raise ValueError("Number of <tool_call> and <tool_call> must be equal>")

