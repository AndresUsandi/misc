#!/usr/bin/env python3
import sys
from _e2e import E2ETest

t = E2ETest("vocab", "Unpadded 50,257 vocabulary vs. --vocab_padded, checkpoint vocab adaptation")


def main():
    t.clean()
    t.train("[1/5] Running Pre-training (--vocab_padded false: 50,257 vocab)...", "Training", "--vocab_padded", "false")
    t.train("[2/5] Running Fine-Tuning (default padding: 50,304 model loads the 50,257 checkpoint)...", "Fine-Tuning")
    t.train("[3/5] Running Optimizing (default padding)...", "Optimizing")
    t.train("[4/5] Running Pre-training again (--vocab_padded true: resumes the 50,257 checkpoint into a 50,304 model)...", "Training", "--vocab_padded", "true")
    t.infer("[5/5] Running Inference (50,257 model loads the exported weights)...")
    t.assert_log("Vocab: 50,257 | Context: 512", "Vocab: 50,304 | Context: 512", "TRAINING COMPLETED", "FINE-TUNING COMPLETED",
                 "[Resume Notice] Checkpoint has already completed 1 epochs")
    t.clean()


if __name__ == "__main__":
    sys.exit(t.run(main))
