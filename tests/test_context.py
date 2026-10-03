from rag_agent_system.generation.context import ContextBuilder
from rag_agent_system.models import DocumentChunk, RetrievedChunk

def test_build_preserves_content_and_source() -> None:
    # Arrange：准备输入
    chunks = [
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

    # Act：调用被测方法
    context = ContextBuilder().build(chunks)
    # Assert：你来补充断言
    # 正文、来源、chunk ID 和引用编号是否都被保留？

    expected = (
        "position:1,rank:1,source:tinystories,chunk_id:story-a\n"
        "Lily found a needle."
    )
    assert context == expected,"Context should be preserved"

def test_build_empty_list_returns_empty_string() -> None:
    context = ContextBuilder().build([])
    assert context == "","Empty Context"


    # 你来断言空列表对应的结果。