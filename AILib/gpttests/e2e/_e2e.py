"""
Shared body of every test-*.py: the environment, the training / inference steps and the log assertions.

Each test fixes its own GPU usage in its options files (single_gpu / gpu_index / multi_gpu_strategy / pol_device / ref_device),
identically on every machine: nothing here changes how a test runs. The environment makes the GPU kernels repeatable, so the logged
values can be compared exactly with the recorded expected logs. E2E_GPU_COUNT (visible CUDA devices) only lets the designated
multi-GPU tests skip themselves with exit code 2 on a machine with fewer than 2 GPUs. E2E_EXPECTED names the machine whose recorded
logs (expected/<set>/) the run is compared with: run_all_tests.py sets it; a test-*.py run on its own derives it from the GPU model
number (RTX 2080 SUPER -> 2080, RTX 5070 Ti -> 5070). Both are probed in a throwaway interpreter, so this driver process never holds
a CUDA context next to the training runs.
"""
import os
import subprocess
import sys
from pathlib import Path
from typing import Callable, Optional, Union

import _e2e_logcheck
import _e2e_memcheck

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from gpttests.testutil import TestFailed, TestSkipped, run_test

PROMPT = "what is the capital of france?"
NAN_MARKERS = ("train nan", "val nan", "loss : nan", "loss   : nan", "[crash recovery]")
GPU_PROBE = ("import re, torch; n = torch.cuda.device_count(); m = re.search(r'\\d{4}', torch.cuda.get_device_name(0) if n else ''); "
             "print(n, m.group() if m else 'cpu')")

os.environ["AILIB_DETERMINISTIC"] = "1"
os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"


def probe_gpus() -> None:
    """Sets E2E_GPU_COUNT and, unless already given, E2E_EXPECTED (see the module docstring); a no-op when both are already set."""
    if "E2E_GPU_COUNT" not in os.environ or "E2E_EXPECTED" not in os.environ:
        count, derived = subprocess.check_output([sys.executable, "-c", GPU_PROBE], text=True).split()
        os.environ.setdefault("E2E_GPU_COUNT", count)
        os.environ.setdefault("E2E_EXPECTED", derived)


class E2ETest:
    """One end-to-end test of the model folder bin/test-<name>: run(body) wraps the steps that body() issues through the methods below."""

    def __init__(self, name: str, description: str):
        self.model = f"test-{name}"
        self.description = description
        self.model_dir = Path("bin") / self.model  # relative to the repository root, the working directory of every step
        self.log = self.model_dir / "log.txt"
        self.keep = ()

    def run(self, body: Callable[[], None]) -> int:
        """Exit code of the test: 0 passed, 1 failed (a step returned non-zero or an assertion failed), 2 skipped.
        A failed test still cleans its model folder, keeping only log.txt for the diagnosis."""
        probe_gpus()
        code = run_test(f"E2E Test: {self.model}", self.description, body)
        if code == 1:
            self.clean("log.txt", *self.keep)
        return code

    # --- environment ---------------------------------------------------------------------------------------------------------------
    def require_gpus(self, n: int = 2) -> None:
        count = int(os.environ["E2E_GPU_COUNT"])
        if count < n:
            raise TestSkipped(f"{self.model} needs {n} visible CUDA devices, found {count}.")

    def clean(self, *keep: str) -> None:
        """Deletes the files of the model folder except its options / model-params files and those whose name contains a `keep` part,
        plus the token caches (*.tokens.json / *.tokens.npy) next to the data files (the data files themselves stay)."""
        self.keep = keep
        for f in self.model_dir.iterdir():
            if f.is_file() and not any(k in f.name.lower() for k in ("options-", "model-params") + keep):
                f.unlink()
        for f in [f for p in ("*.tokens.json", "*.tokens.npy") for f in self.model_dir.rglob(p)]:
            f.unlink()

    def delete(self, *patterns: str) -> None:
        """Deletes the files of the model folder matching the glob patterns (nothing to delete is fine)."""
        for f in [f for p in patterns for f in self.model_dir.glob(p)]:
            f.unlink()

    # --- steps ----------------------------------------------------------------------------------------------------------------------
    def step(self, title: str, *argv: str, quiet: bool = False) -> None:
        """Prints the step title and runs `python argv...` from the repository root; a non-zero exit code fails the test."""
        print(title)
        if subprocess.call([sys.executable, *argv], stdout=subprocess.DEVNULL if quiet else None) != 0:
            raise TestFailed()

    def train(self, title: str, stage: str, *extra: str) -> None:
        self.step(title, "train.py", "--model_name", self.model, "--training_process", stage, *extra)

    def infer(self, title: str, *extra: str) -> None:
        self.step(title, "infer.py", "--model_name", self.model, "--prompt", PROMPT, *extra)

    def train_rejected(self, title: str, message: str, *args: str) -> None:
        """train.py must reject the arguments at parse time: exit code 2 and `message` in its output."""
        print(title)
        r = subprocess.run([sys.executable, "train.py", "--model_name", self.model, *args], capture_output=True, text=True, errors="replace")
        output = r.stdout + r.stderr
        if r.returncode != 2:
            raise TestFailed(f"[ASSERT] Expected exit code 2 from the argument guard, got {r.returncode}:\n{output}")
        if message not in output:
            raise TestFailed(f'[ASSERT] Guard message "{message}" not found in:\n{output}')

    def memcheck(self, *args: Union[str, int, float, Path]) -> None:
        """One _e2e_memcheck.py check (momentum / gpu0 / losses, see its docstring)."""
        if _e2e_memcheck.main(["_e2e_memcheck.py", *map(str, args)]) != 0:
            raise TestFailed()

    # --- assertions -----------------------------------------------------------------------------------------------------------------
    def fail(self, message: str) -> None:
        raise TestFailed(f"[FAIL] {message}")

    def log_text(self, log: Optional[Path] = None) -> str:
        return (log or self.log).read_text(encoding="utf-8", errors="replace")

    def assert_log(self, *expected: str, log: Optional[Path] = None) -> None:
        """Fails when the log shows a NaN loss or a crash-recovery save, when it differs from the recorded expected log of this
        machine's set (expected/<E2E_EXPECTED>/, see _e2e_logcheck.py), or when any expected literal is missing."""
        log = log or self.log
        if not log.exists():
            raise TestFailed(f"[ASSERT] Log file not found: {log}")
        text = self.log_text(log)
        if any(m in text.lower() for m in NAN_MARKERS):
            raise TestFailed(f"[ASSERT] NaN loss or crash recovery found in {log}")
        if _e2e_logcheck.main(str(log), os.environ.get("E2E_EXPECTED")) != 0:
            raise TestFailed()
        for s in expected:
            if s not in text:
                raise TestFailed(f'[ASSERT] Expected log text not found: "{s}"')
