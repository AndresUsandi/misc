"""
Checks a test's log.txt against its recorded expected log: expected/<N>gpu/<test>.txt, where N is the number of
visible CUDA devices (the log format differs with one or two GPUs visible).

Usage: python _e2e_logcheck.py <log.txt>
With E2E_RECORD=1 (set by "run_all_test.cmd record [tests]") the expected log is (re)recorded instead of checked.

Timestamps, durations, throughput, VRAM used by other processes and generated sample text are masked, and VRAM
figures are rounded to 0.1 GB. Everything else must match: text and integers exactly (files, parameters, steps, token
counts), decimals (losses, perplexities, margins, accuracies, learning rates, VRAM) within one unit of their last
printed digit. Runs are repeatable because train.py seeds its RNG and _e2e_env.cmd enables deterministic GPU kernels.
"""
import difflib
import os
import re
import sys
from pathlib import Path

MAX_REPORTED = 30

TIMESTAMP = re.compile(r"^\[\d{4}-\d\d-\d\d \d\d:\d\d:\d\d\] ?")
GENERATED = re.compile(r"^(Sample:|\s*\[Sample\]:|\s*\[Sample Response\]:|\s*Model Output:|\s*Response    :|\[Assistant\]:).*")
VOLATILE = re.compile(
    r"\b(?:\d+h )?(?:\d+m )?\d+(?:\.\d+)?s\b"                          # durations: 0h 0m 1s | 0m 6s (6.76s) | Eval: 0.06s
    r"|(?<=tok/sec: )\d+(?:,\d{3})*|[\d.]+(?= (?:tok/s|pairs/sec)\b)"  # throughput
    r"|[\d.]+(?= GiB already in use)"                                  # depends on other processes' VRAM
    r"|(?<=\| Tokens: )\d+"                                            # length of the sampled inference reply
)
VRAM = re.compile(r"\d+\.\d+(?=G\b| GB)")  # per-thread cuBLAS workspaces and compiler buffers move these by a few MB
NUMBER = re.compile(r"[-+]?\d+(?:,\d{3})*(?:\.\d+)?")


def normalize(text):
    lines, in_generated, temp = [], False, os.environ.get("TEMP")
    for raw in text.splitlines():
        stamped = bool(TIMESTAMP.match(raw))
        if in_generated and not stamped:
            continue  # continuation lines of multi-line generated text
        line = TIMESTAMP.sub("", raw)
        line = line.replace(temp, "%TEMP%") if temp else line
        in_generated = bool(GENERATED.match(line))
        line = VOLATILE.sub("*", GENERATED.sub(r"\1 <text>", line)).rstrip()
        line = VRAM.sub(lambda m: f"{float(m.group()):.1f}", line)
        if line.strip():
            lines.append(line)
    return lines


def same_number(expected, actual):
    if "." not in expected:
        return expected == actual
    unit = 10 ** -len(expected.split(".")[1])  # a value right at a rounding boundary may print one unit off
    return abs(float(actual.replace(",", "")) - float(expected.replace(",", ""))) <= unit * 1.0001


def compare(expected, actual):
    split = lambda lines: [(NUMBER.sub("#", l), NUMBER.findall(l)) for l in lines]
    exp, act = split(expected), split(actual)
    matcher = difflib.SequenceMatcher(None, [s for s, _ in exp], [s for s, _ in act], autojunk=False)
    diffs = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            diffs += [f"  expected  : {expected[i]}\n  actual    : {actual[j]}"
                      for i, j in zip(range(i1, i2), range(j1, j2)) if not all(map(same_number, exp[i][1], act[j][1]))]
        else:
            diffs.append("\n".join([f"  missing   : {l}" for l in expected[i1:i2]] + [f"  unexpected: {l}" for l in actual[j1:j2]]))
    return diffs


def main(log_path):
    log = Path(log_path)
    expected_file = Path(__file__).parent / "expected" / f"{os.environ.get('E2E_GPU_COUNT', '0')}gpu" / f"{log.parent.name}.txt"
    actual = normalize(log.read_text(encoding="utf-8", errors="replace"))
    if os.environ.get("E2E_RECORD") == "1":
        expected_file.parent.mkdir(parents=True, exist_ok=True)
        expected_file.write_text("\n".join(actual) + "\n", encoding="utf-8")
        print(f"[LOGCHECK] Recorded {len(actual)} expected log lines to {expected_file}")
        return 0
    if not expected_file.exists():
        print(f"[LOGCHECK] No expected log recorded at {expected_file} (record it with: run_all_test.cmd record {log.parent.name[5:]})")
        return 1
    diffs = compare(expected_file.read_text(encoding="utf-8").splitlines(), actual)
    if not diffs:
        print(f"[LOGCHECK] {len(actual)} log lines match {expected_file}")
        return 0
    print(f"[LOGCHECK] {len(diffs)} difference(s) between {log} and {expected_file}:")
    print("\n".join(diffs[:MAX_REPORTED]))
    print(f"[LOGCHECK] If the change is intended, re-record with: run_all_test.cmd record {log.parent.name[5:]}")
    return 1


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main(sys.argv[1]))
