# Copyright (c) Sebastian Raschka under Apache License 2.0 (see LICENSE.txt).
# Device resolution and PyTorch CUDA allocator memory management.

import os
from pathlib import Path
import sys
from typing import Any, Tuple

import torch

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from argsutil import TrainingArgs
from gptio.pathutil import STAGE_TRAIN, STAGE_OPTIMIZE
from gptutils.consoleutils import print

CUDA_ALLOCATOR_MEMORY_FRACTION: float = 0.95  # allocator cache cap per card (SFT/DPO); the rest is left for driver-level allocations such as kernel loads


def parse_device_spec(dev_val: Any, use_cuda: bool) -> torch.device:
    """Parses a device specifier (int, digit string, device name) into a torch.device."""
    if not use_cuda or dev_val is None:
        return torch.device("cpu")
    if isinstance(dev_val, int):
        return torch.device(f"cuda:{dev_val}")
    s = str(dev_val).strip()
    if s.isdigit():
        return torch.device(f"cuda:{s}")
    return torch.device(s if (s == "cpu" or use_cuda) else "cpu")


def setup_devices_and_allocator(
    args: TrainingArgs,
) -> Tuple[torch.device, torch.device, bool]:
    """
    Resolves compute devices for policy and reference models, applies allocator cache caps,
    and warms up cuBLAS workspaces.
    Returns (device, ref_device, use_cuda).
    """
    stage = args.stage
    use_cuda = torch.cuda.is_available() and (args.device != "cpu")
    if stage == STAGE_OPTIMIZE:
        pol_spec = args.pol_device
        ref_spec = args.ref_device
        if pol_spec is not None:
            device = parse_device_spec(pol_spec, use_cuda)
        elif use_cuda:
            dev_idx = args.gpu_index if (args.gpu_index is not None and args.gpu_index < torch.cuda.device_count()) else 0
            device = torch.device(f"cuda:{dev_idx}")
        else:
            device = torch.device("cpu")

        if ref_spec is not None:
            ref_device = parse_device_spec(ref_spec, use_cuda)
        elif use_cuda and torch.cuda.device_count() > 1 and not args.single_gpu:
            ref_idx = (device.index + 1) % torch.cuda.device_count() if device.index is not None else 1
            ref_device = torch.device(f"cuda:{ref_idx}")
        else:
            ref_device = device
    else:
        if args.device:
            device = parse_device_spec(args.device, use_cuda)
        elif use_cuda:
            dev_idx = args.gpu_index if (args.gpu_index is not None and args.gpu_index < torch.cuda.device_count()) else 0
            device = torch.device(f"cuda:{dev_idx}")
        else:
            device = torch.device("cpu")
        ref_device = device

    # Variable-length SFT/DPO batches fragment the allocator cache: cap cache per card at a fixed fraction. This assignment is the one the
    # allocator reads (it parses the env at first CUDA init, below, so train.py's import-time value only applies to pretraining).
    # expandable_segments (Linux only, ignored with a filtered warning on Windows) lets freed memory be reused across the varying shapes: the 350M
    # SFT on 2 x 16 GB held ~2 GiB of reserved-but-unallocated cache without it and OOMed on the largest batches (Windows paged that to RAM).
    if stage != STAGE_TRAIN and use_cuda:
        os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True,garbage_collection_threshold:0.8"
        for d in (range(torch.cuda.device_count()) if not args.single_gpu else [device.index]):
            free, total = torch.cuda.mem_get_info(d)
            torch.cuda.set_per_process_memory_fraction(CUDA_ALLOCATOR_MEMORY_FRACTION, d)
            print(f"[Memory] cuda:{d}: allocator cache capped at {CUDA_ALLOCATOR_MEMORY_FRACTION * total / 2**30:.2f} GiB of {total / 2**30:.2f} GiB ({(total - free) / 2**30:.2f} GiB already in use as seen by CUDA).")

    # Warm up cuBLAS workspace if using CUDA
    if device.type == "cuda":
        try:
            torch.cuda.set_device(device)
            _ = torch.empty(1, 1, device=device) @ torch.empty(1, 1, device=device)
        except Exception:
            pass

    return device, ref_device, use_cuda
