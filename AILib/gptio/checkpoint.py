# Copyright (c) Sebastian Raschka under Apache License 2.0 (see LICENSE.txt).
# Checkpoint Saving, Loading, and State Restoration for GPT Models.

import gc
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import torch
import torch.nn as nn

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from argsutil import ModelArgs
from gptutils.consoleutils import print
from gptutils.processutil import get_locking_processes
from gptio.modelio import (
    _unwrap_model,
    _clean_state_dict_keys,
)
from gptio.pathutil import (
    resolve_path,
    resolve_checkpoint_candidates,
    TARGET_ROOT,
    TARGET_CHECKPOINT,
    STAGE_TRAIN,
    STAGE_TUNE,
    STAGE_OPTIMIZE,
    CHECKPOINT_EXT,
    CHECKPOINT_TRN_EXT,
    CHECKPOINT_SFT_EXT,
    CHECKPOINT_DPO_EXT,
    CHECKPOINT_TMP_SUFFIX,
    CHECKPOINT_SWAP_SUFFIX,
    CHECKPOINT_BAK_SUFFIX,
    MODEL_EXT,
    MODEL_ALT_EXT,
)

DEFAULT_SAVE_TIMEOUT_SECONDS: float = 600.0
SAVE_RETRY_INTERVAL_SECONDS: float = 1.0
SAVE_LOG_INTERVAL_SECONDS: float = 10.0
CHECKPOINT_TMP_PREFIX: str = "."

def atomic_replace_with_retry(src_path: Path, dst_path: Path, timeout_seconds: float = DEFAULT_SAVE_TIMEOUT_SECONDS) -> None:
    """
    Replaces dst_path with src_path atomically.
    If dst_path or src_path is locked:
      - If locked by a DIFFERENT process (PID != os.getpid()): errors out immediately with RuntimeError.
      - If locked ONLY by the current process (PID == os.getpid()) or transient OS lock:
        waits and retries with periodic gc.collect() until released or timeout_seconds elapses.
    """
    start_time = time.time()
    my_pid = os.getpid()
    last_log_time = 0.0

    while True:
        try:
            os.replace(str(src_path), str(dst_path))
            return
        except (PermissionError, OSError) as exc:
            src_locks = get_locking_processes(src_path)
            dst_locks = get_locking_processes(dst_path)
            all_locks = list(dict.fromkeys(src_locks + dst_locks))

            other_procs = [p for p in all_locks if p[0] != my_pid]
            if other_procs:
                proc_desc = ", ".join([f"PID {p[0]} ({p[1]})" for p in other_procs])
                raise RuntimeError(
                    f"Checkpoint file '{dst_path}' cannot be saved because it is being used by a different process: {proc_desc}. "
                    f"Aborting immediately."
                ) from exc

            elapsed = time.time() - start_time
            if elapsed >= timeout_seconds:
                raise TimeoutError(
                    f"Checkpoint file '{dst_path}' could not be replaced after waiting {elapsed:.1f}s (timeout={timeout_seconds:.1f}s). "
                    f"File remains held by current process (PID {my_pid})."
                ) from exc

            now = time.time()
            if now - last_log_time >= SAVE_LOG_INTERVAL_SECONDS:
                print(f"[checkpoint] Checkpoint file '{dst_path}' is currently in use by current process (PID {my_pid}). Waiting for release... ({elapsed:.1f}s / {timeout_seconds:.1f}s)")
                last_log_time = now

            gc.collect()
            time.sleep(SAVE_RETRY_INTERVAL_SECONDS)


def save_checkpoint(
    model: nn.Module,
    args: ModelArgs,
    config: Optional[Dict[str, Any]] = None,
    optimizer: Optional[Union[torch.optim.Optimizer, List[torch.optim.Optimizer]]] = None,
    global_step: int = 0,
    epoch: int = 0,
    current_epoch: Optional[int] = None,
    current_file_idx: int = 1,
    step_in_file: int = 0,
    step_in_epoch: int = 0,
    epoch_completed: bool = False,
    tokens_seen: int = 0,
    train_losses: Optional[List[float]] = None,
    val_losses: Optional[List[float]] = None,
    track_tokens: Optional[List[int]] = None,
    stage: str = "train",
    is_sft: bool = False,
    is_dpo: bool = False,
    accumulated_training_time: float = 0.0,
    save_timeout: float = 600.0,
) -> str:
    """
    Unified, crash-proof checkpoint saver for pretraining, instruction fine-tuning, and DPO optimization.
    Saves full training state (model weights, optimizer state, scheduler, step/epoch progress) to a checkpoint file (.trn.chk, .sft.chk, .dpo.chk).
    Path and filename resolution is strictly internal: [models_dir]/[model_name]/[model_name].[stage].chk
    """
    if not args.model_name:
        raise ValueError("save_checkpoint requires 'model_name' to be specified.")

    unwrapped = _unwrap_model(model)

    # Determine configuration
    model_config = config
    if model_config is None and hasattr(unwrapped, "config") and isinstance(unwrapped.config, dict):
        model_config = unwrapped.config
    elif model_config is None:
        model_config = {
            "vocab_size": getattr(unwrapped, "tok_emb", nn.Embedding(50257, 768)).num_embeddings if hasattr(unwrapped, "tok_emb") else 50257,
            "emb_dim": getattr(unwrapped, "tok_emb", nn.Embedding(50257, 768)).embedding_dim if hasattr(unwrapped, "tok_emb") else 768,
            "n_layers": len(unwrapped.trf_blocks) if hasattr(unwrapped, "trf_blocks") else 12,
        }

    # Infer stage flags
    stage_val = stage
    if is_sft or stage_val in (STAGE_TUNE, "sft"):
        is_sft = True
        stage_val = STAGE_TUNE
    elif is_dpo or stage_val in (STAGE_OPTIMIZE, "dpo"):
        is_dpo = True
        stage_val = STAGE_OPTIMIZE
    else:
        stage_val = STAGE_TRAIN

    target_dir = resolve_path(args.model_name, target=TARGET_ROOT, models_dir=args.models_base_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    target_file = resolve_path(args.model_name, target=TARGET_CHECKPOINT, stage=stage_val, models_dir=args.models_base_dir)
    backup_file = resolve_path(args.model_name, target=TARGET_CHECKPOINT, stage=stage_val, suffix=CHECKPOINT_TMP_SUFFIX, models_dir=args.models_base_dir)
    tmp2_file = resolve_path(args.model_name, target=TARGET_CHECKPOINT, stage=stage_val, suffix=CHECKPOINT_SWAP_SUFFIX, models_dir=args.models_base_dir)

    raw_state_dict = unwrapped.state_dict()
    cpu_state_dict = {k: v.cpu() if isinstance(v, torch.Tensor) else v for k, v in raw_state_dict.items()}

    checkpoint_dict: Dict[str, Any] = {
        "model_state_dict": cpu_state_dict,
        "config": model_config,
        "global_step": global_step,
        "epoch": epoch,
        "current_epoch": current_epoch if current_epoch is not None else epoch,
        "current_file_idx": current_file_idx,
        "step_in_file": step_in_file,
        "step_in_epoch": step_in_epoch,
        "epoch_completed": epoch_completed,
        "tokens_seen": tokens_seen,
        "train_losses": train_losses if train_losses is not None else [],
        "val_losses": val_losses if val_losses is not None else [],
        "track_tokens": track_tokens if track_tokens is not None else [],
        "stage": stage_val,
        "is_sft": is_sft,
        "is_dpo": is_dpo,
        "accumulated_training_time": float(accumulated_training_time),
    }

    if optimizer is not None:
        if isinstance(optimizer, (list, tuple)):
            checkpoint_dict["optimizer_state_dict"] = [opt.state_dict() for opt in optimizer]
        else:
            checkpoint_dict["optimizer_state_dict"] = optimizer.state_dict()

    # Step 1: Write checkpoint to the swap file (.tmp2) with 3 retries
    max_write_attempts = 3
    write_success = False
    last_write_err = None
    for attempt in range(1, max_write_attempts + 1):
        try:
            torch.save(checkpoint_dict, str(tmp2_file))
            write_success = True
            break
        except Exception as e:
            last_write_err = e
            print(f"[Checkpoint Warning] Attempt {attempt}/{max_write_attempts} failed to write '{tmp2_file.name}': {e}")
            time.sleep(1.0)

    if not write_success:
        raise RuntimeError(f"Failed to write checkpoint to '{tmp2_file.name}' after {max_write_attempts} attempts: {last_write_err}")

    # Step 2: Keep the previous checkpoint as the backup (.tmp) and swap the new file in atomically (two renames instead of a full copy)
    if target_file.exists():
        atomic_replace_with_retry(target_file, backup_file, timeout_seconds=save_timeout)
    atomic_replace_with_retry(tmp2_file, target_file, timeout_seconds=save_timeout)

    step_info = f" (Step {global_step})" if global_step > 0 else ""
    print(f"[gptio] Saved {stage_val.upper()} checkpoint{step_info} to: {target_file}")
    return str(target_file)


def load_checkpoint(
    args: ModelArgs,
    stage: str = "train",
    device: Optional[Union[str, torch.device]] = None,
    silent: bool = False,
) -> Optional[Dict[str, Any]]:
    """
    Unified checkpoint loader for pretraining, fine-tuning, and DPO optimization.
    Loads checkpoint for the given model_name from disk with device mapping and automatic fallback to backups (.tmp / .bak).
    Path resolution is strictly internal to gptio. Callers only provide model_name.
    """
    if not args.model_name:
        return None

    map_loc = device if device is not None else "cpu"
    paths_to_try = resolve_checkpoint_candidates(args.model_name, stage=stage, models_dir=args.models_base_dir)

    if not paths_to_try:
        if silent:
            return None
        target_dir = resolve_path(args.model_name, target=TARGET_ROOT, models_dir=args.models_base_dir)
        raise FileNotFoundError(f"No checkpoint found for model '{args.model_name}' in '{target_dir}'.")

    last_exc = None
    for target in paths_to_try:
        if not Path(target).is_file():
            continue
        try:
            ckpt = torch.load(target, map_location=map_loc, weights_only=False)
            if isinstance(ckpt, dict):
                return ckpt
            elif isinstance(ckpt, torch.Tensor) or hasattr(ckpt, "keys"):
                return {"model_state_dict": ckpt}
        except Exception as e1:
            last_exc = e1
            try:
                ckpt = torch.load(target, map_location="cpu", weights_only=True)
                if isinstance(ckpt, dict):
                    return ckpt
            except Exception:
                try:
                    ckpt = torch.load(target, map_location="cpu", weights_only=False)
                    if isinstance(ckpt, dict):
                        return ckpt
                except Exception:
                    pass

    if silent:
        return None

    if last_exc is not None:
        raise last_exc
    return None


def restore_training_state(
    model: Optional[nn.Module],
    checkpoint: Dict[str, Any],
    optimizer: Optional[Union[torch.optim.Optimizer, List[torch.optim.Optimizer]]] = None,
    device: Optional[Union[str, torch.device]] = None,
) -> Dict[str, Any]:
    """
    Restores model weights, optimizer states, and training progress metrics from a checkpoint dictionary.
    """
    if model is not None and checkpoint is not None:
        state_dict = None
        if isinstance(checkpoint, dict):
            if "model_state_dict" in checkpoint or "state_dict" in checkpoint:
                state_dict = checkpoint.get("model_state_dict", checkpoint.get("state_dict"))
            elif "model" in checkpoint and isinstance(checkpoint["model"], dict):
                state_dict = checkpoint["model"]
            elif any(isinstance(v, torch.Tensor) for v in checkpoint.values()) or any("weight" in str(k) or "bias" in str(k) for k in checkpoint.keys()):
                state_dict = checkpoint

        if state_dict is not None and hasattr(state_dict, "keys"):
            unwrapped = _unwrap_model(model)
            cleaned_sd = _clean_state_dict_keys(state_dict, unwrapped)
            has_nan = any(isinstance(v, torch.Tensor) and (torch.isnan(v).any() or torch.isinf(v).any()) for v in cleaned_sd.values())
            if has_nan:
                print("[gptio] Warning: Checkpoint weights contain NaN/Inf values! Refusing to load corrupted weights into model.")
            else:
                unwrapped.load_state_dict(cleaned_sd, strict=False)
            is_sharded = hasattr(model, "layer_devices") or hasattr(unwrapped, "layer_devices") or (len({p.device for p in unwrapped.parameters() if isinstance(p, torch.Tensor)}) > 1)
            if device is not None and not is_sharded:
                model.to(device=device)
        else:
            raise Exception("[gptio] Warning: No model weights found in checkpoint! Model parameters were not restored.")


    opt_state = checkpoint.get("optimizer_state_dict")
    if optimizer is not None and opt_state is not None:
        try:
            def _has_opt_nan(state_obj):
                if isinstance(state_obj, dict):
                    return any(_has_opt_nan(v) for v in state_obj.values())
                elif isinstance(state_obj, (list, tuple)):
                    return any(_has_opt_nan(v) for v in state_obj)
                elif isinstance(state_obj, torch.Tensor):
                    return bool(torch.isnan(state_obj).any() or torch.isinf(state_obj).any())
                return False

            if _has_opt_nan(opt_state):
                print("[gptio] Warning: Checkpoint optimizer state contains NaN/Inf values! Resetting to freshly initialized optimizer state.")
            else:
                unwrapped = _unwrap_model(model) if model is not None else None
                if unwrapped is not None and isinstance(opt_state, dict) and "state" in opt_state and not isinstance(optimizer, (list, tuple)):
                    flat_params = []
                    for group in optimizer.param_groups:
                        flat_params.extend(group["params"])

                    for p_idx, p in enumerate(flat_params):
                        if p_idx in opt_state["state"]:
                            p_state = opt_state["state"][p_idx]
                            for buf_name in ["exp_avg", "exp_avg_sq", "momentum_buffer"]:
                                if buf_name in p_state and isinstance(p_state[buf_name], torch.Tensor):
                                    if p_state[buf_name].shape != p.shape:
                                        b_shape = p_state[buf_name].shape
                                        t_shape = p.shape
                                        if len(b_shape) == len(t_shape) == 2 and b_shape[1] == t_shape[1]:
                                            if b_shape[0] < t_shape[0]:
                                                padded = torch.zeros(t_shape, dtype=p_state[buf_name].dtype, device=p_state[buf_name].device)
                                                padded[:b_shape[0], :] = p_state[buf_name]
                                                p_state[buf_name] = padded
                                            else:
                                                p_state[buf_name] = p_state[buf_name][:t_shape[0], :]
                                        else:
                                            p_state[buf_name] = torch.zeros_like(p)

                if isinstance(optimizer, (list, tuple)) and isinstance(opt_state, (list, tuple)):
                    for opt, s_dict in zip(optimizer, opt_state):
                        opt.load_state_dict(s_dict)
                elif not isinstance(optimizer, (list, tuple)) and isinstance(opt_state, dict):
                    optimizer.load_state_dict(opt_state)
        except Exception as e:
            print(f"[gptio] Notice: Could not fully restore optimizer state ({e}). Resuming with initialized optimizer state.")

    raw_epoch = checkpoint.get("epoch", 0)
    current_epoch = checkpoint.get("current_epoch", None)
    epoch_completed = checkpoint.get("epoch_completed", None)

    if current_epoch is None:
        if epoch_completed is True:
            current_epoch = raw_epoch
        elif epoch_completed is False:
            current_epoch = raw_epoch
        else:
            step_in_file = checkpoint.get("step_in_file", checkpoint.get("file_step", 0))
            if step_in_file > 0 or checkpoint.get("global_step", 0) > 0:
                current_epoch = max(0, raw_epoch - 1)
            else:
                current_epoch = raw_epoch

    return {
        "global_step": checkpoint.get("global_step", -1),
        "epoch": raw_epoch,
        "current_epoch": current_epoch,
        "current_file_idx": checkpoint.get("current_file_idx", checkpoint.get("file_idx", 1)),
        "step_in_file": checkpoint.get("step_in_file", checkpoint.get("file_step", 0)),
        "step_in_epoch": checkpoint.get("step_in_epoch", checkpoint.get("step_in_file", 0)),
        "epoch_completed": checkpoint.get("epoch_completed", False),
        "tokens_seen": checkpoint.get("tokens_seen", 0),
        "train_losses": checkpoint.get("train_losses", []),
        "val_losses": checkpoint.get("val_losses", []),
        "track_tokens": checkpoint.get("track_tokens", checkpoint.get("track_tokens_seen", [])),
        "train_margins": checkpoint.get("train_margins", []),
        "val_margins": checkpoint.get("val_margins", []),
        "is_sft": checkpoint.get("is_sft", False),
        "is_dpo": checkpoint.get("is_dpo", False),
        "accumulated_training_time": float(checkpoint.get("accumulated_training_time", 0.0)),
    }
