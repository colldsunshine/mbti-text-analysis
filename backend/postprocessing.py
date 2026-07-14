"""Rule-based lexical evidence and questionnaire-aware probability correction."""

import math
import re
from typing import Any, Dict, List, Optional, Tuple

from backend.config import ORDER, THRESHOLDS
from backend.lexicon_data import (
    AXES,
    BIG_MBTI_LEXICON,
    NEGATION_WORDS,
    QUESTION_AXIS_WEIGHTS,
    QUESTION_EVIDENCE_BLEND_BY_AXIS,
    QUESTION_EVIDENCE_MIN_SCORE,
    QUESTION_MARKERS,
)


LEXICON_LAMBDA_BY_AXIS = {"E": 1.00, "N": 1.10, "T": 0.30, "J": 1.15}
LEXICON_PHRASE_WEIGHT = 2.0
LEXICON_STEM_WEIGHT = 0.18
LEXICON_STEM_SCORE_CAP = 1.25
EVIDENCE_BOUNDARY = "__clause__"


def remove_mbti_markers(text: str) -> str:
    """Remove direct MBTI/typeology words so users cannot steer the classifier."""
    text = str(text)

    mbti_patterns = [
        r"\b(?:[EI][NS][TF][JP])\b",
        r"\b[EI]\s*[-_ ]?\s*[NS]\s*[-_ ]?\s*[TF]\s*[-_ ]?\s*[JP]\b",
        r"(мой|моя|у меня|я|тип|mbti|тип личности)\s*.{0,30}?(?:[EI][NS][TF][JP])",
    ]

    leak_patterns = [
        r"\bmbti\b",
        r"\b16\s*personalities\b",
        r"\bсоционик\w*\b",
        r"\bтиполог\w*\b",
        r"\bкогнитивн\w*\s+функци\w*\b",
        r"\bфункци[яи]\s+(fe|fi|te|ti|ne|ni|se|si)\b",
        r"\b(fe|fi|te|ti|ne|ni|se|si)\s*(доминирует|дом|aux|tert|inf|ведущая|вспомогательная)\b",
        r"\bинтроверт\w*\b",
        r"\bэкстраверт\w*\b",
        r"\bинтуит\w*\b",
        r"\bсенсорик\w*\b",
        r"\bлогик\w*\b",
        r"\bэтик\w*\b",
        r"\bрационал\w*\b",
        r"\bиррационал\w*\b",
    ]

    for pattern in mbti_patterns + leak_patterns:
        text = re.sub(pattern, " ", text, flags=re.IGNORECASE)

    return re.sub(r"\s+", " ", text).strip()


def normalize_text(text: str) -> str:
    text = str(text).lower().replace("ё", "е")
    text = re.sub(r"[^\w\s\-]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def normalize_evidence_text(text: str) -> str:
    """Normalize text without letting negation leak into another clause."""
    text = str(text).lower().replace("ё", "е")
    text = re.sub(r"[.!?;:\n]+", f" {EVIDENCE_BOUNDARY} ", text)
    text = re.sub(
        r"\b(?:но|однако|зато|хотя)\b",
        f" {EVIDENCE_BOUNDARY} ",
        text,
    )
    text = re.sub(r"[^\w\s\-]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def sigmoid(x: float) -> float:
    return 1 / (1 + math.exp(-x))


def prob_to_logit(prob: float) -> float:
    eps = 1e-6
    prob = min(max(float(prob), eps), 1 - eps)
    return math.log(prob / (1 - prob))


def has_negation_before_position(text: str, start: int, window: int = 4) -> bool:
    """Check negation by tokens within the current clause."""
    previous_tokens = text[:start].split()
    if EVIDENCE_BOUNDARY in previous_tokens:
        last_boundary = len(previous_tokens) - 1 - previous_tokens[::-1].index(EVIDENCE_BOUNDARY)
        previous_tokens = previous_tokens[last_boundary + 1:]
    previous_tokens = previous_tokens[-window:]
    return any(
        token in NEGATION_WORDS or token.startswith("ненавиж")
        for token in previous_tokens
    )


def pole_score(text: str, pole: str) -> float:
    data = BIG_MBTI_LEXICON[pole]
    phrase_score = 0.0
    phrase_spans = []

    for phrase in data["phrases"]:
        for match in re.finditer(rf"\b{re.escape(phrase)}\b", text):
            phrase_spans.append(match.span())
            phrase_score += (
                -LEXICON_PHRASE_WEIGHT
                if has_negation_before_position(text, match.start())
                else LEXICON_PHRASE_WEIGHT
            )

    stem_vote = 0.0
    seen_stem_spans = set()
    for stem in data["stems"]:
        for match in re.finditer(rf"\b\w*{re.escape(stem)}\w*\b", text):
            span = match.span()
            if span in seen_stem_spans:
                continue
            if any(start <= span[0] and span[1] <= end for start, end in phrase_spans):
                continue
            seen_stem_spans.add(span)
            stem_vote += -1.0 if has_negation_before_position(text, match.start()) else 1.0

    stem_score = max(
        -LEXICON_STEM_SCORE_CAP,
        min(LEXICON_STEM_SCORE_CAP, stem_vote * LEXICON_STEM_WEIGHT),
    )

    return phrase_score + stem_score


def axis_lexicon_score(text: str, positive_pole: str, negative_pole: str) -> float:
    pos = pole_score(text, positive_pole)
    neg = pole_score(text, negative_pole)
    total = abs(pos) + abs(neg)
    if total == 0:
        return 0.0
    return (pos - neg) / (total + 2.0)


def get_lexicon_scores(text: str) -> Dict[str, float]:
    normalized = normalize_evidence_text(text)
    scores = {}
    for axis, (positive, negative) in AXES.items():
        lexicon_score = axis_lexicon_score(normalized, positive, negative)
        marker_score, marker_hits = questionnaire_axis_signal(normalized, axis)

        if marker_hits:
            scores[axis] = 0.70 * marker_score + 0.30 * lexicon_score
        else:
            scores[axis] = lexicon_score
    return scores


def apply_lexicon_to_model_probs(model_probs: Dict[str, float], text: str) -> Dict[str, float]:
    """Apply a bounded lexical nudge after the neural model prediction."""
    lex_scores = get_lexicon_scores(text)
    final_probs = {}
    for axis in ORDER:
        model_logit = prob_to_logit(model_probs[axis])
        threshold_logit = prob_to_logit(THRESHOLDS[axis])
        model_distance = abs(model_logit - threshold_logit)
        uncertainty_gate = 0.35 + 0.65 * math.exp(-model_distance)
        final_logit = (
            model_logit
            + uncertainty_gate * LEXICON_LAMBDA_BY_AXIS[axis] * lex_scores[axis]
        )
        final_probs[axis] = sigmoid(final_logit)
    return final_probs


def marker_weight(text: str, markers: Tuple[Tuple[str, float], ...]) -> Tuple[float, float]:
    """Return direct and negated weights for precision questionnaire markers."""
    positive_weight = 0.0
    negated_weight = 0.0

    for pattern, weight in markers:
        for match in re.finditer(pattern, text):
            if has_negation_before_position(text, match.start(), window=3):
                negated_weight += weight
            else:
                positive_weight += weight

    return positive_weight, negated_weight


def questionnaire_axis_signal(text: str, axis: str) -> Tuple[float, float]:
    """Score one answer only against the axis explicitly asked in that question."""
    positive_pole, _ = AXES[axis]
    positive, positive_negated = marker_weight(text, QUESTION_MARKERS[positive_pole]["positive"])
    negative, negative_negated = marker_weight(text, QUESTION_MARKERS[positive_pole]["negative"])

    positive += negative_negated
    negative += positive_negated
    total = positive + negative
    if total == 0:
        return 0.0, 0.0

    return (positive - negative) / (total + 0.75), total


def collect_questionnaire_evidence(answers: List[str]) -> Dict[str, Dict[str, Any]]:
    """Aggregate direct, question-aware evidence without using free-form text."""
    weighted_scores = {axis: 0.0 for axis in ORDER}
    total_weights = {axis: 0.0 for axis in ORDER}
    total_hits = {axis: 0.0 for axis in ORDER}
    question_numbers = {axis: [] for axis in ORDER}

    for index, raw_answer in enumerate(answers[: len(QUESTION_AXIS_WEIGHTS)]):
        text = normalize_evidence_text(remove_mbti_markers(str(raw_answer)))
        if not text:
            continue

        for axis, question_weight in QUESTION_AXIS_WEIGHTS[index].items():
            score, hits = questionnaire_axis_signal(text, axis)
            if hits == 0:
                continue
            weighted_scores[axis] += question_weight * score
            total_weights[axis] += question_weight
            total_hits[axis] += hits
            question_numbers[axis].append(index + 1)

    evidence = {}
    for axis in ORDER:
        score = weighted_scores[axis] / total_weights[axis] if total_weights[axis] else 0.0
        evidence[axis] = {
            "score": float(score),
            "hits": float(total_hits[axis]),
            "questions": question_numbers[axis],
        }
    return evidence


def apply_questionnaire_evidence(
    final_probs: Dict[str, float],
    answers: Optional[List[str]],
) -> Tuple[Dict[str, float], Dict[str, Dict[str, Any]], Dict[str, str]]:
    """Let a clear answer to its own question resolve a model contradiction."""
    evidence = collect_questionnaire_evidence(answers or [])
    adjusted = dict(final_probs)
    adjustments = {}

    for axis in ORDER:
        score = evidence[axis]["score"]
        threshold = THRESHOLDS[axis]
        if abs(score) < QUESTION_EVIDENCE_MIN_SCORE:
            continue

        model_direction = 1 if adjusted[axis] >= threshold else -1
        evidence_direction = 1 if score > 0 else -1
        if model_direction == evidence_direction:
            continue

        evidence_logit = prob_to_logit(threshold) + score * 2.4
        model_logit = prob_to_logit(adjusted[axis])
        blend = QUESTION_EVIDENCE_BLEND_BY_AXIS[axis]
        adjusted[axis] = sigmoid(
            (1 - blend) * model_logit
            + blend * evidence_logit
        )

        if (adjusted[axis] >= threshold) == (evidence_direction > 0):
            adjustments[axis] = "direct_question_evidence"
        else:
            adjustments[axis] = "questionnaire_nudge"

    return adjusted, evidence, adjustments
