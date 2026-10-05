"""Future evaluation contracts; add metrics after the Day 18 baseline works."""
def recall_at_k(
    retrieved_ids: list[str],
    relevant_ids: set[str],
    k: int,
) -> float:
    """前 k 条命中的相关 ID 数 / 全部相关 ID 数。"""
    counter =0
    if not type(k) is int or k <= 0:
        raise ValueError('k must be positive integer')
    if not relevant_ids:
        raise ValueError("relevant_ids must not be empty")
    if not retrieved_ids:
        return 0.0
    for m,retrieved_id in enumerate(retrieved_ids[:k]):
        if retrieved_id in relevant_ids and retrieved_id not in retrieved_ids[:m]:
            counter+=1
    return counter/len(relevant_ids)


def hit_rate_at_k(
    retrieved_ids: list[str],
    relevant_ids: set[str],
    k: int,
) -> float:
    """前 k 条至少命中一个相关 ID，返回 1.0，否则返回 0.0。"""
    if not type(k) is int or k <= 0:
        raise ValueError('k must be positive integer')
    if not relevant_ids:
        raise ValueError("relevant_ids must not be empty")
    if not retrieved_ids:
        return 0.0
    for retrieved_id in retrieved_ids[:k]:
        if retrieved_id in relevant_ids:
            return 1.0
    return 0.0

def reciprocal_rank(relevant: list[bool]) -> float:
    """Return reciprocal rank for the first relevant result, or zero if absent."""

    for rank, is_relevant in enumerate(relevant, start=1):
        if is_relevant:
            return 1.0 / rank
    return 0.0

