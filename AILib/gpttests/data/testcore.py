# Copyright (c) Sebastian Raschka under Apache License 2.0 (see LICENSE.txt).
# Shared test execution core for model quality tests: format checks (validators), Tier A spec rules, Tier B NLI, Tier C LLM judge,
# N seeded samples per turn with a required pass rate.

import argparse
import copy
import json
import math
from pathlib import Path
import re
import sys
import time
from typing import Any, Dict, List, Optional, Tuple, Union

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import torch

from argsutil import build_inference_parser
from gptinfer.session import setup_inference, run_generation
from gpttests.data.judge import LlmJudge
from gpttests.data.nli import NliVerifier
from gpttests.data.sessions import FACTUAL_SESSIONS_EXTENDED
from gpttests.data.validators import (
    CATEGORY_FACTUAL, SPEC_CATEGORY, SPEC_FACTS, SPEC_PROMPT, validate_content_spec, validate_format_quality,
)
from gpttests.testutil import run_test
from gptutils.consoleutils import str_to_bool

TurnSpec = Dict[str, Any]
# What the per-model test files run by default: every check (5 seeded samples per turn, judge, NLI, the 127-question extended factual set,
# the 40 head-to-head prompts) with the results written to bin/<model>/<model with underscores>_data.json. The command line overrides any of it.
FULL_SUITE = ["--samples", "5", "--judge", "true", "--nli", "true", "--extended_factual", "true", "--head_to_head", "true", "--output_to_file", "auto"]


def normalize_spec(turn: Union[str, TurnSpec]) -> TurnSpec:
    """A bare prompt string becomes a factual spec with no Tier A rules (format checks + judge still apply)."""
    spec = {SPEC_PROMPT: turn} if isinstance(turn, str) else dict(turn)
    spec.setdefault(SPEC_CATEGORY, CATEGORY_FACTUAL)
    return spec


def _parse_test_args(argv: List[str]) -> Tuple[argparse.Namespace, List[str]]:
    """Test-harness options; everything unrecognized is forwarded to build_inference_parser."""
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--samples", type=int, default=5, help="Generations per turn; each uses seed + sample_index.")
    parser.add_argument("--min_pass_rate", type=float, default=0.8, help="Fraction of samples that must pass for the turn to pass.")
    parser.add_argument("--seed", type=int, default=1234, help="Base seed for reproducible sampling.")
    parser.add_argument("--nli", type=str_to_bool, nargs="?", const=True, default=True, help="Run the Tier B NLI verifier on turns that define facts.")
    parser.add_argument("--judge", type=str_to_bool, nargs="?", const=True, default=True, help="Run the Tier C LLM judge on every turn.")
    parser.add_argument("--judge_gpu", type=int, default=None, help="CUDA device for the NLI model and judge GGUF (default: last GPU).")
    parser.add_argument("--extended_factual", type=str_to_bool, nargs="?", const=True, default=True, help="Also run sessions.FACTUAL_SESSIONS_EXTENDED (117 more factual turns, 127 in total) so factual accuracy is measured on hundreds of distinct questions instead of ten. Default True; set false for the quick 20-turn run.")
    parser.add_argument("--head_to_head", type=str_to_bool, nargs="?", const=True, default=True, help="Also generate the 40 headtohead.PROMPTS x 2 seeds (~5 min) and keep the replies in the output file, so gpttests/compare_models.py can judge this model against another one.")
    parser.add_argument("--output_to_file", nargs="?", const="auto", default="auto", help="Write every turn, sample, verdict and the head-to-head replies to a JSON file for gpttests/compare_models.py: a path, or (default) bin/<model>/<model with underscores>_data.json; 'none' to skip.")
    if "-h" in argv or "--help" in argv:  # the inference parser prints its own help next; this parser has none of its own so unknown options pass through
        print("Test harness options (everything else goes to the inference options below):\n" + parser.format_help())
    return parser.parse_known_args(argv)


CORE_ERRORS = ("Expected answer not found", "Forbidden term", "Response does not match")  # Tier A: the core answer itself is wrong
PRONOUN = re.compile(r"\b(he|she|it|that happen|him|her)\b")


def summarize_records(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Aggregates per-turn records into the figures compare_models.py reports: per subset, judge passes (with standard error), mean judge
    score, failure profile (core answer wrong vs right-but-an-added-claim-rejected), reply length, turns passed."""
    def stats(turns: List[Dict[str, Any]]) -> Dict[str, Any]:
        ss = [s for t in turns for s in t["samples"]]
        n = len(ss)
        if not n:
            return {"n": 0, "turns": 0}
        jp = sum(bool(s["judge_pass"]) for s in ss)
        scores = [s["judge_score"] for s in ss if s["judge_score"] is not None]
        core_wrong = sum(any(e.startswith(CORE_ERRORS) for e in s["errors"]) for s in ss)
        pct = 100 * jp / n
        return {"n": n, "turns": len(turns), "turns_passed": sum(t["turn_ok"] for t in turns), "samples_passed": sum(s["passed"] for s in ss),
                "judge_pass": jp, "judge_pass_pct": round(pct, 1), "se": round(100 * math.sqrt(max(pct / 100 * (1 - pct / 100), 1e-9) / n), 1),
                "judge_mean": round(sum(scores) / len(scores), 2) if scores else None,
                "core_wrong": core_wrong, "right_but_judge_fail": sum((not any(e.startswith(CORE_ERRORS) for e in s["errors"])) and s["judge_pass"] is False for s in ss),
                "avg_tokens": round(sum(s["tokens"] for s in ss) / n, 1),
                "one_word": sum(len(s["response"].split()) <= 2 for s in ss),
                "loops_or_truncations": sum(any(("repet" in e.lower() or "loop" in e.lower() or "truncat" in e.lower() or "cut off" in e.lower()) for e in s["errors"] + s["warnings"]) for s in ss)}
    fact = [t for t in records if t["category"] == CATEGORY_FACTUAL]
    base = [t for t in records if not t["extended"]]
    return {"all": stats(records), "base": stats(base), "factual": stats([t for t in fact if not t["extended"]]), "creative": stats([t for t in base if t["category"] != CATEGORY_FACTUAL]),
            "story": stats([t for t in base if t["category"] != CATEGORY_FACTUAL and t["session_turns"] >= 6]),
            "factual_all": stats(fact), "factual_extended": stats([t for t in fact if t["extended"]]),
            "single_turn": stats([t for t in fact if t["extended"] and not PRONOUN.search(t["prompt"])]), "pronoun_followups": stats([t for t in fact if t["extended"] and PRONOUN.search(t["prompt"])])}


def _evaluate_sample(spec: TurnSpec, response: str, stats: Dict[str, Any], ctx: Dict[str, Any], history: List[Dict[str, str]],
                     nli: Optional[NliVerifier], judge: Optional[LlmJudge]) -> Tuple[List[str], List[str], List[str], Optional[bool], Optional[int]]:
    """Runs every validation tier on one sample. Returns (errors, warnings, notes, judge_pass, judge_score); any error fails the sample."""
    _, errors, warnings = validate_format_quality(spec[SPEC_PROMPT], response, stats, ctx["spell_checker"])
    errors += validate_content_spec(spec, response)
    notes: List[str] = []
    judge_pass = judge_score = None
    if judge:
        verdict = judge.grade(history, spec[SPEC_PROMPT], response, spec)
        judge_pass, judge_score = verdict["pass"], verdict.get("score")
        line = f"Judge {'PASS' if judge_pass else 'FAIL'} (score {verdict['score']}/5) {verdict['issues']}"
        (notes if judge_pass else errors).append(line)
        if judge_pass:
            # The length heuristics misfire on a correct one-word answer ("Paris"); once the judge has read and passed the response they
            # are only worth a warning.
            demoted = [e for e in errors if e.startswith(("Response too short", "Who/where/which-name question answered without any proper noun"))]
            warnings += [f"{e} (judge passed, demoted)" for e in demoted]
            errors[:] = [e for e in errors if e not in demoted]
    if nli and spec.get(SPEC_FACTS):
        contradicted, unsupported = nli.check(spec[SPEC_FACTS], response)
        # NLI contradictions are errors on their own only when no judge is running or the judge also failed the sample; the NLI
        # cross-encoder has false positives on sentences that merely share an entity with a fact, so a passing judge demotes them.
        nli_sink = warnings if judge_pass else errors
        nli_sink += [f"NLI contradiction{' (judge disagrees)' if judge_pass else ''}: {c}" for c in contradicted]
        if unsupported:
            warnings.append(f"NLI: {len(unsupported)} sentence(s) not supported by the reference facts, e.g. {unsupported[0]}")
    return errors, warnings, notes, judge_pass, judge_score


def run_model_quality_test(
    model_name: str,
    test_cases: Union[List[List[Union[str, TurnSpec]]], List[Union[str, TurnSpec]]],
    extra_args: Optional[List[str]] = None,
    test_defaults: Optional[List[str]] = None,
) -> int:
    """
    Executes model quality validation across sessions or single-turn prompts, from the repository root and between the
    Running / [PASS] / [FAIL] banners.

    Args:
        model_name: Model identifier (e.g. 'gpt2-774M', 'andres1s-350M').
        test_cases: Either a list of multi-turn conversation sessions (list of turns) or a list of standalone turns.
                    A turn is a prompt string or a spec dict (see validators.SPEC_* keys).
        extra_args: Optional additional command-line argument overrides for inference.
        test_defaults: Harness options (--samples, --judge, ...) this test starts from; the command line overrides them.

    Returns:
        0 if every turn reached the required pass rate, 1 otherwise.
    """
    return run_test(f"Model Data Test: {model_name}", "Format Validation", lambda: _quality_test(model_name, test_cases, extra_args, test_defaults))


def _quality_test(model_name, test_cases, extra_args, test_defaults) -> int:
    test_args, passthrough = _parse_test_args((test_defaults or []) + sys.argv[1:])
    print("=" * 70)
    print(f"       Model Quality & Content Validation Test: {model_name}")
    print("=" * 70)

    cmd_args = ["--model_name", model_name, "--precision", "fp16"] + (extra_args or []) + passthrough
    args = build_inference_parser(cmd_args)
    ctx = setup_inference(args)

    aux_gpu = test_args.judge_gpu if test_args.judge_gpu is not None else max(torch.cuda.device_count() - 1, 0)
    aux_device = torch.device(f"cuda:{aux_gpu}" if torch.cuda.is_available() else "cpu")
    nli = NliVerifier(aux_device) if test_args.nli else None
    judge = LlmJudge(aux_gpu) if test_args.judge else None
    print(f"[Validation] samples/turn={test_args.samples} min_pass_rate={test_args.min_pass_rate:.0%} seed={test_args.seed} "
          f"nli={'on' if nli else 'off'} judge={'on' if judge else 'off'} aux_device={aux_device}")

    is_session_list = bool(test_cases and isinstance(test_cases[0], (list, tuple)))
    sessions: List[List[TurnSpec]] = [[normalize_spec(t) for t in s] for s in (test_cases if is_session_list else [[t] for t in test_cases])]  # type: ignore
    base_turns = sum(len(s) for s in sessions)
    if test_args.extended_factual:
        sessions += [[normalize_spec(t) for t in s] for s in FACTUAL_SESSIONS_EXTENDED]

    is_multiturn_suite = any(len(s) > 1 for s in sessions)
    total_prompts = sum(len(s) for s in sessions)
    passed_count = 0
    failures: List[Tuple[str, int, int]] = []
    records: List[Dict[str, Any]] = []
    global_idx = 0
    t_start = time.time()

    if is_multiturn_suite:
        print(f"\nExecuting validation across {len(sessions)} conversation session(s) ({total_prompts} total turns)...\n")
    else:
        print(f"\nExecuting validation across {total_prompts} evaluation prompts...\n")

    for session_idx, session_specs in enumerate(sessions, 1):
        conversation: List[Dict[str, str]] = []
        is_multiturn = len(session_specs) > 1
        if is_multiturn_suite:
            session_label = f"Session {session_idx} ({'Multi-Turn' if is_multiturn else 'Single-Turn'}, {len(session_specs)} turns)"
            print(f"--- {session_label} ---")

        for turn_idx, spec in enumerate(session_specs, 1):
            global_idx += 1
            prompt = spec[SPEC_PROMPT]
            turn_str = f"Turn {turn_idx}" if is_multiturn else "Prompt"
            print(f"[{global_idx:2d}/{total_prompts}] {turn_str}: \"{prompt}\" [{spec[SPEC_CATEGORY]}]")

            passed_samples = 0
            chosen_conv: Optional[List[Dict[str, str]]] = None
            first_conv: Optional[List[Dict[str, str]]] = None
            samples: List[Dict[str, Any]] = []
            for k in range(test_args.samples):
                conv = copy.deepcopy(conversation)
                response, stats = run_generation(ctx=ctx, conversation_messages=conv, user_input=prompt, stream=False, seed=test_args.seed + k)
                errors, warnings, notes, judge_pass, judge_score = _evaluate_sample(spec, response, stats, ctx, conversation, nli, judge)
                is_valid = not errors
                passed_samples += is_valid
                samples.append({"seed": test_args.seed + k, "response": response, "tokens": stats["tokens"], "elapsed_sec": round(stats["elapsed_sec"], 2), "passed": is_valid,
                                "judge_pass": judge_pass, "judge_score": judge_score, "errors": errors, "warnings": warnings})
                first_conv = first_conv or conv
                if is_valid and chosen_conv is None:
                    chosen_conv = conv
                print(f"   sample {k + 1}/{test_args.samples} {'PASS' if is_valid else 'FAIL'} | seed {test_args.seed + k} | "
                      f"{stats['tokens']} tokens in {stats['elapsed_sec']:.2f}s ({stats['tokens_per_sec']:.1f} tok/s)")
                print(f"      Response: \"{response}\"")
                for err in errors:
                    print(f"      * Error: {err}")
                for warn in warnings:
                    print(f"      * Warning: {warn}")
                for note in notes:
                    print(f"      * {note}")

            pass_rate = passed_samples / test_args.samples
            turn_ok = pass_rate >= test_args.min_pass_rate
            passed_count += turn_ok
            if not turn_ok:
                failures.append((prompt, passed_samples, test_args.samples))
            records.append({"idx": global_idx, "session": session_idx, "turn": turn_idx, "session_turns": len(session_specs), "prompt": prompt, "category": spec[SPEC_CATEGORY],
                            "extended": global_idx > base_turns, "samples": samples, "passed_samples": passed_samples, "turn_ok": turn_ok})
            print(f"   => {'PASS' if turn_ok else 'FAIL'} | pass rate {passed_samples}/{test_args.samples} ({pass_rate:.0%}), required >= {test_args.min_pass_rate:.0%}\n")
            conversation = chosen_conv or first_conv or conversation

    print("=" * 70)
    print(f"Validation Summary: {passed_count}/{total_prompts} turns passed ({passed_count / total_prompts * 100:.1f}%)")
    print("=" * 70)

    if test_args.output_to_file and test_args.output_to_file.lower() != "none":
        from gpttests.data.headtohead import PROMPTS, SEEDS, generate_replies
        replies = None
        if test_args.head_to_head:
            t0 = time.time()
            replies = generate_replies(ctx)
            print(f"[Head-to-head] {len(replies)} replies to the {len(PROMPTS)} fixed prompts x {len(SEEDS)} seeds in {time.time() - t0:.0f}s")
        out = Path(test_args.output_to_file) if test_args.output_to_file != "auto" else Path(args.models_base_dir) / model_name / f"{model_name.replace('-', '_')}_data.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps({"kind": "data", "model": model_name, "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"), "elapsed_sec": round(time.time() - t_start),
                                   "settings": {"samples": test_args.samples, "min_pass_rate": test_args.min_pass_rate, "seed": test_args.seed, "nli": bool(nli), "judge": bool(judge),
                                                "extended_factual": bool(test_args.extended_factual), "base_turns": base_turns, "total_turns": total_prompts, "system_prompt": args.system_prompt,
                                                "inference_args": passthrough},
                                   "summary": summarize_records(records), "turns": records,
                                   "head_to_head": {"prompts": PROMPTS, "seeds": SEEDS, "replies": replies} if replies else None}, indent=1), encoding="utf-8")
        print(f"[Output] Results written to {out}  (compare with: python gpttests/compare_models.py <this file> <another model's file>)")

    if failures:
        print(f"\n[FAIL] {len(failures)} turn(s) below the required pass rate:")
        for prompt, ok, n in failures:
            print(f"- \"{prompt}\" -> {ok}/{n} samples passed")
        return 1

    print("\n[SUCCESS] All model quality checks passed successfully!")
    return 0


if __name__ == "__main__":  # python gpttests/data/testcore.py --model_name <model> [harness and inference options]: the standard suite for any model
    from gpttests.data.sessions import TEST_SESSIONS
    p = argparse.ArgumentParser(add_help=False)
    p.add_argument("--model_name", required=True)
    known, rest = p.parse_known_args()
    sys.argv = [sys.argv[0]] + rest
    sys.exit(run_model_quality_test(known.model_name, TEST_SESSIONS))
