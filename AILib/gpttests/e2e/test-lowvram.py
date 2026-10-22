#!/usr/bin/env python3
import sys
from _e2e import E2ETest

t = E2ETest("lowvram", "Activation Checkpointing + Recompute LM Head + Freeze Embeddings + Chunk Size + Accumulation")


def main():
    t.clean()
    t.train("[1/4] Running Pre-training (activation checkpointing + recompute_lmhead, no compile)...", "Training")
    t.train("[2/4] Running Fine-Tuning (+ freeze_embeddings, chunk_size 128, batch 2 x accum 4, max_length 256)...", "Fine-Tuning")
    t.train("[3/4] Running Optimizing (+ freeze_embeddings, batch 1 x accum 4, max_length 256)...", "Optimizing")
    t.infer("[4/4] Running Inference...")
    t.assert_log("[Low-VRAM Optimization] Activation / Gradient Checkpointing enabled",
                 "[Low-VRAM Optimization] Token and position embeddings frozen (requires_grad = False).",
                 "[Gradient Accumulation] Accumulating gradients over 4 sub-steps before optimizer update.", "FINE-TUNING COMPLETED",
                 "[Step Limit Reached] Reached target step 5. Pausing DPO optimization cleanly.")
    t.clean()


if __name__ == "__main__":
    sys.exit(t.run(main))
