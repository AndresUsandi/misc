#!/usr/bin/env python3
import sys
from _e2e import E2ETest

t = E2ETest("precision-fp32", "Full FP32, no AMP")


def main():
    t.clean()
    t.train("[1/4] Running Pre-training (fp32)...", "Training")
    t.train("[2/4] Running Fine-Tuning (fp32)...", "Fine-Tuning")
    t.train("[3/4] Running Optimizing (fp32)...", "Optimizing")
    t.infer("[4/4] Running Inference (fp32)...", "--precision", "fp32")
    t.assert_log("Precision: FP32 | Model Dtype: torch.float32 | AMP: Disabled", "TRAINING COMPLETED", "FINE-TUNING COMPLETED",
                 "[Step Limit Reached] Reached target step 5. Pausing DPO optimization cleanly.")
    t.clean()


if __name__ == "__main__":
    sys.exit(t.run(main))
