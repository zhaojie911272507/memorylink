from __future__ import annotations

from typing import Any


DIMENSION_WEIGHTS = {
    "consistency": 0.30,
    "recall": 0.25,
    "personality": 0.20,
    "knowledge": 0.15,
    "forgetting": 0.10,
}


def score_expected(reply: str, expected: list[str]) -> dict[str, Any]:
    hits = sum(1 for item in expected if item.lower() in reply.lower())
    ratio = hits / max(1, len(expected))
    return {"hits": hits, "total": len(expected), "ratio": ratio}


def weighted_score(dimension_scores: dict[str, float]) -> float:
    total = 0.0
    for dimension, weight in DIMENSION_WEIGHTS.items():
        total += dimension_scores.get(dimension, 0.0) * weight
    return round(total, 4)

