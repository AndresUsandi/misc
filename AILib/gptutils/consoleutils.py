# Copyright (c) Sebastian Raschka under Apache License 2.0 (see LICENSE.txt).
# Console and terminal UI utilities (progress bars, formatting, telemetry display).

import os
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


_PDH: Any = None  # Windows PDH query for this process's GPU memory (what Task Manager shows): None = not opened yet, False = unavailable


def _process_gpu_bytes() -> Optional[int]:
    """Dedicated GPU memory of this process as the OS accounts it, summed over adapters: torch's pool plus what torch's counters never see
    (CUDA context, cuBLAS/cuDNN workspaces, compiled kernels). Windows: the 'GPU Process Memory' performance counters (Task Manager's
    'Dedicated GPU memory'); elsewhere NVML per-process usage (needs pynvml). None when unavailable."""
    global _PDH
    if _PDH is False:
        return None
    try:
        if sys.platform == "win32":
            import ctypes
            pdh = ctypes.windll.pdh
            if _PDH is None:
                q, c = ctypes.c_void_p(), ctypes.c_void_p()
                if pdh.PdhOpenQueryW(None, 0, ctypes.byref(q)) or pdh.PdhAddEnglishCounterW(q, f"\\GPU Process Memory(pid_{os.getpid()}_*)\\Dedicated Usage", 0, ctypes.byref(c)):
                    return None
                _PDH = (q, c)
            q, c = _PDH
            size, count = ctypes.c_ulong(0), ctypes.c_ulong(0)
            if pdh.PdhCollectQueryData(q):
                return None
            pdh.PdhGetFormattedCounterArrayW(c, 0x400, ctypes.byref(size), ctypes.byref(count), None)  # PDH_FMT_LARGE; sizes the buffer
            buf = ctypes.create_string_buffer(max(1, size.value))
            if pdh.PdhGetFormattedCounterArrayW(c, 0x400, ctypes.byref(size), ctypes.byref(count), buf):
                return None

            class Item(ctypes.Structure):  # PDH_FMT_COUNTERVALUE_ITEM_W: name pointer, status, 64-bit value (one per adapter instance)
                _fields_ = [("name", ctypes.c_wchar_p), ("status", ctypes.c_ulong), ("value", ctypes.c_longlong)]
            items = ctypes.cast(buf, ctypes.POINTER(Item))
            return sum(items[i].value for i in range(count.value))
        import pynvml
        pynvml.nvmlInit()
        pid = os.getpid()
        return sum(p.usedGpuMemory or 0 for i in range(pynvml.nvmlDeviceGetCount()) for p in pynvml.nvmlDeviceGetComputeRunningProcesses(pynvml.nvmlDeviceGetHandleByIndex(i)) if p.pid == pid)
    except Exception:
        _PDH = False
        return None


def _bytes_per_device(tensors: Any) -> dict:
    """Sums tensor storage bytes per CUDA device index (torchao 8-bit optimizer states count their int8 codes and scales, not the dequantized view)."""
    out: dict = {}
    for t in tensors:
        if t is not None and t.is_cuda:
            inner = [getattr(t, a) for a in ("codes", "scale", "qmap") if torch.is_tensor(getattr(t, a, None))]
            out[t.device.index] = out.get(t.device.index, 0) + sum(x.numel() * x.element_size() for x in (inner or [t]))
    return out


def format_vram_report(model: Any = None, optimizer: Any = None, device: Optional[Any] = None) -> str:
    """One '[VRAM cuda:N]' line per CUDA device this process has used (empty on CPU), each with: the peak torch allocated since the previous report (the
    counter is reset afterwards) split into weights (+buffers), gradients, optimizer state and the rest (activations, autocast weight copies,
    loss chunks, temporaries; what the batch costs); the current allocation; the allocator's reserved pool and its unused part (fragmentation
    and headroom kept for reuse); the process total the OS sees (see _process_gpu_bytes; one figure, all adapters); the device's total use incl.
    other processes; and how often the allocator had to free cached blocks and retry (memory pressure). Weights/grads/optimizer need the model
    and optimizer(s); without them those parts read 0 and 'other' is the whole peak. 'grads' is the room the gradients take while they exist
    (one gradient per trainable tensor on the device, plus the DP wrappers' fp32 accumulators), not what happens to be alive at this instant:
    gradients live only between a backward and the following zero_grad, and the evaluations run on either side of it depending on the stage."""
    if not torch.cuda.is_available() or str(device) == "cpu":
        return ""
    GB = 1024 ** 3
    opts = optimizer if isinstance(optimizer, list) else [optimizer] if optimizer is not None else []
    # The multi-GPU wrappers' parameters() cover only the fp32 masters (DP) or the shards (ZeRO-1): the compute copies on every GPU
    # (raw_replicas) and the fp32 gradient accumulators of the copies (_grad_bufs) are reached explicitly, deduplicated by identity
    mods = [m for m in [model, getattr(model, "raw_model", None)] + list(getattr(model, "raw_replicas", None) or []) if m is not None]
    params = list({id(p): p for m in mods for p in m.parameters()}.values())
    weights = _bytes_per_device(params + list({id(b): b for m in mods for b in m.buffers()}.values()))
    grads = _bytes_per_device([p for p in params if p.requires_grad] + [g for bufs in getattr(model, "_grad_bufs", None) or [] for g in bufs])
    optim = _bytes_per_device(v for o in opts for st in o.state.values() for v in st.values() if torch.is_tensor(v))
    proc = _process_gpu_bytes()
    lines = []
    # devices this process never used (single-GPU run on a multi-GPU machine) are left out: nothing to report, and mem_get_info would create a CUDA context on them
    active = [d for d in range(torch.cuda.device_count()) if torch.cuda.max_memory_allocated(d) or torch.cuda.memory_allocated(d) or torch.cuda.memory_reserved(d)]
    for d in active:
        peak, now, reserved = torch.cuda.max_memory_allocated(d), torch.cuda.memory_allocated(d), torch.cuda.memory_reserved(d)
        torch.cuda.reset_peak_memory_stats(d)
        free, total = torch.cuda.mem_get_info(d)
        static = weights.get(d, 0) + grads.get(d, 0) + optim.get(d, 0)
        used = total - free
        others = f" (others {max(0, used - proc) / GB:.2f})" if proc is not None and len(active) == 1 else ""  # the process figure spans all GPUs it uses, so 'others' is only well-defined when that is one
        lines.append(f"[VRAM cuda:{d}] peak {peak / GB:.3f} GB = weights {weights.get(d, 0) / GB:.3f} + grads {grads.get(d, 0) / GB:.3f} + optim {optim.get(d, 0) / GB:.3f} + other {max(0, peak - static) / GB:.3f}"
                     f" | now {now / GB:.3f} | reserved {reserved / GB:.3f} (unused {(reserved - now) / GB:.3f}) | process {'n/a' if proc is None else f'{proc / GB:.2f}'}"
                     f" | device {used / GB:.2f}/{total / GB:.2f} used{others} | alloc retries {torch.cuda.memory_stats(d).get('num_alloc_retries', 0)}")
    return "\n".join(lines)


def print_gpu_memory_breakdown(model: Any = None, optimizer: Any = None) -> None:
    """Prints the per-GPU memory report line(s) (see format_vram_report)."""
    for line in format_vram_report(model, optimizer).splitlines():
        print(line)  # one print per device line so each gets its own timestamp


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
    train_chosen: Optional[float] = None,
    val_chosen: Optional[float] = None,
) -> None:
    """Prints standard step telemetry log to console and log file."""
    step_pct = round(100.0 * step / total_steps) if total_steps and total_steps > 0 else 0
    global_pct = round(100.0 * global_step / global_total_steps) if global_total_steps and global_total_steps > 0 else 0

    if vram_str is None:
        vram_str = format_vram_report(device=device)

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
        if train_chosen is not None and val_chosen is not None:  # DPO: mean per-token log-prob of the chosen answers, policy minus reference. Falling well below 0 = the model is losing the answers themselves
            metric_str += f"Chosen vs ref: Tr {train_chosen:+.3f}, Val {val_chosen:+.3f} | "
    else:
        metric_str = ""

    tail = (
        f"Step tok/sec: {round(tps):,}, Avg tok/sec: {round(avg_tps):,} | "
        f"Eval: {eval_duration:.2f}s | "
        f"LR: {lr:.{lr_precision}f}"
    )

    print(f"{header}{loss_str}{metric_str}{tail}")
    for line in (vram_str or "").splitlines():
        print(line)  # the memory report goes on its own line per device (each timestamped), see format_vram_report


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

