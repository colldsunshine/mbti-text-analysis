from typing import Any, Dict, List, Optional

import numpy as np
import torch
from transformers import AutoTokenizer

from backend.config import DEVICE, MAX_LEN, MODEL_NAME, ORDER, STRIDE, THRESHOLDS, WEIGHTS_PATH
from backend.modeling import MBTI_BERT, chunk_text, load_state_dict_strict
from backend.portraits import build_gigachat_portrait, build_local_portrait
from backend.postprocessing import (
    apply_lexicon_to_model_probs,
    apply_questionnaire_evidence,
    get_lexicon_scores,
    remove_mbti_markers,
)
from backend.scoring import (
    axis_confidence,
    display_percent,
    overall_confidence,
    probs_to_type,
)


tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = MBTI_BERT(freeze_bert=True).to(DEVICE)
load_state_dict_strict(model, WEIGHTS_PATH)
model.eval()


@torch.no_grad()
def predict_text(text: str, questionnaire_answers: Optional[List[str]] = None) -> Dict[str, Any]:
    text_clean = remove_mbti_markers(text)
    if not text_clean:
        text_clean = "Нет данных"

    text_prepared = "[FREE_TEXT] " + text_clean
    chunks = chunk_text(text_prepared, tokenizer, MAX_LEN, STRIDE)

    enc = tokenizer(
        chunks,
        max_length=MAX_LEN,
        padding="max_length",
        truncation=True,
        return_tensors="pt",
    )
    logits = model(enc["input_ids"].to(DEVICE), enc["attention_mask"].to(DEVICE))
    chunk_logits = logits.detach().cpu().numpy()

    mean_logits = chunk_logits.mean(axis=0)
    std_logits = chunk_logits.std(axis=0)
    probs = 1 / (1 + np.exp(-mean_logits))

    model_probs = {axis: float(probs[i]) for i, axis in enumerate(ORDER)}
    lexicon_probs = apply_lexicon_to_model_probs(model_probs, text_clean)
    lexicon_scores = get_lexicon_scores(text_clean)
    lexicon_adjustments = {
        axis: "lexicon_flip"
        for axis in ORDER
        if (model_probs[axis] >= THRESHOLDS[axis])
        != (lexicon_probs[axis] >= THRESHOLDS[axis])
    }
    final_probs = lexicon_probs
    final_probs, questionnaire_evidence, questionnaire_adjustments = apply_questionnaire_evidence(
        final_probs,
        questionnaire_answers,
    )

    word_count = len(text_clean.split())
    axis_levels = {
        axis: axis_confidence(final_probs[axis], THRESHOLDS[axis], float(std_logits[i]), word_count)
        for i, axis in enumerate(ORDER)
    }
    for axis, adjustment in questionnaire_adjustments.items():
        if adjustment == "direct_question_evidence" and axis_levels[axis] == "high":
            axis_levels[axis] = "medium"
    for axis in lexicon_adjustments:
        if axis_levels[axis] == "high":
            axis_levels[axis] = "medium"

    mbti_type = probs_to_type(final_probs)
    percent = {
        axis: display_percent(final_probs[axis], THRESHOLDS[axis], axis_levels[axis])
        for axis in ORDER
    }

    local_portrait = build_local_portrait(mbti_type, final_probs)
    confidence = overall_confidence(axis_levels)
    gigachat_portrait = build_gigachat_portrait(mbti_type, percent, confidence, axis_levels)
    portrait = gigachat_portrait or local_portrait

    return {
        "mbti_type": mbti_type,
        "percent": percent,
        "portrait": portrait,
        "portrait_source": "gigachat" if gigachat_portrait else "local",
        "confidence": confidence,
        "axis_confidence": axis_levels,
        "n_chunks": len(chunks),
        "debug": {
            "model_probs": {axis: round(model_probs[axis], 4) for axis in ORDER},
            "lexicon_probs": {axis: round(lexicon_probs[axis], 4) for axis in ORDER},
            "final_probs": {axis: round(final_probs[axis], 4) for axis in ORDER},
            "lexicon_scores": {axis: round(lexicon_scores[axis], 4) for axis in ORDER},
            "lexicon_adjustments": lexicon_adjustments,
            "questionnaire_evidence": {
                axis: {
                    "score": round(details["score"], 4),
                    "hits": round(details["hits"], 2),
                    "questions": details["questions"],
                }
                for axis, details in questionnaire_evidence.items()
            },
            "questionnaire_adjustments": questionnaire_adjustments,
            "logit_std": {axis: round(float(std_logits[i]), 4) for i, axis in enumerate(ORDER)},
            "word_count": word_count,
        },
    }
