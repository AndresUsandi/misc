# Copyright (c) Sebastian Raschka under Apache License 2.0 (see LICENSE.txt).
# Hugging Face references for the content-validation models (shared by nli.py, judge.py and download_judge.py; no heavy imports here).

from pathlib import Path

NLI_MODEL_ID = "MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli"
JUDGE_REPO_ID = "unsloth/gemma-4-E4B-it-GGUF"
JUDGE_FILENAME = "gemma-4-E4B-it-Q4_K_M.gguf"
JUDGE_DIR = Path(__file__).resolve().parents[2] / "bin" / "judge"
