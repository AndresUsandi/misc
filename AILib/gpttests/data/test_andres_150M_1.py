# Copyright (c) Sebastian Raschka under Apache License 2.0 (see LICENSE.txt).
# Model Working & Format Quality Validation Test for andres1xs-150M.

from pathlib import Path
import sys
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from gpttests.data.testcore import FULL_SUITE, run_model_quality_test


TEST_PROMPTS = [
    "what is the capital of france?",
    "who wrote the book frankenstein?",
    "when did mankind first reach the surface of the moon?",
    "who was the first president of the united states?",
    "what is the largest planet in our solar system?",
    "what chemical element has the symbol Au?",
    "in what year was the first commercial airplane flight?",
    "what is the tallest mountain in the world above sea level?",
    "who invented the telephone?",
    "what is the primary function of red blood cells in the human body?",
]


def main() -> int:
    return run_model_quality_test("andres-150M-1", TEST_PROMPTS, test_defaults=FULL_SUITE)


if __name__ == "__main__":
    sys.exit(main())
