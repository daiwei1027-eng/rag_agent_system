"""Hugging Face text-generation contract."""
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

class HuggingFaceGenerator:
    """Generate an answer with a lazily loaded Hugging Face model."""

    def __init__(
        self,
        model_name: str,
        *,
        max_new_tokens: int ,
        temperature: float ,
    ) -> None:
        self.model_name = model_name
        self.max_new_tokens = max_new_tokens
        self.temperature = temperature
        self._tokenizer = None
        self._model = None
        self._device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )
        if temperature < 0:
            raise ValueError("temperature must be non-negative.")
        if type(max_new_tokens) is not int or max_new_tokens <= 0:
            raise ValueError("max_new_tokens must be a positive integer.")
    def _load_resources(self) -> None:
        """Load resources once and reuse them."""

        if self._model is not None and self._tokenizer is not None:
            return

        tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        model = AutoModelForCausalLM.from_pretrained(self.model_name)
        model.to(self._device)
        model.eval()

        self._tokenizer = tokenizer
        self._model = model
    def generate(self, prompt: str) -> str:
        """Run model inference and return only the newly generated answer text.

        Reuse cached resources and apply the model's chat template.
        Sample at positive temperature; use greedy decoding at zero temperature.
        """
        if not isinstance(prompt, str):
            raise TypeError("prompt must be a string.")
        if not prompt.strip():
            raise ValueError("prompt cannot be empty.")

        self._load_resources()

        messages = [
            {"role": "user", "content": prompt},
        ]

        formatted_prompt = self._tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )

        inputs = self._tokenizer(
            formatted_prompt,
            return_tensors="pt",
            add_special_tokens=False,
        ).to(self._device)
        with torch.inference_mode():
            if self.temperature > 0:
                output = self._model.generate(
                    **inputs,
                    max_new_tokens=self.max_new_tokens,
                    do_sample=True,
                    temperature=self.temperature,
                )
            else:
                output = self._model.generate(
                    **inputs,
                    max_new_tokens=self.max_new_tokens,
                    do_sample=False,
                )
        input_length=inputs["input_ids"].shape[1]
        new_tokens=output[0,input_length:]
        answer=self._tokenizer.decode(new_tokens,skip_special_tokens=True)
        return answer.strip()

