"""FastAPI entry point for the MBTI inference service."""

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.config import DEVICE, MODEL_NAME, WEIGHTS_PATH
from backend.inference import predict_text


class AnalyzeRequest(BaseModel):
    answers: List[str]
    free_text: Optional[str] = ""
    user_message: Optional[str] = ""


app = FastAPI(title="MBTI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> Dict[str, Any]:
    return {
        "ok": True,
        "device": str(DEVICE),
        "model": MODEL_NAME,
        "model_weights_found": WEIGHTS_PATH.is_file(),
    }


@app.post("/analyze")
def analyze(req: AnalyzeRequest) -> Dict[str, Any]:
    answers = [str(answer).strip() for answer in req.answers[:5]]
    parts = [answer for answer in answers if answer]

    if req.free_text and req.free_text.strip():
        parts.append(req.free_text.strip())

    if req.user_message and req.user_message.strip():
        parts.append(req.user_message.strip())

    text = "\n".join(parts).strip() or "Нет данных"
    try:
        return predict_text(text, questionnaire_answers=answers)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail="Model weights are not available yet") from exc
