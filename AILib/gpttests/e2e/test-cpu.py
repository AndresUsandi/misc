#!/usr/bin/env python3
import sys
from _e2e import E2ETest

t = E2ETest("cpu", "--device cpu on a tiny model, Muon on CPU / Muon CUDA fallback")


def main():
    t.clean()
    t.train("[1/4] Running Pre-training (cpu, Muon)...", "Training")
    t.train("[2/4] Running Fine-Tuning (cpu, Muon requested, falls back to AdamW)...", "Fine-Tuning")
    t.train("[3/4] Running Optimizing (cpu, policy and reference on cpu)...", "Optimizing")
    t.infer("[4/4] Running Inference (cpu)...", "--device", "cpu")
    t.assert_log("Device: cpu | Active GPUs: 1 | Precision: FP16 | Model Dtype: torch.float32 | AMP: Disabled",
                 "Optimizers Configured: 2 ([CustomMuon (2D matrices), Fused AdamW (1D/Norms)])",
                 "[Optimizer Warning] CustomMuon requires CUDA; falling back to AdamW.", "Policy Device: cpu | Ref Device: cpu", "TRAINING COMPLETED")
    t.clean()


if __name__ == "__main__":
    sys.exit(t.run(main))
