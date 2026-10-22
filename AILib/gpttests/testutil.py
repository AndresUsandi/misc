# Copyright (c) Sebastian Raschka under Apache License 2.0 (see LICENSE.txt).
# Shared skeleton of every gpttests entry point (what the former .cmd launchers did): the working directory is the repository root,
# so that bin/ and the options files resolve, and the test body runs between an opening banner and a [PASS] / [FAIL] / [SKIP] one.

import os
import sys
import traceback
from pathlib import Path
from typing import Callable, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestFailed(Exception):
    """Raised by a test step or assertion: the message (if any) is printed and the test exits with code 1, without a traceback."""


class TestSkipped(Exception):
    """Raised by a test that cannot run on this machine: exit code 2, which a suite runner counts as skipped."""


def run_test(name: str, description: str, body: Callable[[], Optional[int]]) -> int:
    """Runs body() and returns the process exit code: its return value (None = 0), 1 on any exception, 2 when it raises TestSkipped."""
    os.chdir(REPO_ROOT)
    if hasattr(sys.stdout, "reconfigure"):  # log lines may hold any character; banners stay in order with child output
        sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    print("=" * 60 + f"\nRunning {name} ({description})\n" + "=" * 60)
    try:
        code = body() or 0
    except TestSkipped as e:
        print(f"[SKIP] {e}")
        return 2
    except TestFailed as e:
        if str(e):
            print(e)
        code = 1
    except Exception:
        traceback.print_exc()
        code = 1
    print("=" * 60 + f"\n[{'PASS' if code == 0 else 'FAIL'}] {name}\n" + "=" * 60)
    return code
