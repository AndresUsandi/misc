# Copyright (c) Sebastian Raschka under Apache License 2.0 (see LICENSE.txt).
# Unified DataLoader factory functions for Pretraining, SFT Instruction Tuning, and DPO Preference Optimization.

from pathlib import Path
import sys
from typing import Any, Dict, List, Optional, Tuple, Union

import torch
from torch.utils.data import DataLoader

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from argsutil import TrainingArgs
from gptmodel.Dataset import (
    StreamingTextDataset,
    StreamingInstructionDataset,
    StreamingPreferenceDataset,
    plan_provenance,
    precompute_streaming_steps,
)
from gptio.cache import precompute_dataset_steps
from gptutils.consoleutils import print


def create_training_dataloader(
    all_files: List[Path],
    tokenizer: Any,
    args: TrainingArgs,
    context_length: int,
    device: Optional[Union[str, torch.device]] = None,
) -> Tuple[DataLoader, StreamingTextDataset]:
    """
    Creates streaming DataLoader and StreamingTextDataset for multi-file pretraining.
    """
    if args.precompute_total_steps:
        precompute_dataset_steps(all_files, args, tokenizer=tokenizer)

    dataset = StreamingTextDataset(all_files, tokenizer, args, context_length)
    pin = (device is not None and getattr(device, "type", "") == "cuda") or (isinstance(device, str) and device.startswith("cuda"))
    train_loader = DataLoader(dataset, batch_size=None, pin_memory=pin)
    return train_loader, dataset


def create_instruction_dataloaders(
    data: Union[List[Path], List[str]],
    tokenizer: Any,
    args: TrainingArgs,
    max_length: Optional[int] = None,
    num_workers: int = 0,
    device: Union[str, torch.device] = "cpu",
    prefetch_size: int = 64,
) -> Tuple[DataLoader, DataLoader, List[Dict[str, Any]]]:
    """
    Creates streaming DataLoader instances across multi-file instruction datasets.
    """
    files = [Path(f) for f in data]
    train_ds = StreamingInstructionDataset(files=files, tokenizer=tokenizer, args=args, max_length=max_length, is_train=True, device=device, prefetch_size=prefetch_size)
    if args.precompute_total_steps:
        precompute_streaming_steps(train_ds, "SFT")
    val_ds = StreamingInstructionDataset(files=files, tokenizer=tokenizer, args=args, max_length=max_length, is_train=False, device=device, prefetch_size=prefetch_size)
    pin_mem = (device != "cpu" and torch.cuda.is_available() and num_workers > 0)
    train_loader = DataLoader(train_ds, batch_size=None, pin_memory=pin_mem)
    val_loader = DataLoader(val_ds, batch_size=None, pin_memory=pin_mem)
    print(f"[Streaming Loader] Initialized streaming instruction loader across {len(files)} file(s): ~{len(train_loader):,} train steps, ~{len(val_loader):,} val steps | step plan: {plan_provenance(train_ds)}.")
    return train_loader, val_loader, []


def create_preference_dataloaders(
    data: Union[List[Path], List[str]],
    tokenizer: Any,
    args: TrainingArgs,
    max_length: int = 1024,
    num_workers: int = 0,
    device: Union[str, torch.device] = "cpu",
    prefetch_size: int = 64,
) -> Tuple[DataLoader, DataLoader, List[Dict[str, Any]]]:
    """
    Creates streaming DataLoader instances across multi-file preference datasets.
    """
    files = [Path(f) for f in data]
    train_ds = StreamingPreferenceDataset(files=files, tokenizer=tokenizer, args=args, max_length=max_length, is_train=True, device=device, prefetch_size=prefetch_size)
    if args.precompute_total_steps:
        precompute_streaming_steps(train_ds, "DPO")
    val_ds = StreamingPreferenceDataset(files=files, tokenizer=tokenizer, args=args, max_length=max_length, is_train=False, device=device, prefetch_size=prefetch_size)
    pin_mem = (device != "cpu" and torch.cuda.is_available() and num_workers > 0)
    train_loader = DataLoader(train_ds, batch_size=None, pin_memory=pin_mem)
    val_loader = DataLoader(val_ds, batch_size=None, pin_memory=pin_mem)
    print(f"[Streaming Loader] Initialized streaming preference loader across {len(files)} file(s): ~{len(train_loader):,} train steps, ~{len(val_loader):,} val steps | step plan: {plan_provenance(train_ds)}.")
    return train_loader, val_loader, []
