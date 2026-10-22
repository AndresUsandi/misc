#!/usr/bin/env python3
import sys
from _e2e import E2ETest

t = E2ETest("multifile", "Two dataset files per stage, precompute_total_steps, test_mode")


def main():
    t.clean()
    t.train("[1/4] Running Pre-training (2 text files, precompute_total_steps, train_ratio 0.8)...", "Training")
    t.train("[2/4] Running Fine-Tuning (2 instruction files)...", "Fine-Tuning")
    t.train("[3/4] Running Optimizing (2 preference files, test_mode truncates to 1)...", "Optimizing")
    t.infer("[4/4] Running Inference...")
    t.assert_log("Total training files found: 2", "[Precompute] Verifying/calculating exact tokens across 2 dataset file(s)", "[Data] 2 file(s):",
                 "Val by dataset: TheVeredict", "(2 file(s))", "SFT validation buffer", "across 2 file(s).",
                 "[Test Mode] Truncated dataset to 1 file (preference_combined_1.json).")
    t.clean()


if __name__ == "__main__":
    sys.exit(t.run(main))
