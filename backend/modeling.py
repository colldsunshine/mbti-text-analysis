"""Neural MBTI model architecture, weight loading, and token chunking."""

from pathlib import Path
from typing import List

import torch
import torch.nn as nn
from transformers import AutoModel, AutoTokenizer

from backend.config import DEVICE, MAX_LEN, MODEL_NAME, STRIDE


class MBTI_BERT(nn.Module):
    def __init__(self, freeze_bert: bool = False):
        super().__init__()
        self.freeze_bert = freeze_bert
        self.bert = AutoModel.from_pretrained(MODEL_NAME)

        for param in self.bert.parameters():
            param.requires_grad = not freeze_bert

        self.bert_hidden = self.bert.config.hidden_size * 2
        self.drop = nn.Dropout(p=0.1)

        self.adapter_mbti = nn.Sequential(
            nn.Linear(self.bert_hidden, 256),
            nn.GELU(),
            nn.Dropout(0.1),
            nn.Linear(256, self.bert_hidden),
            nn.LayerNorm(self.bert_hidden),
        )

        def make_head() -> nn.Sequential:
            return nn.Sequential(
                nn.Linear(self.bert_hidden, self.bert_hidden // 2),
                nn.GELU(),
                nn.Dropout(0.1),
                nn.Linear(self.bert_hidden // 2, 1),
            )

        self.mbti_E = make_head()
        self.mbti_N = make_head()
        self.mbti_T = make_head()
        self.mbti_J = make_head()

    def forward(self, input_ids: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
        ctx = torch.no_grad() if self.freeze_bert else torch.enable_grad()
        with ctx:
            outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
            hidden_state = outputs.last_hidden_state

        input_mask_expanded = attention_mask.unsqueeze(-1).expand(hidden_state.size()).float()
        sum_embeddings = torch.sum(hidden_state * input_mask_expanded, 1)
        sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)
        mean_pool = sum_embeddings / sum_mask

        hidden_state_masked = hidden_state.clone()
        hidden_state_masked[input_mask_expanded == 0] = -1e9
        max_pool = torch.max(hidden_state_masked, 1)[0]

        x = self.drop(torch.cat((mean_pool, max_pool), dim=1))
        feat = x + self.adapter_mbti(x)

        return torch.cat(
            [self.mbti_E(feat), self.mbti_N(feat), self.mbti_T(feat), self.mbti_J(feat)],
            dim=1,
        )


def load_state_dict_strict(model: nn.Module, path: Path) -> None:
    sd = torch.load(path, map_location=DEVICE)
    if isinstance(sd, dict) and "state_dict" in sd:
        sd = sd["state_dict"]
    if any(k.startswith("module.") for k in sd.keys()):
        sd = {k.replace("module.", ""): v for k, v in sd.items()}
    model.load_state_dict(sd, strict=True)



def chunk_text(text: str, tokenizer: AutoTokenizer, max_len: int = MAX_LEN, stride: int = STRIDE) -> List[str]:
    if not isinstance(text, str) or not text.strip():
        return [""]

    tokens = tokenizer.encode(text, add_special_tokens=False)
    chunks = []
    start = 0

    while start < len(tokens):
        end = start + max_len - 2
        chunk_tokens = tokens[start:end]
        chunks.append(tokenizer.decode(chunk_tokens, skip_special_tokens=True))
        if end >= len(tokens):
            break
        start += max_len - stride

    return chunks or [text]

