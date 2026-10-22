#!/usr/bin/env python3
import sys
from _e2e import E2ETest

t = E2ETest("tokenizer-qwen", "per-model tokenizer: Qwen2.5 tokenizer.json, 151,665 tokens, vocab_size 151,936")
FETCH_TOKENIZER = ("import json, sys; sys.path.insert(0, '.'); from argsutil import ModelArgs; from gptinfer.inference import get_tokenizer; "
                   f"get_tokenizer(json.load(open('{t.model_dir.as_posix()}/{t.model}.model-params.json')), ModelArgs(model_name='{t.model}'))")


def main():
    t.clean("tokenizer.json")
    t.step("[0/4] Fetching the tokenizer declared in model-params.json (first run only, kept across runs)...", "-c", FETCH_TOKENIZER, quiet=True)
    t.train("[1/4] Running Pre-training...", "Training")
    t.train("[2/4] Running Fine-Tuning...", "Fine-Tuning")
    t.train("[3/4] Running Optimizing (DPO)...", "Optimizing")
    t.infer("[4/4] Running Inference...")
    t.assert_log("[Tokenizer] Loaded tokenizer.json (151,665 tokens, <|endoftext|>=151643, model vocab_size=151,936).", "Vocab: 151,936",
                 "TRAINING COMPLETED", "FINE-TUNING COMPLETED", "DPO OPTIMIZATION COMPLETED",
                 f"[modelio] Successfully loaded model weights from: {t.model_dir / f'{t.model}.pth'}")
    t.clean("tokenizer.json")


if __name__ == "__main__":
    sys.exit(t.run(main))
