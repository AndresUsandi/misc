#!/usr/bin/env python3
import sys
from _e2e import E2ETest

t = E2ETest("resume", "Mid-run checkpoint resume for every stage, Muon optimizer state restore")


def main():
    t.clean()
    t.train("[1/7] Running Pre-training (fresh, stops at step 3 mid-file)...", "Training")
    t.train("[2/7] Running Pre-training again (resumes at step 3, fast-forwards inside the file)...", "Training")
    t.train("[3/7] Running Fine-Tuning (fresh, stops at step 3)...", "Fine-Tuning")
    t.train("[4/7] Running Fine-Tuning again (resumes at step 3)...", "Fine-Tuning")
    t.train("[5/7] Running Optimizing (fresh, stops at step 3)...", "Optimizing")
    t.train("[6/7] Running Optimizing again (resumes at step 3)...", "Optimizing")
    t.infer("[7/7] Running Inference...")
    t.assert_log("[Resume] No existing checkpoint found for 'test-resume' (TRAIN). Starting from scratch.",
                 "[Resume] Successfully loaded active TRAIN checkpoint at Global Step 3",
                 "[Training Plan] Resumed from step 3. Training for 3 steps -> Target step: 6.",
                 "[Resume] Fast-forwarding 3 step(s) in Epoch 1 -> Resuming from step 4/", "Saved TRAIN checkpoint (Step 6)",
                 "[Resume] Successfully loaded active TUNE checkpoint at Global Step 3", "[Resume] Fast-forwarding 3 step(s) in Epoch 1",
                 "Saved TUNE checkpoint (Step 6)", "[Resume] Successfully loaded active OPTIMIZE checkpoint at Global Step 3",
                 "[DPO Plan] Resumed from step 3. Training for 3 steps -> Target step: 6.", "Saved OPTIMIZE checkpoint (Step 6)")
    t.clean()


if __name__ == "__main__":
    sys.exit(t.run(main))
