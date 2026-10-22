# Copyright (c) Sebastian Raschka under Apache License 2.0 (see LICENSE.txt).
# Model Benchmark Test for andres-350M-1 (350M, bf16-trained): HellaSwag, ARC, SciQ, Winogrande, LAMBADA, TriviaQA, GSM8K, perplexities.

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from gpttests.benchmark.benchcore import run_benchmark


# "pth" = the served weights (the SFT result, or the DPO result for DPO models); "trn" = pretrained only, "sft" / "dpo" = that stage's
# checkpoint. Override from the command line with --weights. All benchmark sets run and the results go to
# bin/<model>/<model with underscores>_benchmark.json (see benchcore.py).
WEIGHTS = "pth"


def main() -> int:
    return run_benchmark("andres-150M-1", weights=WEIGHTS)


if __name__ == "__main__":
    sys.exit(main())
