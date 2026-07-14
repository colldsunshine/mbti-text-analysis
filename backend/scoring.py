"""MBTI type selection, confidence levels, and display percentages."""

import math
from typing import Dict

from backend.config import ORDER, PAIRS, THRESHOLDS


DISPLAY_PERCENT_CAPS = {
    "low": 0.10,
    "medium": 0.22,
    "high": 0.32,
}
CONFIDENCE_RANK = {"low": 0, "medium": 1, "high": 2}


def normalize_prob_around_threshold(prob: float, threshold: float) -> float:
    if prob < threshold:
        return 0.5 * (prob / threshold)
    return 0.5 + 0.5 * ((prob - threshold) / (1.0 - threshold))


def display_percent(prob: float, threshold: float, confidence: str) -> float:
    raw = normalize_prob_around_threshold(prob, threshold)
    strength = abs(raw - 0.5)
    cap = DISPLAY_PERCENT_CAPS.get(confidence, DISPLAY_PERCENT_CAPS["medium"])
    shown = 0.5 + math.copysign(min(strength, cap), raw - 0.5)
    return round(shown * 100, 1)


def axis_confidence(prob: float, threshold: float, std_logit: float, word_count: int) -> str:
    distance = abs(prob - threshold)

    if word_count < 35 or distance < 0.06 or std_logit > 0.85:
        return "low"
    if word_count < 80 or distance < 0.13 or std_logit > 0.50:
        return "medium"
    return "high"


def overall_confidence(axis_levels: Dict[str, str]) -> str:
    min_rank = min(CONFIDENCE_RANK[level] for level in axis_levels.values())
    for level, rank in CONFIDENCE_RANK.items():
        if rank == min_rank:
            return level
    return "low"


def probs_to_type(final_probs: Dict[str, float]) -> str:
    letters = []
    for axis in ORDER:
        left, right = PAIRS[axis]
        letters.append(right if final_probs[axis] >= THRESHOLDS[axis] else left)
    return "".join(letters)


def selected_poles(final_probs: Dict[str, float]) -> Dict[str, str]:
    return {
        axis: PAIRS[axis][1] if final_probs[axis] >= THRESHOLDS[axis] else PAIRS[axis][0]
        for axis in ORDER
    }


def normalized_axis_distance(prob: float, threshold: float) -> float:
    if prob >= threshold:
        return (prob - threshold) / max(1e-6, 1 - threshold)
    return (threshold - prob) / max(1e-6, threshold)
