"""Retrieved-context assembly contract."""
from rag_agent_system.models import RetrievedChunk

class ContextBuilder:
    """Build source-labelled context from ranked chunks."""
    def build(self, chunks: list[RetrievedChunk]) -> str:
        """Convert retrieved chunks into the context passed to the prompt.

        Preserve the supplied retrieval order and source labels.
        TODO: enforce a character/token budget without losing traceability.
        """

        output:list[str]=[]
        for position,result in enumerate(chunks,start=1):
            rank = result.rank
            chunk_id=result.chunk.chunk_id
            source=result.chunk.source
            if not source:
                source="Unknown"
            text=result.chunk.text
            inf_block=(f"position:{position},rank:{rank},source:{source},chunk_id:{chunk_id}\n"
                       f"{text}")
            output.append(inf_block)
        return "\n\n".join(output)
