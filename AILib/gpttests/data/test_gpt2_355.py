# Copyright (c) Sebastian Raschka under Apache License 2.0 (see LICENSE.txt).
# Model Working, Format & Content Quality Validation Test for gpt2-774M.

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from gpttests.data.sessions import TEST_SESSIONS  # the standard 20 turns (10 factual, 10 creative) in 8 sessions, with facts and rubrics
from gpttests.data.testcore import run_model_quality_test


def main() -> int:
    return run_model_quality_test("gpt2-355M", TEST_SESSIONS)


if __name__ == "__main__":
    sys.exit(main())
