from rag_agent_system.config import load_config
from rag_agent_system.generation.generator import HuggingFaceGenerator
from rag_agent_system.generation.prompt import PromptBuilder


def test_generator() -> None:
    config = load_config()
    generator = HuggingFaceGenerator(
        model_name=config.generation.model_name,
        max_new_tokens=64,
        temperature=0.0,
    )

    prompt = PromptBuilder().build(
        question="Who found the needle?",
        context="rank:1,source=tinystories,chunk_id=story-a\n"
                "Lily found a needle.",
        additional_instruction="Answer in one short sentence.",
    )

    answer = generator.generate(prompt)
    assert isinstance(answer, str)
    assert answer.strip(), "Generated answer should not be empty."
    assert "lily" in answer.casefold(), (
        f"Expected an answer mentioning Lily, got: {answer!r}"
    )