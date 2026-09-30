import pytest

from rag_agent_system.pipeline import RAGPipeline


@pytest.mark.skip(reason="TODO(DAY18): user exercise — remove skip and add core assertions")
def test_pipeline_passes_retrieved_chunks_to_context_builder() -> None:
    """TODO(DAY18): use fakes and assert the retrieved chunks reach the context builder."""

    # Arrange small fake collaborators, call RAGPipeline.query, and assert interactions.
    raise NotImplementedError


@pytest.mark.skip(reason="TODO(DAY18): user exercise — remove skip and add core assertions")
def test_pipeline_returns_answer_and_ranked_sources() -> None:
    """TODO(DAY18): assert answer text and ranked sources on the returned RAGResult."""

    # Keep this test model-free: use deterministic fakes instead of downloading HF weights.
    assert RAGPipeline is not None

