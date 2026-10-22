#!/usr/bin/env python3
import sys
from _e2e import E2ETest

t = E2ETest("basic", "Basic Baseline, single GPU")


def main():
    t.clean()
    t.train("[1/4] Running Pre-training...", "Training")
    t.train("[2/4] Running Fine-Tuning...", "Fine-Tuning")
    t.train("[3/4] Running Optimizing (DPO, policy and reference on one GPU)...", "Optimizing")
    t.infer("[4/4] Running Inference...")
    t.assert_log("Optimizer Configured: 1 ([Single Fused AdamW for all layers, default])", "TRAINING COMPLETED",
                 "[modelio] Successfully saved clean final model", "[Resume] Loaded base pre-trained weights for TUNE. Starting TUNE from Step 0.",
                 "FINE-TUNING COMPLETED", "Policy Device: cuda:0 | Ref Device: cuda:0",
                 "[Reference Model] Initialized frozen reference model from SFT checkpoint",
                 "[Resume] Loaded base SFT weights for OPTIMIZE. Starting OPTIMIZE from Step 0.",
                 "[Step Limit Reached] Reached target step 5. Pausing DPO optimization cleanly.")
    t.clean()


if __name__ == "__main__":
    sys.exit(t.run(main))
