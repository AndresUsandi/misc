#!/usr/bin/env python3
import shutil
import sys
import tempfile
from pathlib import Path
from _e2e import E2ETest

t = E2ETest("basedir", "--models_base_dir pointing outside bin/")
BASE = Path(tempfile.gettempdir()) / "ailib-e2e-basedir"


def main():
    t.clean()
    shutil.rmtree(BASE, ignore_errors=True)
    shutil.copytree(t.model_dir, BASE / t.model)
    t.train(f"[1/3] Running Pre-training (models_base_dir={BASE})...", "Training", "--models_base_dir", str(BASE))
    t.train(f"[2/3] Running Fine-Tuning (models_base_dir={BASE})...", "Fine-Tuning", "--models_base_dir", str(BASE))
    t.train(f"[3/3] Running Optimizing (models_base_dir={BASE})...", "Optimizing", "--models_base_dir", str(BASE))

    for ext in ("chk.trn", "chk.sft", "chk.dpo", "pth"):
        if not (BASE / t.model / f"{t.model}.{ext}").exists():
            t.fail(f"Missing {t.model}.{ext} under {BASE}")
    if not (BASE / t.model / "steps_cache.json").exists():
        t.fail(f"steps_cache.json not written under {BASE}")
    leaked = [f.name for pattern in ("*.chk*", "*.pth", "log.txt") for f in t.model_dir.glob(pattern)]
    if leaked:
        t.fail(f"Outputs leaked into the default {t.model_dir} folder: {', '.join(leaked)}")
    t.assert_log(f"Saved TRAIN checkpoint (Step 2) to: {BASE / t.model / f'{t.model}.chk.trn'}",
                 "[Resume] Loaded base pre-trained weights for TUNE. Starting TUNE from Step 0.",
                 "[Reference Model] Initialized frozen reference model from SFT checkpoint",
                 "[Resume] Loaded base SFT weights for OPTIMIZE. Starting OPTIMIZE from Step 0.", log=BASE / t.model / "log.txt")
    shutil.rmtree(BASE, ignore_errors=True)
    t.clean()


if __name__ == "__main__":
    sys.exit(t.run(main))
