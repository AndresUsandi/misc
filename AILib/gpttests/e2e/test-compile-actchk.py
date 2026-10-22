#!/usr/bin/env python3
import sys
from _e2e import E2ETest

t = E2ETest("compile-actchk", "Compile + Act Checkpointing")


def main():
    t.clean()
    t.train("[1/4] Running Pre-training (Compile + Act Checkpointing)...", "Training")
    t.train("[2/4] Running Fine-Tuning (Compile + Act Checkpointing)...", "Fine-Tuning")
    t.train("[3/4] Running Optimizing (Compile + Act Checkpointing)...", "Optimizing")
    t.infer("[4/4] Running Inference...")
    t.assert_log("[Low-VRAM Optimization] Activation / Gradient Checkpointing enabled", "Applying torch.compile(model.forward_features)")
    t.clean()


if __name__ == "__main__":
    sys.exit(t.run(main))
