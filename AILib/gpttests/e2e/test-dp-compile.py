#!/usr/bin/env python3
import sys
from _e2e import E2ETest

t = E2ETest("dp-compile", "Production path: Data Parallelism + torch.compile, mid-run resume under DP, DPO with policy and reference on separate GPUs")


def main():
    t.require_gpus(2)
    t.clean()
    t.train("[1/5] Running Pre-training (DP + compile, fresh, stops at step 3)...", "Training")
    t.train("[2/5] Running Pre-training again (DP + compile, resumes at step 3, fast-forwards inside the epoch)...", "Training")
    t.train("[3/5] Running Fine-Tuning (DP + compile)...", "Fine-Tuning")
    t.train("[4/5] Running Optimizing (compile, policy on GPU 1, reference on GPU 0)...", "Optimizing")
    t.infer("[5/5] Running Inference...")
    t.assert_log("Wrapping model in MultiGpuGptModelDP across 2 GPUs (Data Parallelism, compile=True, primary=cuda:0)",
                 "Model Dtype: torch.float32 | AMP: Enabled", "[Resume] Successfully loaded active TRAIN checkpoint at Global Step 3",
                 "[Resume] Fast-forwarding 1 step(s) in Epoch 2 -> Resuming from step 2/2", "Saved TRAIN checkpoint (Step 4)", "TRAINING COMPLETED",
                 "[modelio] Successfully saved clean final model", "FINE-TUNING COMPLETED", "Policy Device: cuda:1 | Ref Device: cuda:0",
                 "[Step Limit Reached] Reached target step 5. Pausing DPO optimization cleanly.")
    t.clean()


if __name__ == "__main__":
    sys.exit(t.run(main))
