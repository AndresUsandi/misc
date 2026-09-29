# Copyright (c) Sebastian Raschka under Apache License 2.0 (see LICENSE.txt).
# Model Working & Format Quality Validation Test for andres2xs-150M.

from pathlib import Path
import sys
from typing import Any, Dict, List, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from argsutil import build_inference_parser
from gptinfer.session import setup_inference, run_generation
from gpttests.data.validators import validate_format_quality


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
    print("=" * 70)
    print("       Model Quality & Format Validation Test: andres2xs-150M")
    print("=" * 70)

    args = build_inference_parser([
        "--model_name", "andres2xs-150M",
        "--max_new_tokens", "64",
        "--precision", "fp16",
    ])

    ctx = setup_inference(args)

    total_prompts = len(TEST_PROMPTS)
    passed_count = 0
    failures: List[Tuple[str, str, List[str]]] = []

    print("\nExecuting validation across 10 evaluation prompts...\n")

    for idx, prompt in enumerate(TEST_PROMPTS, 1):
        conversation: List[Dict[str, str]] = []
        response, stats = run_generation(
            ctx=ctx,
            conversation_messages=conversation,
            user_input=prompt,
            stream=False,
        )

        is_valid, errors = validate_format_quality(prompt, response)

        # Truncate response preview for display
        preview = response.replace("\n", " ").strip()
        if len(preview) > 100:
            preview = preview[:97] + "..."

        if is_valid:
            passed_count += 1
            print(f"[{idx:2d}/{total_prompts}] PASS | Prompt: \"{prompt}\"")
            print(f"       Response: \"{preview}\"")
            print(f"       Telemetry: {stats['tokens']} tokens in {stats['elapsed_sec']:.2f}s ({stats['tokens_per_sec']:.1f} tok/s)\n")
        else:
            failures.append((prompt, response, errors))
            print(f"[{idx:2d}/{total_prompts}] FAIL | Prompt: \"{prompt}\"")
            print(f"       Response: \"{preview}\"")
            for err in errors:
                print(f"       * Error: {err}")
            print()

    print("=" * 70)
    print(f"Validation Summary: {passed_count}/{total_prompts} Passed ({passed_count / total_prompts * 100:.1f}%)")
    print("=" * 70)

    if failures:
        print(f"\n[FAIL] {len(failures)} prompt(s) failed format validation:")
        for prompt, resp, errs in failures:
            print(f"- \"{prompt}\" -> {errs}")
        return 1

    print("\n[SUCCESS] All model format quality checks passed successfully!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
