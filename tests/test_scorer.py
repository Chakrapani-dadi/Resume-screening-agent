"""
test_scorer.py
--------------
Tests for the pure-math parts of scorer.py (cosine_similarity, tier_for logic).
These don't call the Gemini API - they test the math independently, so they
run instantly and don't need an API key or network access.
"""

import os
import sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# scorer.py creates a Gemini client at import time, which needs an API key
# present (even a fake one) just to construct the client object. No network
# call is made unless we actually invoke get_embedding/generate_reasoning.
os.environ.setdefault("GEMINI_API_KEY", "test-key-not-used-by-these-tests")

from scorer import cosine_similarity


def test_identical_vectors_score_one():
    a = np.array([1, 2, 3])
    b = np.array([1, 2, 3])
    assert cosine_similarity(a, b) == 1.0


def test_opposite_vectors_score_negative_one():
    a = np.array([1, 0, 0])
    b = np.array([-1, 0, 0])
    assert cosine_similarity(a, b) == -1.0


def test_orthogonal_vectors_score_zero():
    a = np.array([1, 0])
    b = np.array([0, 1])
    assert cosine_similarity(a, b) == 0.0


def test_same_direction_different_magnitude_scores_one():
    # Cosine similarity ignores vector length, only direction matters.
    a = np.array([1, 2, 3])
    b = np.array([2, 4, 6])
    assert cosine_similarity(a, b) == 1.0


def test_zero_vector_returns_zero_not_error():
    # A zero-length vector would cause a divide-by-zero in raw cosine math;
    # the function should handle this gracefully instead of crashing.
    a = np.array([0, 0, 0])
    b = np.array([1, 2, 3])
    assert cosine_similarity(a, b) == 0.0
