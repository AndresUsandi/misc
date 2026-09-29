# Copyright (c) Sebastian Raschka under Apache License 2.0 (see LICENSE.txt).
# Console and terminal UI utilities (progress bars, formatting, telemetry display).

import sys
import shutil
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, Tuple, Union

import torch

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from gptutils.loggingutil import write_to_log

class SimpleProgressBar:
    """
    Lightweight, self-contained single-line in-place console progress bar.
    Operates without external dependencies, writing carriage-return (\r) updates directly to sys.stdout.
    """
    def __init__(
        self,
        total: int = 0,
        desc: str = "",
        unit: str = "it",
        unit_scale: bool = False,
        mininterval: float = 0.1,
    ):
        self.total = total
        self.desc = desc
        self.unit = unit
        self.unit_scale = unit_scale
        self.mininterval = mininterval
        self.n = 0
        self.start_time = time.time()
        self.last_print = 0.0

    def update(self, n: int = 1) -> None:
        self.n += n
        now = time.time()
        if now - self.last_print >= self.mininterval or (self.total and self.n >= self.total):
            self.last_print = now
            elapsed = max(now - self.start_time, 1e-6)
            rate = self.n / elapsed
            pct = min(100.0, (self.n / self.total * 100.0)) if self.total and self.total > 0 else 0.0
            if self.unit_scale and self.unit == "iB":
                n_mb = self.n / (1024 * 1024)
                rate_mb = rate / (1024 * 1024)
                if self.total and self.total > 0:
                    tot_mb = self.total / (1024 * 1024)
                    eta = max(0.0, (self.total - self.n) / rate) if rate > 0 else 0
                    msg = f"{self.desc}: {pct:5.1f}% | {n_mb:6.1f}/{tot_mb:6.1f} MB | {rate_mb:5.1f} MB/s | ETA: {eta:4.0f}s"
                else:
                    msg = f"{self.desc}: {n_mb:6.1f} MB | {rate_mb:5.1f} MB/s [{elapsed:.1f}s]"
            else:
                if self.total and self.total > 0:
                    msg = f"{self.desc}: {pct:5.1f}% | {self.n}/{self.total} [{elapsed:.1f}s, {rate:.1f} {self.unit}/s]"
                else:
                    msg = f"{self.desc}: {self.n} {self.unit} [{elapsed:.1f}s, {rate:.1f} {self.unit}/s]"
            try:
                cols = max(shutil.get_terminal_size((80, 20)).columns - 1, 80)
            except Exception:
                cols = 80
            pad = max(cols - len(msg), 0)
            sys.stdout.write(f"\r{msg}{' ' * pad}\x1b[K")
            sys.stdout.flush()

    def write(self, msg: str) -> None:
        """Prints a message cleanly above or clearing the progress bar line."""
        sys.stdout.write(f"\r{' ' * 80}\r{msg}\n")
        sys.stdout.flush()

    def close(self) -> None:
        sys.stdout.write("\n")
        sys.stdout.flush()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def create_progress_bar(
    total: Optional[Union[int, float]] = None,
    desc: str = "",
    unit: str = "it",
    unit_scale: bool = False,
    leave: bool = True,
    mininterval: float = 0.1,
) -> Any:
    """
    Creates a robust progress bar configured to cleanly update in-place on a single line
    across Windows Terminal, VS Code integrated terminal, PowerShell, and Unix shells.
    Prevents cursor-wrap newline explosion by:
    1. Directing output to sys.stdout (avoiding PowerShell stderr newline handling).
    2. Capping bar width ({bar:25}) so total line length stays safely under 75 columns.
    3. Enabling dynamic_ncols=True to track terminal width.
    Falls back to SimpleProgressBar if tqdm is not installed.
    """
    try:
        from tqdm import tqdm
        try:
            from tqdm.std import disp_len
        except ImportError:
            disp_len = len

        class _CustomTqdm(tqdm):
            @classmethod
            def format_meter(cls, n, total, elapsed, ncols=None, prefix="", ascii=False, unit="it", unit_scale=False, rate=None, bar_format=None, postfix=None, unit_divisor=1000, initial=0, colour=None, **extra_kwargs):
                if not bar_format:
                    if total and total > 0:
                        bar_format = "{desc}: {percentage:3.0f}%|{bar:25}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]"
                    else:
                        bar_format = "{desc}: {n_fmt} {unit} [{elapsed}, {rate_fmt}]"
                return super().format_meter(
                    n, total, elapsed, ncols=ncols, prefix=prefix, ascii=ascii, unit=unit,
                    unit_scale=unit_scale, rate=rate, bar_format=bar_format, postfix=postfix,
                    unit_divisor=unit_divisor, initial=initial, colour=colour, **extra_kwargs
                )

            @staticmethod
            def status_printer(file):
                fp = file
                fp_flush = getattr(fp, "flush", lambda: None)
                if fp in (sys.stderr, sys.stdout):
                    getattr(sys.stderr, "flush", lambda: None)()
                    getattr(sys.stdout, "flush", lambda: None)()

                def fp_write(s):
                    fp.write(str(s))
                    fp_flush()

                def print_status(s):
                    try:
                        cols = max(shutil.get_terminal_size((80, 20)).columns - 1, 80)
                    except Exception:
                        cols = 80
                    len_s = disp_len(s)
                    pad = max(cols - len_s, 0)
                    fp_write("\r" + s + (" " * pad) + "\x1b[K")

                return print_status

        return _CustomTqdm(
            total=int(total) if total is not None else None,
            desc=desc,
            unit=unit,
            unit_scale=unit_scale,
            file=sys.stdout,
            dynamic_ncols=True,
            leave=leave,
            mininterval=mininterval,
        )
    except (ImportError, Exception):
        return SimpleProgressBar(
            total=int(total) if total is not None else 0,
            desc=desc,
            unit=unit,
            unit_scale=unit_scale,
            mininterval=mininterval,
        )

_builtin_print = print
_at_start_of_line = True

def print_with_timestamp(*args: Any, **kwargs: Any) -> None:
    """
    Timestamped print function. Automatically prepends the current timestamp [YYYY-MM-DD HH:MM:SS],
    defaults flush=True for real-time console streaming, and writes to [base_dir]/[model_name]/log.txt.
    """
    global _at_start_of_line

    if "flush" not in kwargs:
        kwargs["flush"] = True

    sep = kwargs.get("sep", " ")
    end = kwargs.get("end", "\n")
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if not args:
        _builtin_print(**kwargs)
        write_to_log(end)
        _at_start_of_line = str(end).endswith("\n")
        return

    # Check if we should prepend a timestamp
    if _at_start_of_line:
        if isinstance(args[0], str):
            first = args[0]
            if first.startswith("\n"):
                lead_nl = len(first) - len(first.lstrip("\n"))
                formatted_first = f"{first[:lead_nl]}[{now_str}] {first[lead_nl:]}"
            else:
                formatted_first = f"[{now_str}] {first}"
            out_args = (formatted_first,) + args[1:]
        else:
            out_args = (f"[{now_str}]",) + args
    else:
        out_args = args

    # Print to console
    _builtin_print(*out_args, **kwargs)

    # Write to log file
    log_text = sep.join(str(a) for a in out_args) + str(end)
    write_to_log(log_text)

    # Track line boundary
    _at_start_of_line = str(end).endswith("\n") or (str(out_args[-1]).endswith("\n") if out_args else False)


# Aliases for backwards compatibility and ease of import
print_with_timestap = print_with_timestamp
tprint = print_with_timestamp
print = print_with_timestamp


def format_vram_str(device: Optional[Any] = None) -> str:
    """Formats VRAM allocation string for single or multi-GPU setups."""
    if not torch.cuda.is_available() or str(device) == "cpu":
        return ""
    if torch.cuda.device_count() > 1:
        vram_parts = [
            f"cuda:{d}: {torch.cuda.memory_allocated(d) / (1024**3):.1f}G"
            for d in range(torch.cuda.device_count())
        ]
        return f" | VRAM: [{', '.join(vram_parts)}]"
    else:
        d = device if device is not None else 0
        vram_alloc = torch.cuda.memory_allocated(d) / (1024 ** 3)
        vram_res = torch.cuda.memory_reserved(d) / (1024 ** 3)
        return f" | VRAM: {vram_alloc:.2f}G/{vram_res:.2f}G"


def print_gpu_memory_breakdown() -> None:
    """Prints per-GPU allocated and reserved VRAM breakdown."""
    if not torch.cuda.is_available():
        return
    mem_info = []
    for d_idx in range(torch.cuda.device_count()):
        alloc = torch.cuda.memory_allocated(d_idx) / (1024 ** 3)
        res = torch.cuda.memory_reserved(d_idx) / (1024 ** 3)
        dev_name = torch.cuda.get_device_name(d_idx)
        mem_info.append(f"GPU {d_idx} ({dev_name}): {alloc:.3f} GB Alloc / {res:.3f} GB Res")
    print(" | ".join(mem_info))


def format_elapsed_time(seconds: float) -> str:
    """Formats seconds into human-readable duration (e.g. '1d 4h 12m 30s', '1h 23m 45s' or '12m 34s (754.21s)')."""
    sec_int = max(0, int(seconds))
    days, rem = divmod(sec_int, 86400)
    hours, rem = divmod(rem, 3600)
    mins, secs = divmod(rem, 60)
    if days > 0:
        return f"{days}d {hours}h {mins}m {secs}s"
    if hours > 0:
        return f"{hours}h {mins}m {secs}s"
    return f"{mins}m {secs}s ({seconds:.2f}s)"


def print_step_telemetry(
    epoch: int,
    num_epochs: int,
    step: int,
    total_steps: int,
    global_step: int,
    global_total_steps: int,
    train_loss: float,
    val_loss: float,
    tps: float,
    avg_tps: float,
    eval_duration: float,
    lr: float,
    vram_str: Optional[str] = None,
    device: Optional[Any] = None,
    val_ppl: Optional[float] = None,
    train_margin: Optional[float] = None,
    val_margin: Optional[float] = None,
    train_acc: Optional[float] = None,
    val_acc: Optional[float] = None,
    lr_precision: int = 6,
    val_seq_loss: Optional[float] = None,
    val_seq_ppl: Optional[float] = None,
) -> None:
    """Prints standard step telemetry log to console and log file."""
    step_pct = round(100.0 * step / total_steps) if total_steps and total_steps > 0 else 0
    global_pct = round(100.0 * global_step / global_total_steps) if global_total_steps and global_total_steps > 0 else 0

    if vram_str is None:
        vram_str = format_vram_str(device)

    header = f"Ep {epoch+1}/{num_epochs} (Step {step:06d}/{total_steps:06d} - {step_pct}% | Global {global_step:06d}/{global_total_steps:06d} - {global_pct}%): "
    if val_seq_loss is not None:
        loss_str = f"Train {train_loss:.3f}, Val {val_loss:.3f} (Seq {val_seq_loss:.3f}) | "
    else:
        loss_str = f"Train {train_loss:.3f}, Val {val_loss:.3f} | "

    if val_ppl is not None:
        if val_seq_ppl is not None:
            metric_str = f"PPL: {val_ppl:.2f} (Seq {val_seq_ppl:.2f}) | "
        else:
            metric_str = f"PPL: {val_ppl:.2f} | "
    elif train_margin is not None and val_margin is not None and train_acc is not None and val_acc is not None:
        metric_str = f"Margin: Tr {train_margin:+.3f}, Val {val_margin:+.3f} | Acc: Tr {train_acc * 100:.1f}%, Val {val_acc * 100:.1f}% | "
    else:
        metric_str = ""

    tail = (
        f"Step tok/sec: {round(tps):,}, Avg tok/sec: {round(avg_tps):,} | "
        f"Eval: {eval_duration:.2f}s | "
        f"LR: {lr:.{lr_precision}f}{vram_str}"
    )

    print(f"{header}{loss_str}{metric_str}{tail}")


def str_to_bool(v: Any) -> bool:
    if isinstance(v, bool):
        return v
    if str(v).lower() in ("yes", "true", "t", "y", "1"):
        return True
    elif str(v).lower() in ("no", "false", "f", "n", "0"):
        return False
    return True


def convert_time(seconds: float) -> Tuple[int, int, int]:
    """Converts seconds into hours, minutes, and seconds."""
    hours, rem = divmod(int(seconds), 3600)
    minutes, seconds_int = divmod(rem, 60)
    return hours, minutes, seconds_int


def print_eta(start_time: float, book_start_time: float, index: int, total_files: int) -> None:
    """Prints elapsed time and remaining ETA metrics across multi-file corpus training."""
    book_end_time = time.time()
    elapsed_time = book_end_time - book_start_time
    total_elapsed_time = book_end_time - start_time
    books_remaining = total_files - index
    average_time_per_book = total_elapsed_time / index if index > 0 else 0.0
    eta = average_time_per_book * books_remaining

    book_h, book_m, book_s = convert_time(elapsed_time)
    total_h, total_m, total_s = convert_time(total_elapsed_time)
    eta_h, eta_m, eta_s = convert_time(eta)

    print(f"File processed: {book_h}h {book_m}m {book_s}s | "
          f"Total elapsed: {total_h}h {total_m}m {total_s}s | "
          f"ETA for remaining files: {eta_h}h {eta_m}m {eta_s}s")

