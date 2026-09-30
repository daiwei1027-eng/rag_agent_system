"""Hugging Face text-generation contract."""


class HuggingFaceGenerator:
    """Generate an answer with a lazily loaded Hugging Face model."""

    def __init__(
        self,
        model_name: str,
        *,
        max_new_tokens: int = 256,
        temperature: float = 0.2,
    ) -> None:
        self.model_name = model_name
        self.max_new_tokens = max_new_tokens
        self.temperature = temperature

    def generate(self, prompt: str) -> str:
        """Run model inference and return only the newly generated answer text.

        TODO(DAY18): load/cache tokenizer and model, apply an appropriate chat template,
        run inference under no-grad/inference mode, and decode only generated tokens.
        Consider device selection and deterministic behavior when temperature is zero.
        """

        raise NotImplementedError("TODO(DAY18): implement HuggingFaceGenerator.generate")

