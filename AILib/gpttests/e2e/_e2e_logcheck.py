"""
Checks a test's log.txt against its recorded expected log: expected/<set>/<test>.txt, where <set> names the machine the logs
were recorded on (2080 = dual RTX 2080 SUPER, fp16 compute; 5070 = dual RTX 5070 Ti, bf16 compute; losses, dtypes and device
names differ between them). Each test decides for itself whether it runs single- or multi-GPU through its options files, and the
recordings were made with every GPU of the machine visible (the [VRAM] report prints one line per visible device).

Usage: python _e2e_logcheck.py <log.txt> [<set>]
The set defaults to the E2E_EXPECTED environment variable, which run_all_tests.py sets explicitly and _e2e.py derives from the GPU
model when a test-*.py is run on its own.
With E2E_RECORD=1 (set by "run_all_tests.py --set <set> --record [--tests names]") the expected log is (re)recorded instead of checked.

Only the numbers are compared, never the text. Every number in the log is picked up together with the words right before it
(its label: "Train", "Val", "PPL", "Margin Tr", "[VRAM cuda:0] peak", "Total updates", ...; a line's leading [Tag] and a
"Header:" prefix are part of the label), and the sequence of values of each label is compared with the recorded one in order.
Labels that exist on only one side (a field added, removed or renamed, a reworded line) are reported for information and do
not fail the check, so cosmetic log changes never require re-recording; a changed value, or a changed number of values of a
label (an evaluation line more or less), does.

Timestamps, durations, throughput, VRAM used by other processes and generated sample text are masked, as are discrete DPO
batch accuracies and the static "(ideal: ...)" ranges. Decimals (losses, perplexities, margins, learning rates) match within
1% relative tolerance, one unit of their last printed digit, or 0.05 absolute tolerance near zero; integers must match
exactly. On the "[VRAM cuda:N]" memory report lines the process-specific figures (process total, device use, other
processes, allocator retries) and the allocator's reserved pool (reserved, unused: they move with driver and compiler
workspaces between runs) are masked; the remaining GB figures get a 10% relative / 0.1 GB absolute tolerance.
"""
import os
import re
import sys
import tempfile
from pathlib import Path

MAX_REPORTED = 30

TIMESTAMP = re.compile(r"^\[\d{4}-\d\d-\d\d \d\d:\d\d:\d\d\] ?")
GENERATED = re.compile(r"^(Sample:|\s*\[Sample\]:|\s*\[Sample Response\]:|\s*Model Output:|\s*Response    :|\[Assistant\]:).*")
CACHE_STATE = re.compile(r"^\[Token Cache\] ")  # printed only when a text file is (re)tokenized: depends on what earlier runs left on disk, not on the code under test
VOLATILE = re.compile(
    r"\b(?:\d+h )?(?:\d+m )?\d+(?:\.\d+)?s\b"                          # durations: 0h 0m 1s | 0m 6s (6.76s) | Eval: 0.06s
    r"|(?<=tok/sec: )\d+(?:,\d{3})*|[\d.]+(?= (?:tok/s|pairs/sec)\b)"  # throughput
    r"|[\d.]+(?= GiB already in use)"                                  # depends on other processes' VRAM
    r"|(?<=\bAcc: )(?:Tr [\d.]+%,\s+Val [\d.]+%|[\d.]+%)"              # discrete DPO batch accuracy
    r"|(?<=\| Tokens: )\d+"                                            # length of the sampled inference reply
    r"|(?<=-)\d{8}-\d{6}(?=\.chk\.(?:trn|sft|dpo)\b)"                   # save-time stamp in archived checkpoint names (--checkpoint_keep_n)
    r"|(?<=\| process )[\d.]+|(?<=\| device )[\d.]+/[\d.]+|(?<=\(others )[\d.]+|(?<=alloc retries )\d+"  # [VRAM] report: process-specific figures
    r"|(?<=\| reserved )[\d.]+|(?<=\(unused )[\d.]+"                   # [VRAM] report: the allocator's reserved pool moves with driver/compiler workspaces between runs
)
VRAM_LINE = re.compile(r"^\[VRAM cuda:\d+\] ")  # memory report lines: loose tolerance on the remaining GB figures
NUMBER = re.compile(r"(?<![\w.])[-+]?\d+(?:,\d{3})*(?:\.\d+)?(?:[eE][-+]?\d+)?(?![\w]|\.\d)")  # not glued to a word: e2e, fp8, float32, combined_1, 10BT, 51.2M are names


def normalize(text):
    lines, in_generated, temp = [], False, tempfile.gettempdir()  # the same folder test-basedir.py uses, on every OS
    for raw in text.splitlines():
        stamped = bool(TIMESTAMP.match(raw))
        if in_generated and not stamped:
            continue  # continuation lines of multi-line generated text
        line = TIMESTAMP.sub("", raw)
        if CACHE_STATE.match(line):
            continue
        line = line.replace(temp, "%TEMP%") if temp else line
        in_generated = bool(GENERATED.match(line))
        line = VOLATILE.sub("*", GENERATED.sub(r"\1 <text>", line)).rstrip()
        if line.strip():
            lines.append(line)
    return lines


REL_TOL = 0.01  # 1% relative tolerance for cross-machine / driver GPU variance
ABS_TOL = 0.05  # absolute tolerance for differences near zero (e.g. margins, gaps)


def same_number(expected, actual, rel_tol=REL_TOL, abs_tol=ABS_TOL):
    if "." not in expected or "." not in actual:
        return expected == actual
    e_val = float(expected.replace(",", ""))
    a_val = float(actual.replace(",", ""))
    unit = 10 ** -len(expected.split(".")[1])  # a value right at a rounding boundary may print one unit off
    diff = abs(a_val - e_val)
    effective_abs_tol = abs_tol if len(expected.split(".")[1]) <= 4 else unit * 1.0001
    return diff <= max(unit * 1.0001, effective_abs_tol, abs(e_val) * rel_tol)


TAG = re.compile(r"^\s*(\[[^\]]*\])\s*")  # a line's leading tag: [VRAM cuda:0], [Training Plan], [gptio], [Data], ...
WORD = re.compile(r"[A-Za-z][A-Za-z_]*")
IGNORED_LABEL = re.compile(r"\bideal\b")  # the static "(ideal: 3.90-4.05)" guidance ranges of the summary blocks


def metrics(lines):
    """{label: [(value, is_vram), ...]} for every number of the normalized log, in order of appearance. A number's label is the
    line's [Tag] + the segment's "Header:" (a "|"-separated segment whose text before the colon has no digits) + the last three
    words before the number; a number right after "<number>/" gets the previous label + "/" (the denominator of a "2/4").
    Numbers with no label at all (e.g. the "- 50%" of a step line) are not metrics."""
    out = {}
    for line in lines:
        vram = bool(VRAM_LINE.match(line))
        m = TAG.match(line)
        tag, rest = (m.group(1), line[m.end():]) if m else ("", line)
        line_header = ""
        for seg in rest.split(" | "):
            head, colon, body = seg.partition(":")
            header = " ".join(WORD.findall(head)) if colon and WORD.search(head) and not any(c.isdigit() for c in head) else ""
            if header:
                line_header = header
            else:
                header, body = line_header, seg  # "Final Losses : Train 10.3 | Val 10.4": a segment without its own header keeps the line's
            prev_label, prev_end = None, 0
            for n in NUMBER.finditer(body):
                between = body[prev_end:n.start()]
                words = WORD.findall(between)
                if prev_label and between.strip() == "/":
                    label = prev_label + "/"
                else:
                    label = " ".join(p for p in (tag, header, " ".join(words[-3:])) if p) if (words or header or (tag and prev_end == 0)) else None
                prev_label, prev_end = label, n.end()
                if label and not IGNORED_LABEL.search(label):
                    out.setdefault(label, []).append((n.group(0), vram))
    return out


INTEGER = re.compile(r"[-+]?\d+(?:,\d{3})*")


def same_value(expected, actual, vram):
    if INTEGER.fullmatch(expected) and INTEGER.fullmatch(actual):
        return int(expected.replace(",", "")) == int(actual.replace(",", ""))  # integers: exact, whatever the zero padding
    if "e" in expected.lower() or "e" in actual.lower():  # scientific notation (learning_rate=5e-06): relative tolerance only
        e_val, a_val = float(expected.replace(",", "")), float(actual.replace(",", ""))
        return abs(a_val - e_val) <= max(abs(e_val) * REL_TOL, 1e-12)
    return same_number(expected, actual, *((0.10, 0.10) if vram else (REL_TOL, ABS_TOL)))


def compare(expected, actual):
    """Differences in the values of the labels both logs have; labels on one side only are listed in the second element."""
    exp, act = metrics(expected), metrics(actual)
    diffs, info = [], []
    for label in exp:
        if label not in act:
            info.append(f"removed: {label}")
            continue
        e, a = exp[label], act[label]
        if len(e) != len(a):
            diffs.append(f"  {label}: {len(e)} value(s) expected ({', '.join(v for v, _ in e[:8])}{', ...' if len(e) > 8 else ''}), {len(a)} found ({', '.join(v for v, _ in a[:8])}{', ...' if len(a) > 8 else ''})")
            continue
        diffs += [f"  {label} #{i + 1} of {len(e)}: expected {ev}, actual {av}" for i, ((ev, vram), (av, _)) in enumerate(zip(e, a)) if not same_value(ev, av, vram)]
    info += [f"new: {label}" for label in act if label not in exp]
    return diffs, info


def main(log_path, expected_set=None):
    log = Path(log_path)
    expected_set = expected_set or os.environ.get("E2E_EXPECTED")
    if not expected_set:
        print("[LOGCHECK] No expected-log set given: pass it as the second argument or set E2E_EXPECTED (e.g. 2080 or 5070).")
        return 1
    test_name = log.parent.name[5:]
    expected_file = Path(__file__).parent / "expected" / expected_set / f"{log.parent.name}.txt"
    actual = normalize(log.read_text(encoding="utf-8", errors="replace"))
    if os.environ.get("E2E_RECORD") == "1":
        expected_file.parent.mkdir(parents=True, exist_ok=True)
        expected_file.write_text("\n".join(actual) + "\n", encoding="utf-8")
        print(f"[LOGCHECK] Recorded {len(actual)} expected log lines to {expected_file}")
        return 0
    if not expected_file.exists():
        print(f"[LOGCHECK] No expected log recorded at {expected_file} (record it with: python gpttests/e2e/run_all_tests.py --set {expected_set} --record --tests {test_name})")
        return 1
    expected = [VOLATILE.sub("*", l) for l in expected_file.read_text(encoding="utf-8").splitlines()]
    diffs, info = compare(expected, actual)
    compared = sum(len(v) for k, v in metrics(expected).items())
    if info:
        print(f"[LOGCHECK] {len(info)} label(s) on one side only, ignored (text or field changes; re-record to refresh): {'; '.join(info[:MAX_REPORTED])}")
    if not diffs:
        print(f"[LOGCHECK] {compared} recorded values match {expected_file}")
        return 0
    print(f"[LOGCHECK] {len(diffs)} value difference(s) between {log} and {expected_file}:")
    print("\n".join(diffs[:MAX_REPORTED]))
    print(f"[LOGCHECK] If the change is intended, re-record with: python gpttests/e2e/run_all_tests.py --set {expected_set} --record --tests {test_name}")
    return 1


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None))
