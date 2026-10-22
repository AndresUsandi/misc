"""
Memory-side assertions for the e2e tests of the VRAM options (test-muon-bf16, test-autocast-cache). Exit code 0 on success, 1 on failure.

  python _e2e_memcheck.py momentum <checkpoint.chk> <bfloat16|float32>
      Every CustomMuon momentum buffer saved in the checkpoint has the given dtype (and there is at least one).

  python _e2e_memcheck.py gpu0 <log.txt> <runA> <runB> <peak|now|reserved|weights|grads|optim|other> <min_drop_gb>
      The log holds several training invocations ("runs"), numbered from 1 in order of appearance; each one starts with its
      "Device: cuda..." header line (parse-only invocations that fail in argparse have no header and do not count). Takes the
      largest value of the named field over the "[VRAM cuda:0] ..." report lines (format_vram_report, printed with every evaluation
      and at every completed epoch) of runA and runB and requires max(runA) - max(runB) >= min_drop_gb.

  python _e2e_memcheck.py losses <log.txt> <runA> <runB> <abs_tol>
      The "Train x.xxx, Val y.yyy" evaluation lines of runA and runB match pairwise: same count, every value within abs_tol or 1%.
"""
import re
import sys
from pathlib import Path

RUN_HEADER = re.compile(r"Device: cuda")
GPU0 = re.compile(r"^(?:\[.*?\] )?\[VRAM cuda:0\] ")
LOSSES = re.compile(r"Train ([\d.]+), Val ([\d.]+)")


def runs(log_path):
    """Splits the log into training invocations: list of line lists, one per 'Device: cuda' header."""
    out = []
    for line in Path(log_path).read_text(encoding="utf-8", errors="replace").splitlines():
        if RUN_HEADER.search(line):
            out.append([])
        if out:
            out[-1].append(line)
    return out


def check_momentum(chk_path, dtype_name):
    import torch
    ckpt = torch.load(chk_path, map_location="cpu", weights_only=False)
    opt_state = ckpt.get("optimizer_state_dict")
    states = opt_state if isinstance(opt_state, (list, tuple)) else [opt_state]
    bufs = [v for s in states if isinstance(s, dict) for p in s.get("state", {}).values() for k, v in p.items() if k == "momentum_buffer"]
    if not bufs:
        print(f"[MEMCHECK] No Muon momentum buffers found in {chk_path}")
        return 1
    dtypes = {str(b.dtype).replace("torch.", "") for b in bufs}
    mib = sum(b.numel() * b.element_size() for b in bufs) / 2**20
    if dtypes != {dtype_name}:
        print(f"[MEMCHECK] Muon momentum buffers in {Path(chk_path).name} are {sorted(dtypes)}, expected {dtype_name}")
        return 1
    print(f"[MEMCHECK] {len(bufs)} Muon momentum buffers in {Path(chk_path).name} are {dtype_name} ({mib:.1f} MiB)")
    return 0


def check_gpu0(log_path, run_a, run_b, what, min_drop):
    all_runs = runs(log_path)
    try:
        a, b = all_runs[run_a - 1], all_runs[run_b - 1]
    except IndexError:
        print(f"[MEMCHECK] {log_path} holds {len(all_runs)} training run(s); runs {run_a} and {run_b} requested")
        return 1
    field = re.compile(rf"\b{what} ([\d.]+)")
    peak = lambda lines: max((float(m.group(1)) for l in lines if GPU0.match(l) for m in [field.search(l)] if m), default=None)
    pa, pb = peak(a), peak(b)
    if pa is None or pb is None:
        print(f"[MEMCHECK] No '[VRAM cuda:0]' line with a '{what}' field in run {run_a if pa is None else run_b} of {log_path}")
        return 1
    drop = pa - pb
    label = what
    if drop < min_drop:
        print(f"[MEMCHECK] GPU 0 {label} VRAM: run {run_a} {pa:.3f} GB vs run {run_b} {pb:.3f} GB, drop {drop:+.3f} GB < required {min_drop:.3f} GB")
        return 1
    print(f"[MEMCHECK] GPU 0 {label} VRAM: run {run_a} {pa:.3f} GB -> run {run_b} {pb:.3f} GB (saves {drop:.3f} GB, required >= {min_drop:.3f})")
    return 0


def check_losses(log_path, run_a, run_b, abs_tol):
    all_runs = runs(log_path)
    try:
        a, b = all_runs[run_a - 1], all_runs[run_b - 1]
    except IndexError:
        print(f"[MEMCHECK] {log_path} holds {len(all_runs)} training run(s); runs {run_a} and {run_b} requested")
        return 1
    la = [(float(m.group(1)), float(m.group(2))) for m in map(LOSSES.search, a) if m]
    lb = [(float(m.group(1)), float(m.group(2))) for m in map(LOSSES.search, b) if m]
    if not la or len(la) != len(lb):
        print(f"[MEMCHECK] Loss lines: run {run_a} has {len(la)}, run {run_b} has {len(lb)}")
        return 1
    worst = max(abs(x - y) for pa, pb in zip(la, lb) for x, y in zip(pa, pb))
    bad = [(pa, pb) for pa, pb in zip(la, lb) if any(abs(x - y) > max(abs_tol, 0.01 * abs(x)) for x, y in zip(pa, pb))]
    if bad:
        print(f"[MEMCHECK] Losses of run {run_a} and run {run_b} differ beyond {abs_tol} (or 1%): {bad[:5]}")
        return 1
    print(f"[MEMCHECK] {len(la)} evaluation lines of run {run_a} and run {run_b} agree (largest train/val difference {worst:.4f}, tolerance {abs_tol})")
    return 0


def main(argv):
    cmd = argv[1] if len(argv) > 1 else ""
    if cmd == "momentum" and len(argv) == 4:
        return check_momentum(argv[2], argv[3])
    if cmd == "gpu0" and len(argv) == 7:
        return check_gpu0(argv[2], int(argv[3]), int(argv[4]), argv[5], float(argv[6]))
    if cmd == "losses" and len(argv) == 6:
        return check_losses(argv[2], int(argv[3]), int(argv[4]), float(argv[5]))
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main(sys.argv))
