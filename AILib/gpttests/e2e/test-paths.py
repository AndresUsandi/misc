#!/usr/bin/env python3
import os
import sys
from _e2e import E2ETest

t = E2ETest("paths", "Data Path Overrides: directory and single file")
DATA = os.path.join("bin", "test-basic", "data")  # the override_data_folder targets of the options files, as the OS prints them


def main():
    t.clean()
    t.train("[1/4] Running Pre-training (override_data_folder = directory)...", "Training")
    t.train("[2/4] Running Fine-Tuning (override_data_folder = single file)...", "Fine-Tuning")
    t.train("[3/4] Running Optimizing (override_data_folder = directory)...", "Optimizing")
    t.infer("[4/4] Running Inference...")
    t.assert_log(f"Training Data Path: {os.path.join(DATA, 'Training')}",
                 f"Instruction Data: {os.path.join(DATA, 'Tuning', 'ch07_instruction', 'combined_1.txt')} (1 file(s))",
                 f"Preference Data: {os.path.join(DATA, 'Optimizing')} (1 file(s))")
    t.clean()


if __name__ == "__main__":
    sys.exit(t.run(main))
