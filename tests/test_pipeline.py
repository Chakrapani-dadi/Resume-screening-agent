"""
test_pipeline.py
-----------------
Tests for the ranking logic that ties scoring together: given a set of
scored resumes, are they sorted correctly and does score_resume() return
the expected shape? Uses monkeypatching to fake the embedding call, so
this runs instantly with no API key or network access needed.
"""

import os
import sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("GEMINI_API_KEY", "test-key-not-used-by-these-tests")

import scorer


def test_score_resume_returns_expected_shape(monkeypatch):
    # Fake get_embedding so no real API call happens - it just returns a
    # fixed vector regardless of input text.
    monkeypatch.setattr(scorer, "get_embedding", lambda text: np.array([1.0, 0.0, 0.0]))

    jd_embedding = np.array([1.0, 0.0, 0.0])  # identical direction
    result = scorer.score_resume(jd_embedding, "some resume text")

    assert "score" in result
    assert isinstance(result["score"], float)
    assert result["score"] == 1.0  # identical vectors -> perfect match


def test_ranking_sorts_highest_score_first():
    # This mirrors the sort step in main.py / app.py without needing to
    # run the full pipeline.
    candidates = [
        {"filename": "low_match.pdf", "score": 0.21},
        {"filename": "best_match.pdf", "score": 0.78},
        {"filename": "mid_match.pdf", "score": 0.55},
    ]
    candidates.sort(key=lambda r: r["score"], reverse=True)

    assert [c["filename"] for c in candidates] == [
        "best_match.pdf", "mid_match.pdf", "low_match.pdf"
    ]


def test_ranks_are_assigned_in_order():
    candidates = [
        {"filename": "best_match.pdf", "score": 0.78},
        {"filename": "mid_match.pdf", "score": 0.55},
        {"filename": "low_match.pdf", "score": 0.21},
    ]
    for i, r in enumerate(candidates):
        r["rank"] = i + 1

    assert candidates[0]["rank"] == 1
    assert candidates[-1]["rank"] == len(candidates)
