#!/usr/bin/env python3
"""
Runs the E2E suite and prints a PASS / FAIL / SKIP summary.

Usage: python gpttests/e2e/run_all_tests.py --set <set> [--record] [--tests names...]      e.g.  run_all_tests.py --set 5070 --tests basic resume

<set> names the machine whose recorded logs (expected/<set>/test-*.txt) the run is compared with:
  2080  the single RTX 2080 SUPER machine (fp16 compute). Its default list leaves out the multi-GPU suites (dp*, pp*), which that
        machine cannot run; name them explicitly to run them elsewhere.
  5070  the dual RTX 5070 Ti machines (bf16 compute, fp8 capable). Default list: every test.
Every test is single-GPU by its own options files except the designated multi-GPU suites (dp, dp-compile, dp-fp8, dp-zero1,
dp-zero1-fp8, dp-zero1-muon, dp-zero1-switch, pp, pp-async), which skip themselves when fewer than 2 CUDA devices are visible.
E2E_TESTS narrows the default list. After an intended behavior change, re-record a machine's logs on that machine with:
  python gpttests/e2e/run_all_tests.py --set <set> --record [--tests names...]
"""
import os
import argparse
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from _e2e import probe_gpus

E2E_DIR = Path(__file__).resolve().parent
SINGLE_GPU = ("basic hyperparams data-text paths resume epochs stage-order muon muon-bf16 compile-actchk precision-fp32 precision-fp8 "
              "lowvram autocast-cache json-precompute vocab multifile device basedir cpu tokenizer-qwen tokenizer-smollm").split()
MULTI_GPU = "dp dp-compile dp-fp8 dp-zero1 dp-zero1-fp8 dp-zero1-muon dp-zero1-switch pp pp-async".split()
DEFAULT_TESTS = {"2080": SINGLE_GPU}  # every other set runs everything


def main(argv):
    sets = sorted(p.name for p in (E2E_DIR / "expected").iterdir() if p.is_dir())
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--set", choices=sets, required=True, help="recorded-log set to compare against")
    parser.add_argument("--tests", nargs="*", default=os.environ.get("E2E_TESTS", "").split(), help="test names to run (default: E2E_TESTS, else the set's default list)")
    parser.add_argument("--record", action="store_true", help="record the expected logs instead of checking them")
    parsed = parser.parse_args(argv)
    os.environ["E2E_EXPECTED"] = parsed.set
    if parsed.record:
        os.environ["E2E_RECORD"] = "1"
    tests = parsed.tests or DEFAULT_TESTS.get(parsed.set, SINGLE_GPU + MULTI_GPU)
    probe_gpus()  # once for the whole run; the tests inherit E2E_GPU_COUNT instead of probing again
    summary = Path(tempfile.gettempdir()) / "ailib-e2e-summary.txt"
    lines = [f"E2E run started {time.strftime('%Y-%m-%d %H:%M:%S')} (expected-log set: {parsed.set})"]
    counts = {"PASS": 0, "FAIL": 0, "SKIP": 0}
    for name in tests:
        code = subprocess.call([sys.executable, str(E2E_DIR / f"test-{name}.py")])
        verdict = {0: "PASS", 2: "SKIP"}.get(code, "FAIL")
        counts[verdict] += 1
        lines.append(f"[{verdict}] test-{name}")
        summary.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n" + "=" * 60)
    print(f"E2E SUMMARY ({parsed.set} logs): {counts['PASS']} passed, {counts['FAIL']} failed, {counts['SKIP']} skipped")
    if os.environ.get("E2E_RECORD") == "1":
        print("[RECORD MODE] Expected logs were recorded, not checked.")
    print("=" * 60)
    print("\n".join(lines))
    return 1 if counts["FAIL"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
