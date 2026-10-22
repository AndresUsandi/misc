# Copyright (c) Sebastian Raschka under Apache License 2.0 (see LICENSE.txt).
# Model Working & Format Quality Validation Test for andres-350M-2-fp8v2.

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from gpttests.data.sessions import TEST_SESSIONS  # the standard 20 turns (10 factual, 10 creative) in 8 sessions
from gpttests.data.testcore import FULL_SUITE, run_model_quality_test


def main() -> int:
    return run_model_quality_test("andres-350M-2-fp8v2", TEST_SESSIONS, test_defaults=FULL_SUITE)


if __name__ == "__main__":
    sys.exit(main())
