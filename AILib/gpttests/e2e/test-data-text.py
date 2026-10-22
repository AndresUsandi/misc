#!/usr/bin/env python3
import sys
from _e2e import E2ETest

t = E2ETest("data-text", "Data Ratios, Max Length, Chunk Size, Mask Prompt, Sampling, Verbose")


def main():
    t.clean()
    t.train("[1/4] Running Pre-training (Chunk Size + Ratios + Sampling Temperature/Top-K + Save Timeout)...", "Training")
    t.train("[2/4] Running Fine-Tuning (Mask Prompt off + Max Length 256 + Chunk Size 128 + Ratios + Verbose)...", "Fine-Tuning")
    t.train("[3/4] Running Optimizing (Beta 0.2 + Max Length clamped from 1024 + Ratios + Verbose + Resume off)...", "Optimizing")
    t.infer("[4/4] Running Inference (Sampling Temp/Top-K/Top-P + ChatML)...")
    t.assert_log("Sample: Every effort moves you", "[Sample]:",
                 "[Policy Model] Resume disabled. Initialized policy weights from base SFT checkpoint (.chk.sft).", "[Sample Response]:")
    t.clean()


if __name__ == "__main__":
    sys.exit(t.run(main))
