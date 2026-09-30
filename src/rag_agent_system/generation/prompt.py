"""Grounded RAG prompt construction contract."""


class PromptBuilder:
    """Create the final instruction/query/context prompt."""

    def build(self, question: str, context: str) -> str:
        """Return a prompt that asks the model to answer from supplied context.

        TODO(DAY18): define the system behavior, no-evidence behavior, source citation
        convention, and clear delimiters between instructions, context, and question.
        """

        raise NotImplementedError("TODO(DAY18): implement PromptBuilder.build")

