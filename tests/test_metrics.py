from rag_agent_system.evaluation.metrics import recall_at_k, hit_rate_at_k
import pytest
def test_recall_at_k():
    recall1=recall_at_k(["x", "a"],{"a", "b"},2)
    hit1=hit_rate_at_k(["x", "a"],{"a", "b"},2)
    assert recall1==0.5,"Recall at k is wrong"
    assert hit1==1.0,"Hit rate at k is wrong"
    recall2 = recall_at_k(["x", "y"], {"a"}, 5)
    hit2 = hit_rate_at_k(["x", "y"], {"a"}, 5)
    assert recall2 == 0.0, "Recall at k is wrong"
    assert hit2 == 0.0, "Hit rate at k is wrong"
    recall3 = recall_at_k(["a", "a", "b"], {"a", "b"}, 2)
    hit3 = hit_rate_at_k(["a", "a", "b"], {"a", "b"}, 2)
    assert recall3 == 0.5, "Recall at k is wrong"
    assert hit3 == 1.0, "Hit rate at k is wrong"
    recall4 = recall_at_k([],{"a"}, 5)
    hit4 = hit_rate_at_k([],{"a"}, 5)
    assert recall4 == 0.0, "Recall at k is wrong"
    assert hit4 == 0.0, "Hit rate at k is wrong"
    with pytest.raises(ValueError, match="relevant_ids"):
        recall_at_k([], set(), 5)

    with pytest.raises(ValueError, match="relevant_ids"):
        hit_rate_at_k([], set(), 5)

@pytest.mark.parametrize("k", [0, -1, 1.5, True])
def test_invalid_k(k):
    with pytest.raises(ValueError):
        recall_at_k(["a"], {"a"}, k)

    with pytest.raises(ValueError):
        hit_rate_at_k(["a"], {"a"}, k)