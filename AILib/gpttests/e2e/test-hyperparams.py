#!/usr/bin/env python3
import sys
from _e2e import E2ETest

t = E2ETest("hyperparams", "Warmup, Min LR, Weight Decay, Eval Freq/Iter, Save Interval, Step Limit, Beta")


def main():
    t.clean()
    t.train("[1/4] Running Pre-training (Warmup Steps + Min LR + Weight Decay + Periodic Saves)...", "Training")
    t.train("[2/4] Running Fine-Tuning (Warmup Ratio + Min LR + Eval Iter + Periodic Saves)...", "Fine-Tuning")
    t.train("[3/4] Running Optimizing (Warmup Ratio + Min LR + Beta 0.2 + Periodic Saves)...", "Optimizing")
    t.infer("[4/4] Running Inference...")
    t.assert_log("Warmup Steps: 2", "[Checkpointing] Periodic saves enabled every 2 steps", "Saved TRAIN checkpoint (Step 2)",
                 "Saved TUNE checkpoint (Step 2)", "Saved TUNE checkpoint (Step 4)", "Beta: 0.2",
                 "Saved OPTIMIZE checkpoint (Step 2)", "Saved OPTIMIZE checkpoint (Step 4)")
    t.clean()


if __name__ == "__main__":
    sys.exit(t.run(main))
