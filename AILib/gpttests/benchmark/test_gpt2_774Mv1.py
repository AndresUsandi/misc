# Copyright (c) Sebastian Raschka under Apache License 2.0 (see LICENSE.txt).
# Model Benchmark Test for andres-350M-1 (350M, bf16-trained): HellaSwag, ARC-Easy, LAMBADA, TriviaQA, WikiText-103.

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from gpttests.benchmark.benchcore import run_benchmark


# .sft.chk: the fine-tuned weights before DPO, so this model and andres-350M-1-fp8 are compared stage for stage
# ("pth" = the final exported weights, "trn" = pretrained only). Override from the command line with --weights.
WEIGHTS = "sft"


def main() -> int:
    return run_benchmark("gpt2-774M", weights=WEIGHTS)


if __name__ == "__main__":
    sys.exit(main())
