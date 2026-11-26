
import pytest


from app.evaluation.metrics import (
    recall_at_k,
    precision_at_k,
    reciprocal_rank,
    hit_rate_at_k,
)

def test_recall_at_k():
    retrieved = ["chunk_1", "chunk_2", "chunk_3"]
    relevant = ["chunk_2", "chunk_3", "chunk_4"]

    assert recall_at_k(retrieved, relevant, 3) == pytest.approx(2 / 3)


def test_precision_at_k():
    retrieved = ["chunk_1", "chunk_2", "chunk_3"]
    relevant = ["chunk_2", "chunk_3", "chunk_4"]

    assert precision_at_k(retrieved, relevant, 3) == pytest.approx(2 / 3)


def test_no_relevant_results():
    retrieved = ["chunk_1", "chunk_2"]
    relevant = ["chunk_3", "chunk_4"]

    assert recall_at_k(retrieved, relevant, 2) == 0.0
    assert precision_at_k(retrieved, relevant, 2) == 0.0


def test_invalid_k():
    with pytest.raises(ValueError):
        recall_at_k(["chunk_1"], ["chunk_1"], 0)

    with pytest.raises(ValueError):
        precision_at_k(["chunk_1"], ["chunk_1"], 0)



def test_reciprocal_rank():
    retrieved = ["chunk_1", "chunk_2", "chunk_3"]
    relevant = ["chunk_2", "chunk_3"]

    assert reciprocal_rank(retrieved, relevant) == 0.5


def test_reciprocal_rank_no_relevant_result():
    retrieved = ["chunk_1", "chunk_2"]
    relevant = ["chunk_3"]

    assert reciprocal_rank(retrieved, relevant) == 0.0


def test_hit_rate_at_k():
    retrieved = ["chunk_1", "chunk_2", "chunk_3"]
    relevant = ["chunk_2", "chunk_4"]

    assert hit_rate_at_k(retrieved, relevant, 3) == 1.0


def test_hit_rate_at_k_no_relevant_result():
    retrieved = ["chunk_1", "chunk_2", "chunk_3"]
    relevant = ["chunk_4"]

    assert hit_rate_at_k(retrieved, relevant, 3) == 0.0
