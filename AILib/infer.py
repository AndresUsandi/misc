# Copyright (c) Sebastian Raschka under Apache License 2.0 (see LICENSE.txt).
# Interactive Multi-Turn GPT Generation and Execution Script.

import sys
from typing import Dict, List

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from argsutil import build_inference_parser
from gptinfer.session import setup_inference, run_generation
from gptutils.consoleutils import print as printutil

print_plain = print
print = printutil


def main():
    # Defaults <- <model_name>.options-infer.json <- command line (see argsutil.InferenceArgs)
    args = build_inference_parser()

    ctx = setup_inference(args)

    single_prompt = args.prompt.strip() if args.prompt and args.prompt.strip() else None
    if not single_prompt:
        print("\nModel ready! Commands: 'exit'/'quit' to exit, '/clear' to reset context.\n")

    # Structured conversation state (accumulates multi-turn context)
    conversation_messages: List[Dict[str, str]] = []
    if args.system_prompt and str(args.system_prompt).strip():
        conversation_messages.append({"role": "system", "content": str(args.system_prompt).strip()})
    session_words = 0
    session_tokens = 0
    session_time = 0.0
    turn_count = 0

    while True:
        if single_prompt:
            user_input = single_prompt
        else:
            try:
                user_input = input("User: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nExiting session. Goodbye!")
                break

        if not user_input:
            continue

        if user_input.lower() in ["exit", "quit", "q"]:
            print("Exiting session. Goodbye!")
            break

        if user_input.lower() in ["/clear", "/reset"]:
            conversation_messages = []
            if args.system_prompt and str(args.system_prompt).strip():
                conversation_messages.append({"role": "system", "content": str(args.system_prompt).strip()})
            print("[Context cleared. Starting a fresh conversation.]\n")
            continue

        if single_prompt:
            print_plain(f"User: {user_input}")

        assistant_response, stats = run_generation(
            ctx=ctx,
            conversation_messages=conversation_messages,
            user_input=user_input,
            stream=True,
        )

        session_words += stats["words"]
        session_tokens += stats["tokens"]
        session_time += stats["elapsed_sec"]
        turn_count += 1

        avg_wpm = (session_words / session_time * 60.0) if session_time > 0 else 0.0
        avg_tps = (session_tokens / session_time) if session_time > 0 else 0.0

        print(
            f"⚡ [Performance] Response: {stats['tokens_per_sec']:.1f} tok/s | "
            f"Session Avg: {avg_tps:.1f} tok/s | "
            f"Tokens: {stats['tokens']} in {stats['elapsed_sec']:.2f}s\n"
        )

        if single_prompt:
            break


if __name__ == "__main__":
    main()
