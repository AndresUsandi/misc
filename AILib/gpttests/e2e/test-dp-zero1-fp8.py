#!/usr/bin/env python3
import sys
from _e2e import E2ETest

t = E2ETest("dp-zero1-fp8", "Production fp8 path under ZeRO-1: sharded optimizer + torch.compile + FP8, mid-run resume restoring the shards, SFT, DPO with policy and reference on separate GPUs; falls back to fp16 below Compute 8.9")


def main():
    t.require_gpus(2)
    t.clean()
    t.train("[1/5] Running Pre-training (ZeRO-1 + compile + fp8, fresh, stops at step 3)...", "Training")
    t.train("[2/5] Running Pre-training again (ZeRO-1 + compile + fp8, resumes at step 3 with the sharded optimizer state, fast-forwards inside the epoch)...", "Training")
    t.train("[3/5] Running Fine-Tuning (ZeRO-1 + compile + fp8)...", "Fine-Tuning")
    t.train("[4/5] Running Optimizing (compile + fp8, policy on GPU 1, reference on GPU 0)...", "Optimizing")
    t.infer("[5/5] Running Inference (fp8)...", "--precision", "fp8")
    t.assert_log("Wrapping model in MultiGpuGptModelZeRO1 across 2 GPUs (Data Parallelism, optimizer sharded, compile=True, primary=cuda:0)",
                 "[Multi-GPU ZeRO-1] Optimizer state sharded across 2 GPUs", "Precision: FP8 | Model Dtype: torch.float32",
                 "[Resume] Successfully loaded active TRAIN checkpoint at Global Step 3",
                 "[Resume] Fast-forwarding 1 step(s) in Epoch 2 -> Resuming from step 2/2", "Saved TRAIN checkpoint (Step 4)", "TRAINING COMPLETED",
                 "[modelio] Successfully saved clean final model", "FINE-TUNING COMPLETED", "Policy Device: cuda:1 | Ref Device: cuda:0",
                 "[Step Limit Reached] Reached target step 5. Pausing DPO optimization cleanly.")
    t.clean()


if __name__ == "__main__":
    sys.exit(t.run(main))
