#!/usr/bin/env python3
import sys
from _e2e import E2ETest

t = E2ETest("epochs", "Full epoch completion without step limit, completed-epochs notice")


def main():
    t.clean()
    t.train("[1/6] Running Pre-training (2 full epochs, final .pth export)...", "Training")
    t.train("[2/6] Running Pre-training again (checkpoint already completed the requested epochs)...", "Training")
    t.train("[3/6] Running Fine-Tuning (2 full epochs)...", "Fine-Tuning")
    t.train("[4/6] Running Fine-Tuning again (checkpoint already completed the requested epochs)...", "Fine-Tuning")
    t.train("[5/6] Running Optimizing (1 full epoch)...", "Optimizing")
    t.infer("[6/6] Running Inference...")
    t.assert_log("Starting Epoch 2/2", "[Resume Notice] Checkpoint has already completed 2 epochs", "Starting Fine-Tuning Epoch 2/2",
                 "[Sample Response @ Epoch 2]", "[Plot] Saved fine-tuning loss curves", "[Sample Model Response @ Epoch 1]",
                 "[Plot] Saved DPO telemetry curves")
    for ext in ("chk.trn", "chk.sft", "chk.dpo", "pth"):
        if not (t.model_dir / f"{t.model}.{ext}").exists():
            t.fail(f"Missing expected output {t.model}.{ext}")
    t.clean()


if __name__ == "__main__":
    sys.exit(t.run(main))
