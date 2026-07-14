import os
from pathlib import Path

import torch


DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
MODEL_NAME = "cointegrated/rubert-tiny2"
WEIGHTS_PATH = Path(__file__).resolve().with_name("mbti_stage2_chunked.bin")
GIGACHAT_AUTH_TOKEN = os.getenv("GIGACHAT_AUTH_TOKEN", "").strip()

MAX_LEN = 512
STRIDE = 128

THRESHOLDS = {"E": 0.63, "N": 0.41, "T": 0.53, "J": 0.49}
ORDER = ["E", "N", "T", "J"]
PAIRS = {"E": ("I", "E"), "N": ("S", "N"), "T": ("F", "T"), "J": ("P", "J")}
