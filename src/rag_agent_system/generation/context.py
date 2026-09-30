"""Retrieved-context assembly contract."""

from rag_agent_system.models import RetrievedChunk


class ContextBuilder:
    """Build bounded, source-labelled context from ranked chunks."""

    def build(self, chunks: list[RetrievedChunk]) -> str:
        """Convert retrieved chunks into the context passed to the prompt.

        TODO(DAY18): choose a stable source label format, join chunks in rank order,
        and enforce a defensible character/token budget without losing traceability.
        """

        raise NotImplementedError("TODO(DAY18): implement ContextBuilder.build")

