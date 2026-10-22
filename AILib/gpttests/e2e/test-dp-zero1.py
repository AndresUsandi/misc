#!/usr/bin/env python3
import sys
from _e2e import E2ETest

t = E2ETest("dp-zero1", "Multi-GPU Data Parallelism with the optimizer sharded across GPUs: ZeRO-1 pretraining and SFT, DPO, inference")


def main():
    t.require_gpus(2)
    t.clean()
    t.train("[1/4] Running Pre-training (ZeRO-1, primary GPU 1)...", "Training")
    t.train("[2/4] Running Fine-Tuning (ZeRO-1)...", "Fine-Tuning")
    t.train("[3/4] Running Optimizing (policy on GPU 0, reference on GPU 1)...", "Optimizing")
    t.infer("[4/4] Running Inference...")
    t.assert_log("Wrapping model in MultiGpuGptModelZeRO1 across 2 GPUs (Data Parallelism, optimizer sharded, compile=False, primary=cuda:1)",
                 "Wrapping model in MultiGpuGptModelZeRO1 across 2 GPUs (Data Parallelism, optimizer sharded, compile=False, primary=cuda:0)",
                 "[Multi-GPU ZeRO-1] Optimizer state sharded across 2 GPUs", "TRAINING COMPLETED", "FINE-TUNING COMPLETED",
                 "Policy Device: cuda:0 | Ref Device: cuda:1")
    t.clean()


if __name__ == "__main__":
    sys.exit(t.run(main))
