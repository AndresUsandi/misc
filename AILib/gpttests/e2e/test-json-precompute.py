#!/usr/bin/env python3
import shutil
import sys
from pathlib import Path
from _e2e import E2ETest

t = E2ETest("json-precompute", "DPO with precomputed reference log-probs, no reference model")
SOURCE = Path("bin", "test-basic", "data", "Optimizing", "ch07_preference", "preference_combined_1.json")
PREF = t.model_dir / "data" / "Optimizing" / "ch07_preference" / "preference_combined_1.json"


def main():
    t.clean()
    shutil.copyfile(SOURCE, PREF)
    try:
        t.train("[1/4] Running Pre-training...", "Training")
        t.train("[2/4] Running Fine-Tuning...", "Fine-Tuning")
        t.train("[3/4] Running Optimizing (json_precompute: annotates the dataset, then trains without a reference model)...", "Optimizing")
        if "ref_chosen_logprob" not in PREF.read_text(encoding="utf-8"):
            t.fail("Dataset was not annotated with reference log-probs")
    finally:
        shutil.copyfile(SOURCE, PREF)  # the pristine dataset comes back, also when a step failed
    t.infer("[4/4] Running Inference...")
    t.assert_log("Precomputed Mode: Active (No Ref Model)", "[Precompute Mode] Zero Reference Model VRAM enabled (--json_precompute).",
                 "PRECOMPUTING REFERENCE LOG-PROBABILITIES FOR DPO", "[Precompute] Initialized reference model from SFT checkpoint",
                 "[Precompute Complete] Successfully precomputed 1,100 pairs", "[Precomputed DPO Mode] Reference model bypassed entirely",
                 "[Step Limit Reached] Reached target step 5. Pausing Precomputed DPO optimization cleanly.")
    t.clean()


if __name__ == "__main__":
    sys.exit(t.run(main))
