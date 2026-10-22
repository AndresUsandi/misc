# Copyright (c) Sebastian Raschka under Apache License 2.0 (see LICENSE.txt).
# Tier B content verifier: sentence-level NLI (entailment / contradiction) of a response against reference facts.

import re
from typing import List, Tuple

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from gpttests.data.modelrefs import NLI_MODEL_ID

CONTRADICTION_THRESHOLD = 0.8   # a sentence contradicting any fact above this probability is reported as a contradiction
ENTAILMENT_THRESHOLD = 0.5      # a sentence no fact entails above this probability counts as unsupported (warning)


class NliVerifier:
    """Loads the DeBERTa-v3 MNLI/FEVER/ANLI cross-encoder once; check() scores every response sentence against every fact."""

    def __init__(self, device: torch.device):
        self.device = device
        self.tokenizer = AutoTokenizer.from_pretrained(NLI_MODEL_ID)
        self.model = AutoModelForSequenceClassification.from_pretrained(NLI_MODEL_ID).to(device).eval()
        if device.type == "cuda":
            self.model.half()
        labels = {v.lower(): k for k, v in self.model.config.id2label.items()}
        self.entail_idx, self.contra_idx = labels["entailment"], labels["contradiction"]

    def check(self, facts: List[str], response: str) -> Tuple[List[str], List[str]]:
        """Returns (contradicted_sentences, unsupported_sentences) with the offending fact / probability inlined."""
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n+", response.strip()) if len(s.strip()) > 15]
        if not facts or not sentences:
            return [], []
        premises = [f for f in facts for _ in sentences]
        hypotheses = [s for _ in facts for s in sentences]
        enc = self.tokenizer(premises, hypotheses, return_tensors="pt", padding=True, truncation=True, max_length=512).to(self.device)
        with torch.no_grad():
            probs = torch.softmax(self.model(**enc).logits.float(), dim=-1).view(len(facts), len(sentences), -1)
        contra = probs[:, :, self.contra_idx].max(dim=0)
        entail = probs[:, :, self.entail_idx].max(dim=0)
        contradicted, unsupported = [], []
        for i, sent in enumerate(sentences):
            if contra.values[i] >= CONTRADICTION_THRESHOLD:
                contradicted.append(f"'{sent}' contradicts '{facts[contra.indices[i]]}' (p={contra.values[i]:.2f})")
            elif entail.values[i] < ENTAILMENT_THRESHOLD:
                unsupported.append(f"'{sent}' (max entailment p={entail.values[i]:.2f})")
        return contradicted, unsupported
