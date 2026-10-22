#!/usr/bin/env python3
import sys
from _e2e import E2ETest

t = E2ETest("dp-zero1-switch", "Checkpoints are interchangeable between the data-parallel strategies: pretraining starts under ZeRO-1, resumes under plain Data Parallelism, resumes under ZeRO-1 again; SFT under ZeRO-1, inference")


def main():
    t.require_gpus(2)
    t.clean()
    t.train("[1/5] Running Pre-training (ZeRO-1, fresh, stops at step 3 of 8)...", "Training")
    t.train("[2/5] Running Pre-training again under plain Data Parallelism (resumes the ZeRO-1 checkpoint at step 3, stops at step 6)...", "Training", "--multi_gpu_strategy", "data-parallelism")
    t.train("[3/5] Running Pre-training again under ZeRO-1 (resumes the DP checkpoint at step 6, finishes the 4 epochs)...", "Training")
    t.train("[4/5] Running Fine-Tuning (ZeRO-1)...", "Fine-Tuning")
    t.infer("[5/5] Running Inference...")
    t.assert_log("Wrapping model in MultiGpuGptModelZeRO1 across 2 GPUs (Data Parallelism, optimizer sharded, compile=False, primary=cuda:1)",
                 "Wrapping model in MultiGpuGptModelDP across 2 GPUs (Data Parallelism, compile=False, primary=cuda:1)",
                 "[Resume] No existing checkpoint found for 'test-dp-zero1-switch' (TRAIN). Starting from scratch.",
                 "[Resume] Successfully loaded active TRAIN checkpoint at Global Step 3", "[Resume] Successfully loaded active TRAIN checkpoint at Global Step 6",
                 "Saved TRAIN checkpoint (Step 8)", "TRAINING COMPLETED", "FINE-TUNING COMPLETED")
    t.clean()


if __name__ == "__main__":
    sys.exit(t.run(main))
