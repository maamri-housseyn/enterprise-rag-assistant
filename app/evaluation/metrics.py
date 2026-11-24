
def recall_at_k(
    retrieved_ids: list[str],
    relevant_ids: list[str],
    k: int
) -> float:
    """
    Calculate Recall@K.

    Recall@K = relevant retrieved items / total relevant items.
    """
    if k <= 0:
        raise ValueError("k must be greater than 0")

    if not relevant_ids:
        return 0.0

    retrieved_top_k = set(retrieved_ids[:k])
    relevant = set(relevant_ids)

    relevant_retrieved = retrieved_top_k.intersection(relevant)

    return len(relevant_retrieved) / len(relevant)


def precision_at_k(
    retrieved_ids: list[str],
    relevant_ids: list[str],
    k: int
) -> float:
    """
    Calculate Precision@K.

    Precision@K = relevant retrieved items / K.
    """
    if k <= 0:
        raise ValueError("k must be greater than 0")

    retrieved_top_k = set(retrieved_ids[:k])
    relevant = set(relevant_ids)

    relevant_retrieved = retrieved_top_k.intersection(relevant)

    return len(relevant_retrieved) / k



def reciprocal_rank(
    retrieved_ids: list[str],
    relevant_ids: list[str]
) -> float:
    """
    Calculate Reciprocal Rank.

    RR = 1 / rank of the first relevant retrieved item.
    """
    relevant = set(relevant_ids)

    for rank, chunk_id in enumerate(retrieved_ids, start=1):
        if chunk_id in relevant:
            return 1.0 / rank

    return 0.0


def hit_rate_at_k(
    retrieved_ids: list[str],
    relevant_ids: list[str],
    k: int
) -> float:
    """
    Calculate Hit Rate@K.

    Returns 1.0 if at least one relevant item is retrieved in top K,
    otherwise 0.0.
    """
    if k <= 0:
        raise ValueError("k must be greater than 0")

    relevant = set(relevant_ids)

    return float(
        any(chunk_id in relevant for chunk_id in retrieved_ids[:k])
    )
