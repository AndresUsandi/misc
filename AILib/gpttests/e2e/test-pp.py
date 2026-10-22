#!/usr/bin/env python3
import sys
from _e2e import E2ETest

t = E2ETest("pp", "Multi-GPU Pipeline Parallelism")


def main():
    t.require_gpus(2)
    t.clean()
    t.train("[1/4] Running Pre-training (PP: even layers, 1F1B, 4 micro-batches, async PCIe)...", "Training")
    t.train("[2/4] Running Fine-Tuning (PP: uneven layers)...", "Fine-Tuning")
    t.train("[3/4] Running Optimizing (Dual GPU Policy/Ref)...", "Optimizing")
    t.infer("[4/4] Running Inference...")
    t.assert_log("MultiGpuGptModelPP across 2 GPUs (Layers: even (50", "GPU 1), async_pcie=True, micro_batching=4 stages, 1f1b=True, primary=cuda:0)",
                 "MultiGpuGptModelPP across 2 GPUs (Layers: uneven (60", "GPU 1, default), primary=cuda:0)", "Policy Device: cuda:0 | Ref Device: cuda:1")
    t.clean()


if __name__ == "__main__":
    sys.exit(t.run(main))
