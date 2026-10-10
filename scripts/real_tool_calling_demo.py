
import torch
from transformers import AutoTokenizer,  AutoModelForCausalLM
from rag_agent_system.config import load_config
from rag_agent_system.tools.schemas import CALCULATOR_SCHEMA


def main() -> None:
    config = load_config()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    tokenizer = AutoTokenizer.from_pretrained(
        config.generation.model_name,
        local_files_only=True,
    )
    messages = [
        {"role": "user", "content": "请使用 calculator 计算 12 × 8，并根据工具结果回答。"},
    ]
    tools = [
        {
            "type": "function",
            "function": CALCULATOR_SCHEMA,
        }
    ]

    model = AutoModelForCausalLM.from_pretrained(
        config.generation.model_name,
        local_files_only=True,
    )
    model.to(device)
    model.eval()
    formatted_prompt = tokenizer.apply_chat_template(
        messages,
        tools=tools,
        tokenize=False,
        add_generation_prompt=True,
    )

    inputs = tokenizer(
        formatted_prompt,
        return_tensors="pt",
        add_special_tokens=False,
    ).to(device)
    with torch.inference_mode():
        output = model.generate(
            **inputs,
            max_new_tokens=config.generation.max_new_tokens,
            do_sample=False,
        )
    input_length = inputs["input_ids"].shape[1]
    new_tokens = output[0, input_length:]
    answer = tokenizer.decode(new_tokens, skip_special_tokens=True)
    print(answer.strip())

if __name__ == "__main__":
    main()
