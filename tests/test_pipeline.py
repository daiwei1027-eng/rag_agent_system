from rag_agent_system.models import DocumentChunk, RetrievedChunk
from rag_agent_system.pipeline import RAGPipeline


class FakeRetriever:
    def __init__(self) -> None:
        self.last_call = None
        self.results = [
            RetrievedChunk(
                chunk=DocumentChunk(
                    chunk_id="story-a",
                    text="Lily found a needle.",
                    source="tinystories",
                ),
                score=0.8,
                rank=1,
            )
        ]

    def retrieve(self, query: str, top_k: int = 3):
        self.last_call = (query, top_k)
        return self.results


class FakeContextBuilder:
    def __init__(self) -> None:
        self.received_chunks = None

    def build(self, chunks):
        self.received_chunks = chunks
        return "TEST_CONTEXT"


class FakePromptBuilder:
    def __init__(self) -> None:
        self.last_call = None

    def build(self, question, context, *, additional_instruction=None):
        self.last_call = (question, context, additional_instruction)
        return "TEST_PROMPT"


class FakeGenerator:
    def __init__(self) -> None:
        self.received_prompt = None

    def generate(self, prompt):
        self.received_prompt = prompt
        return "Lily found the needle."


def test_pipeline() -> None:
    retriever = FakeRetriever()
    context_builder = FakeContextBuilder()
    prompt_builder = FakePromptBuilder()
    generator = FakeGenerator()

    pipeline = RAGPipeline(
        retriever=retriever,
        context_builder=context_builder,
        prompt_builder=prompt_builder,
        generator=generator,
        top_k=2,
    )

    result = pipeline.query(
        "  Who found the needle?  ",
        additional_instruction="Answer briefly.",
    )

    # 由你补 assert：
    # 1. retriever.last_call 是否收到清理后的问题和 top_k=2？
    # 2. context_builder.received_chunks 是否等于 retriever.results？
    # 3. prompt_builder.last_call 是否包含问题、TEST_CONTEXT 和补充要求？
    # 4. generator.received_prompt 是否是 TEST_PROMPT？
    # 5. result 是否保留了清理后的问题、回答和 tuple 类型的来源？
    assert retriever.last_call == ("Who found the needle?", 2),"Retriever.last_call doesn't receive question and top_k=2"
    assert context_builder.received_chunks == retriever.results,"Context_Builder doesn't receive RetrievedChunk correctly"
    assert prompt_builder.last_call == (
        "Who found the needle?",
        "TEST_CONTEXT",
        "Answer briefly.",
    ), "PromptBuilder received incorrect arguments."
    assert generator.received_prompt == "TEST_PROMPT","Generator doesn't receive Prompt correctly"
    assert result.question == "Who found the needle?","Result doesn't receive the question correctly"
    assert result.answer == "Lily found the needle."
    assert result.sources == tuple(retriever.results)
    assert result.ranked_chunks == tuple(retriever.results)
    assert result.context_text == "TEST_CONTEXT"
    assert result.prompt_text == generator.received_prompt