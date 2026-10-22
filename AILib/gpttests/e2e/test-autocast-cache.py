#!/usr/bin/env python3
import sys
from _e2e import E2ETest

t = E2ETest("autocast-cache", "--use_autocast_weight_cache: reserved VRAM drops, losses unchanged, --activation_checkpointing guard")


def main():
    t.clean()
    # Each stage runs twice from scratch, cache off then on. The pretraining batch is 4 x 512 tokens = 4 loss chunks of 512, the SFT batch
    # 4 x 256 tokens = 8 chunks of 128, so the cache frees 3 resp. 7 copies of the 25M model's 51 MB LM head: the epoch-end reserved figure
    # must drop by at least 0.05 resp. 0.15 GB (measured 0.10 and 0.29), while the logged losses stay within 0.02 resp. 0.05 (the only
    # numerical change is the head gradient accumulating in the autocast dtype, see the argument's help). The steps cache is deleted before
    # each second run so that both runs of a stage plan their steps (and with them the LR schedule) from the very same starting point.
    t.train("[1/6] Running Pre-training with the cache off (reference)...", "Training", "--resume", "false", "--use_autocast_weight_cache", "false")

    t.delete("steps_cache.json", "*.pth")
    t.train("[2/6] Running Pre-training again from scratch with the cache on...", "Training", "--resume", "false", "--use_autocast_weight_cache", "true")
    t.memcheck("gpu0", t.log, 1, 2, "reserved", 0.05)
    t.memcheck("losses", t.log, 1, 2, 0.02)

    t.train("[3/6] Running Fine-Tuning with the cache off (reference, full epoch)...", "Fine-Tuning", "--resume", "false", "--use_autocast_weight_cache", "false")

    t.delete("steps_cache.json")
    t.train("[4/6] Running Fine-Tuning again from scratch with the cache on...", "Fine-Tuning", "--resume", "false", "--use_autocast_weight_cache", "true")
    t.memcheck("gpu0", t.log, 3, 4, "reserved", 0.15)
    t.memcheck("losses", t.log, 3, 4, 0.05)

    t.train_rejected("[5/6] The cache together with --activation_checkpointing must be rejected at parse time (exit code 2)...",
                     "cannot be combined with --activation_checkpointing",
                     "--training_process", "Training", "--activation_checkpointing", "true", "--use_autocast_weight_cache", "true")

    t.infer("[6/6] Running Inference...")
    t.assert_log("[Low-VRAM Optimization] autocast weight cache enabled: the loss chunks share one low-precision copy of the LM head",
                 "TRAINING COMPLETED", "FINE-TUNING COMPLETED")
    t.clean()


if __name__ == "__main__":
    sys.exit(t.run(main))
