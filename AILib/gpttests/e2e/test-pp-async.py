#!/usr/bin/env python3
import sys
from _e2e import E2ETest

t = E2ETest("pp-async", "Pipeline Parallelism: uneven split, async PCIe, no micro-batching / 1F1B")


def main():
    t.require_gpus(2)
    t.clean()
    t.train("[1/4] Running Pre-training (PP: uneven layers, micro-batching disabled, async PCIe, primary GPU 1)...", "Training")
    t.train("[2/4] Running Fine-Tuning (PP: even layers, primary GPU 1)...", "Fine-Tuning")
    t.train("[3/4] Running Optimizing (policy on cuda:1, reference on cuda:0)...", "Optimizing")
    t.infer("[4/4] Running Inference...")
    t.assert_log("MultiGpuGptModelPP across 2 GPUs (Layers: uneven (60", "GPU 1, default), async_pcie=True, micro_batching=disabled, 1f1b=False, primary=cuda:1)",
                 "MultiGpuGptModelPP across 2 GPUs (Layers: even (50", "GPU 1), primary=cuda:1)", "Policy Device: cuda:1 | Ref Device: cuda:0")
    t.clean()


if __name__ == "__main__":
    sys.exit(t.run(main))
