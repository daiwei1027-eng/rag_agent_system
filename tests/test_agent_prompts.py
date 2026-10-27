"""Dataset selection and input boundaries without any model inference."""

import pytest

from rag_agent_system.agents.prompts import build_agent_prompt


@pytest.mark.parametrize(
    "dataset,expected_corpus,other_corpus",
    [("tinystories", "TinyStories", "SEC"), ("sec", "SEC", "TinyStories")],
)
def test_selects_dataset_rules_and_preserves_question(
    dataset, expected_corpus, other_corpus,
):
    question = "Which source supports {revenue}? 请保留这个问题。"
    prompt = build_agent_prompt(question, dataset=dataset)

    assert expected_corpus in prompt
    assert other_corpus not in prompt
    assert prompt.endswith(f"问题：{question}")
    assert "chunk_id" in prompt and "证据不足" in prompt
    if dataset == "sec":
        assert "报告财年" in prompt and "单位" in prompt
        assert "calculator" in prompt
        assert "只提出一次" not in prompt
        assert "（依据：chunk_id=<编号>）" in prompt


def test_default_preserves_tinystories_callers():
    question = "Who found the needle?"
    prompt = build_agent_prompt(question)

    assert prompt == build_agent_prompt(question, dataset="tinystories")
    assert "请回答 TinyStories 资料库中的问题。" in prompt
    assert "只提出一次简短的英文查询，返回 5 条文段" in prompt


@pytest.mark.parametrize("dataset", ["unknown", "SEC"])
def test_rejects_unknown_dataset(dataset):
    with pytest.raises(ValueError, match="Unknown dataset"):
        build_agent_prompt("Question", dataset=dataset)


@pytest.mark.parametrize(
    "question,error", [(None, TypeError), (" \n\t ", ValueError)],
)
def test_rejects_invalid_question(question, error):
    with pytest.raises(error, match="question"):
        build_agent_prompt(question, dataset="sec")
