#!/usr/bin/env python3
import sys
from _e2e import E2ETest

t = E2ETest("stage-order", "Allowed weight sources per stage: .chk.trn / .chk.sft / .pth, with and without --resume")


def main():
    t.clean()
    t.train("[1/12] Pre-training from scratch (completes 1 epoch: .chk.trn + exported .pth)...", "Training")
    t.train("[2/12] Fine-Tuning on the pre-training checkpoint (.chk.trn)...", "Fine-Tuning")
    t.train("[3/12] Fine-Tuning with --resume false on the pre-training checkpoint (.chk.trn)...", "Fine-Tuning", "--resume", "false")
    t.train("[4/12] Optimizing with --resume false on the SFT checkpoint (.chk.sft)...", "Optimizing", "--resume", "false")

    t.delete("*.chk.sft*", "*.chk.dpo*")
    t.train("[5/12] Optimizing directly on the pre-training checkpoint (.chk.trn, no SFT)...", "Optimizing")

    t.delete("*.chk*")
    t.train("[6/12] Fine-Tuning on the exported model only (.pth)...", "Fine-Tuning")
    t.delete("*.chk*")
    t.train("[7/12] Optimizing on the exported model only (.pth, reference model also from .pth)...", "Optimizing")
    t.delete("*.chk*")
    t.train("[8/12] Fine-Tuning with --resume false on the exported model only (.pth)...", "Fine-Tuning", "--resume", "false")
    t.delete("*.chk*")
    t.train("[9/12] Optimizing with --resume false on the exported model only (.pth)...", "Optimizing", "--resume", "false")

    t.delete("*.pth")
    t.train("[10/12] Pre-training again with only .chk.dpo present (must start from scratch, never from SFT/DPO weights)...", "Training")
    t.train("[11/12] Fine-Tuning with .chk.trn + .chk.dpo present (must take the pre-training checkpoint)...", "Fine-Tuning")
    t.infer("[12/12] Running Inference...")

    if "weights for TRAIN. Starting TRAIN from Step 0." in t.log_text():
        t.fail("Pre-training loaded SFT/DPO checkpoint weights")
    t.assert_log("[Resume] No existing checkpoint found for 'test-stage-order' (TRAIN). Starting from scratch.",
                 "[modelio] Successfully saved clean final model", "[Resume] Loaded base pre-trained weights for TUNE. Starting TUNE from Step 0.",
                 "[Fine-Tuning] Resume disabled. Initialized model from base pre-trained checkpoint (.chk.trn). Starting Fine-Tuning from Step 0.",
                 "[Policy Model] Resume disabled. Initialized policy weights from base SFT checkpoint (.chk.sft).",
                 "[Reference Model] Initialized frozen reference model from SFT checkpoint (.chk.sft)",
                 "[Reference Model] Initialized frozen reference model from pre-training checkpoint (.chk.trn)",
                 "[Resume] Loaded base pre-trained weights for OPTIMIZE. Starting OPTIMIZE from Step 0.",
                 "[Resume] No active SFT checkpoint found for 'test-stage-order'. Loaded base model weights (.pth). Starting Fine-Tuning from Step 0.",
                 "[Reference Model] No SFT/pre-training checkpoint found; initialized frozen reference model from base model weights (.pth)",
                 "[Resume] Loaded base model weights (.pth) for policy model. Starting DPO from Step 0.",
                 "[Fine-Tuning] Resume disabled. Initialized model from base model weights (.pth). Starting Fine-Tuning from Step 0.",
                 "[Policy Model] Resume disabled. Initialized policy weights from base model (.pth).")
    scratch_runs = t.log_text().count("(TRAIN). Starting from scratch.")
    if scratch_runs != 2:
        t.fail(f"Expected 2 from-scratch pre-training runs, found {scratch_runs}")
    t.clean()


if __name__ == "__main__":
    sys.exit(t.run(main))
