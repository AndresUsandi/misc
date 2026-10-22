#!/usr/bin/env python3
import sys
from _e2e import E2ETest

t = E2ETest("dp-zero1-muon", "ZeRO-1 with the hybrid Muon + AdamW optimizers: two optimizers over parameter shards on different GPUs, pretraining and SFT, DPO, inference")


def main():
    t.require_gpus(2)
    t.clean()
    t.train("[1/4] Running Pre-training (ZeRO-1 + Muon)...", "Training")
    t.train("[2/4] Running Fine-Tuning (ZeRO-1 + Muon)...", "Fine-Tuning")
    t.train("[3/4] Running Optimizing (Muon, policy on GPU 0, reference on GPU 1)...", "Optimizing")
    t.infer("[4/4] Running Inference...")
    t.assert_log("Wrapping model in MultiGpuGptModelZeRO1 across 2 GPUs (Data Parallelism, optimizer sharded, compile=False, primary=cuda:1)",
                 "[Multi-GPU ZeRO-1] Optimizer state sharded across 2 GPUs", "Optimizers Configured: 2 ([CustomMuon (2D matrices), Fused AdamW (1D/Norms)])",
                 "Muon LR: 0.02", "[Optimizer] Selected Hybrid CustomMuon (2D weights) + Fused AdamW (1D/Norms/Embeddings).",
                 "TRAINING COMPLETED", "FINE-TUNING COMPLETED")
    t.clean()


if __name__ == "__main__":
    sys.exit(t.run(main))
