#!/usr/bin/env python3
import sys
from _e2e import E2ETest

t = E2ETest("precision-fp8", "FP8 + compile + coordinate descent tuning; falls back to fp16 below Compute 8.9")


def main():
    t.clean()
    t.train("[1/4] Running Pre-training (fp8 + compile + coordinate_descent_tuning)...", "Training")
    t.train("[2/4] Running Fine-Tuning (fp8 + compile)...", "Fine-Tuning")
    t.train("[3/4] Running Optimizing (fp8 + compile)...", "Optimizing")
    t.infer("[4/4] Running Inference (fp8)...", "--precision", "fp8")
    t.assert_log("Precision: FP8 | Model Dtype:", "TRAINING COMPLETED", "FINE-TUNING COMPLETED",
                 "[Step Limit Reached] Reached target step 5. Pausing DPO optimization cleanly.")
    t.clean()


if __name__ == "__main__":
    sys.exit(t.run(main))
