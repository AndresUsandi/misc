#!/usr/bin/env python3
import sys
from _e2e import E2ETest

t = E2ETest("muon", "Muon Optimizer")


def main():
    t.clean()
    t.train("[1/4] Running Pre-training (Muon)...", "Training")
    t.train("[2/4] Running Fine-Tuning (Muon)...", "Fine-Tuning")
    t.train("[3/4] Running Optimizing (Muon)...", "Optimizing")
    t.infer("[4/4] Running Inference...")
    t.assert_log("Optimizers Configured: 2 ([CustomMuon (2D matrices), Fused AdamW (1D/Norms)])", "Muon LR: 0.02",
                 "[Optimizer] Selected Hybrid CustomMuon (2D weights) + Fused AdamW (1D/Norms/Embeddings).")
    t.clean()


if __name__ == "__main__":
    sys.exit(t.run(main))
