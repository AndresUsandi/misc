# Copyright (c) Sebastian Raschka under Apache License 2.0 (see LICENSE.txt).
# Model Working & Format Quality Validation Test for gpt2-774M.

from pathlib import Path
import sys
from typing import Any, Dict, List, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from argsutil import build_inference_parser
from gptinfer.session import setup_inference, run_generation
from gpttests.data.validators import validate_format_quality


# Evaluation sessions matching interactive test prompts:
# Sessions 1 & 2 are standalone questions; sessions 3 & 4 are multi-turn conversations.
TEST_SESSIONS: List[List[str]] = [
    [
        "what is the capital of france?",
    ],
    [
        'who wrote the book "frankenstein"?',
    ],
    [
        "when did mankind first land on the moon?",
        "what was the name of the rocket that took them there?",
        "in what country was the rocket made?",
    ],
    [
        "please write a short story",
        "how does this story make you feel?",
    ],
]


def main() -> int:
    print("=" * 70)
    print("       Model Quality & Format Validation Test: gpt2-774M")
    print("=" * 70)

    args = build_inference_parser([
        "--model_name", "gpt2-774M",
        "--precision", "fp16",
    ])

    ctx = setup_inference(args)

    total_prompts = sum(len(session) for session in TEST_SESSIONS)
    passed_count = 0
    failures: List[Tuple[str, str, List[str]]] = []
    global_idx = 0

    print(f"\nExecuting validation across {len(TEST_SESSIONS)} conversation session(s) ({total_prompts} total turns)...\n")

    for session_idx, session_prompts in enumerate(TEST_SESSIONS, 1):
        conversation: List[Dict[str, str]] = []
        is_multiturn = len(session_prompts) > 1
        session_label = f"Session {session_idx} ({'Multi-Turn' if is_multiturn else 'Single-Turn'}, {len(session_prompts)} turns)"
        print(f"--- {session_label} ---")

        for turn_idx, prompt in enumerate(session_prompts, 1):
            global_idx += 1
            response, stats = run_generation(
                ctx=ctx,
                conversation_messages=conversation,
                user_input=prompt,
                stream=False,
            )

            is_valid, errors = validate_format_quality(prompt, response)

            preview = response.replace("\n", " ").strip()
            if len(preview) > 100:
                preview = preview[:97] + "..."

            if is_valid:
                passed_count += 1
                turn_str = f"Turn {turn_idx}" if is_multiturn else "Prompt"
                print(f"[{global_idx:2d}/{total_prompts}] PASS | {turn_str}: \"{prompt}\"")
                print(f"       Response: \"{preview}\"")
                print(f"       Telemetry: {stats['tokens']} tokens in {stats['elapsed_sec']:.2f}s ({stats['tokens_per_sec']:.1f} tok/s)\n")
            else:
                failures.append((prompt, response, errors))
                turn_str = f"Turn {turn_idx}" if is_multiturn else "Prompt"
                print(f"[{global_idx:2d}/{total_prompts}] FAIL | {turn_str}: \"{prompt}\"")
                print(f"       Response: \"{preview}\"")
                for err in errors:
                    print(f"       * Error: {err}")
                print()

            conversation.append({"role": "user", "content": prompt})
            conversation.append({"role": "assistant", "content": response})

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
