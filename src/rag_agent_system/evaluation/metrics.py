"""Future evaluation contracts; add metrics after the Day 18 baseline works."""


def reciprocal_rank(relevant: list[bool]) -> float:
    """Return reciprocal rank for the first relevant result, or zero if absent."""

    for rank, is_relevant in enumerate(relevant, start=1):
        if is_relevant:
            return 1.0 / rank
    return 0.0

