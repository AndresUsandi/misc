#!/usr/bin/env python3
import sys
from _e2e import E2ETest

t = E2ETest("device", "Explicit --device / --gpu_index / --pol_device / --ref_device specs")


def main():
    t.clean()
    t.train('[1/4] Running Pre-training (device "cuda", gpu_index 0)...', "Training")
    t.train('[2/4] Running Fine-Tuning (device "cuda:0", gpu_index 0)...', "Fine-Tuning")
    t.train('[3/4] Running Optimizing (pol_device "cuda:0", ref_device "0")...', "Optimizing")
    t.infer("[4/4] Running Inference (device cuda:0)...", "--device", "cuda:0")
    t.assert_log("Device: cuda | Active GPUs: 1", "Device: cuda:0 | Active GPUs: 1", "Policy Device: cuda:0 | Ref Device: cuda:0",
                 "TRAINING COMPLETED", "FINE-TUNING COMPLETED")
    t.clean()


if __name__ == "__main__":
    sys.exit(t.run(main))
