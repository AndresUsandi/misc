#!/usr/bin/env python3
import sys
from _e2e import E2ETest

t = E2ETest("dp", "Multi-GPU Data Parallelism")


def main():
    t.require_gpus(2)
    t.clean()
    t.train("[1/4] Running Pre-training (DP, primary GPU 1)...", "Training")
    t.train("[2/4] Running Fine-Tuning (DP, primary GPU 0)...", "Fine-Tuning")
    t.train("[3/4] Running Optimizing (auto reference device on GPU 1)...", "Optimizing")
    t.infer("[4/4] Running Inference...")
    t.assert_log("Wrapping model in MultiGpuGptModelDP across 2 GPUs (Data Parallelism, compile=False, primary=cuda:1)",
                 "Wrapping model in MultiGpuGptModelDP across 2 GPUs (Data Parallelism, compile=False, primary=cuda:0)",
                 "Policy Device: cuda:0 | Ref Device: cuda:1")
    t.clean()


if __name__ == "__main__":
    sys.exit(t.run(main))
