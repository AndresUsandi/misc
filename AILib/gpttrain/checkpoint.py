# Copyright (c) Sebastian Raschka under Apache License 2.0 (see LICENSE.txt).
# Checkpoint resumption, stage fallback loading, and training state restoration.

from pathlib import Path
import sys
from typing import Any, Dict, Optional

import torch
import torch.nn as nn

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from argsutil import TrainingArgs
from gptio.pathutil import STAGE_TRAIN, STAGE_TUNE, STAGE_OPTIMIZE
from gptio.checkpoint import load_checkpoint, restore_training_state
from gptio.modelio import load_model_weights
from gptmodel.MultiGpuGptModelDP import MultiGpuGptModelDP
from gptutils.consoleutils import print


def resume_stage_checkpoint(
    target_model: nn.Module,
    optimizer: Any,
    args: TrainingArgs,
    device: torch.device,
    use_cuda: bool,
) -> Optional[Dict[str, Any]]:
    """
    Handles checkpoint loading, active stage validation, fallback to prior stage weights,
    and replica weight synchronization. Returns dict of resumed state counters, or None if already completed.
    """
    stage = args.stage
    tokens_seen_init = 0
    resumed_step = 0
    initial_epoch = 0
    resumed_step_in_epoch = 0
    resumed_file_idx = 1
    resumed_step_in_file = 0
    initial_train_losses = [] if stage == STAGE_TRAIN else None
    initial_val_losses = [] if stage == STAGE_TRAIN else None
    initial_track_tokens = [] if stage == STAGE_TRAIN else None
    initial_train_margins = None
    initial_val_margins = None
    accumulated_training_time = 0.0

    if args.resume:
        ckpt = load_checkpoint(args, stage=stage, device="cpu", silent=True)
        if ckpt is not None:
            is_active_stage = (stage == STAGE_TRAIN and not ckpt.get("is_sft") and not ckpt.get("is_dpo")) or \
                              (stage == STAGE_TUNE and ckpt.get("is_sft")) or \
                              (stage == STAGE_OPTIMIZE and ckpt.get("is_dpo"))
            if is_active_stage:
                restored = restore_training_state(target_model, ckpt, optimizer=optimizer, device=device)
                resumed_step = max(0, restored.get("global_step", 0))
                epoch_completed = restored.get("epoch_completed", False)
                if epoch_completed:
                    initial_epoch = max(0, restored.get("current_epoch", restored.get("epoch", 0)))
                    resumed_step_in_epoch = 0
                else:
                    initial_epoch = max(0, restored.get("current_epoch", 0))
                    resumed_step_in_epoch = max(0, restored.get("step_in_epoch", 0))
                resumed_file_idx = max(1, restored.get("current_file_idx", 1))
                resumed_step_in_file = max(0, restored.get("step_in_file", 0))
                tokens_seen_init = restored.get("tokens_seen", 0)
                accumulated_training_time = float(restored.get("accumulated_training_time", 0.0))
                initial_train_losses = restored.get("train_losses", []) if stage == STAGE_TRAIN else restored.get("train_losses")
                initial_val_losses = restored.get("val_losses", []) if stage == STAGE_TRAIN else restored.get("val_losses")
                initial_track_tokens = restored.get("track_tokens", []) if stage == STAGE_TRAIN else restored.get("track_tokens")
                if stage == STAGE_OPTIMIZE:
                    initial_train_margins = restored.get("train_margins")
                    initial_val_margins = restored.get("val_margins")
                del ckpt
                if use_cuda:
                    torch.cuda.empty_cache()
                print(f"[Resume] Successfully loaded active {stage.upper()} checkpoint at Global Step {resumed_step:,} "
                      f"(Epoch {initial_epoch + 1}, File {resumed_file_idx}, Step {resumed_step_in_epoch or resumed_step_in_file}, Tokens seen: {tokens_seen_init:,}).")
            else:
                restored = restore_training_state(target_model, ckpt, device=device)
                base_desc = "base SFT" if ckpt.get("is_sft") else "base pre-trained"
                del ckpt
                if use_cuda:
                    torch.cuda.empty_cache()
                print(f"[Resume] Loaded {base_desc} weights for {stage.upper()}. Starting {stage.upper()} from Step 0.")
        else:
            # Checkpoint not found for active stage. Fallback to base weights from prior stage.
            if stage == STAGE_TUNE:
                trn_ckpt = load_checkpoint(args, stage=STAGE_TRAIN, device="cpu", silent=True)
                if trn_ckpt is not None:
                    restore_training_state(target_model, trn_ckpt, device=device)
                    del trn_ckpt
                    print(f"[Resume] No active SFT checkpoint found for '{args.model_name}'. Loaded base pre-trained checkpoint weights (.trn.chk). Starting Fine-Tuning from Step 0.")
                else:
                    loaded_pth = load_model_weights(target_model, args, device=device)
                    if loaded_pth:
                        print(f"[Resume] No active SFT checkpoint found for '{args.model_name}'. Loaded base model weights (.pth). Starting Fine-Tuning from Step 0.")
                    else:
                        print(f"[Resume] No checkpoint or base model found for '{args.model_name}'. Starting Fine-Tuning from initialized weights.")
            elif stage == STAGE_OPTIMIZE:
                sft_ckpt = load_checkpoint(args, stage=STAGE_TUNE, device="cpu", silent=True)
                if sft_ckpt is not None:
                    restore_training_state(target_model, sft_ckpt, device=device)
                    del sft_ckpt
                    print(f"[Resume] No active DPO checkpoint found for '{args.model_name}'. Loaded base SFT checkpoint weights (.sft.chk). Starting DPO from Step 0.")
                else:
                    loaded_pth = load_model_weights(target_model, args, device=device)
                    if loaded_pth:
                        print(f"[Resume] Loaded base model weights (.pth) for policy model. Starting DPO from Step 0.")
                    else:
                        print(f"[Resume] Starting DPO from initialized weights.")
            else:
                print(f"[Resume] No existing checkpoint found for '{args.model_name}' (TRAIN). Starting from scratch.")
    else:
        # Resume disabled: fresh start for this stage
        if stage == STAGE_TUNE:
            trn_ckpt = load_checkpoint(args, stage=STAGE_TRAIN, device="cpu", silent=True)
            if trn_ckpt is not None:
                restore_training_state(target_model, trn_ckpt, device=device)
                del trn_ckpt
                print(f"[Fine-Tuning] Resume disabled. Initialized model from base pre-trained checkpoint (.trn.chk). Starting Fine-Tuning from Step 0.")
            else:
                loaded_pth = load_model_weights(target_model, args, device=device)
                if loaded_pth:
                    print(f"[Fine-Tuning] Resume disabled. Initialized model from base model weights (.pth). Starting Fine-Tuning from Step 0.")
                else:
                    print(f"[Notice] Resume disabled. Starting Fine-Tuning from initialized weights.")
        elif stage == STAGE_OPTIMIZE:
            sft_ckpt = load_checkpoint(args, stage=STAGE_TUNE, device="cpu", silent=True)
            if sft_ckpt is not None:
                restore_training_state(target_model, sft_ckpt, device=device)
                del sft_ckpt
                print(f"[Policy Model] Resume disabled. Initialized policy weights from base SFT checkpoint (.sft.chk).")
            else:
                loaded_pth = load_model_weights(target_model, args, device=device)
                if loaded_pth:
                    print(f"[Policy Model] Resume disabled. Initialized policy weights from base model (.pth).")
                else:
                    print(f"[Notice] Resume disabled. Starting {stage.upper()} from initialized weights.")
        else:
            print(f"[Notice] Resume disabled. Starting {stage.upper()} from initialized weights.")

    if use_cuda:
        torch.cuda.empty_cache()

        if initial_epoch >= args.num_epochs:
            print(f"\n[Resume Notice] Checkpoint has already completed {initial_epoch} epochs (>= requested num_epochs {args.num_epochs}).")
            action_desc = "fine-tune" if stage == STAGE_TUNE else "optimize"
            print(f"To {action_desc} for additional epochs, specify a higher --num_epochs (e.g. --num_epochs {initial_epoch + 1}).\n")
            return None

    # Replicas must start from the restored weights (checkpoints load into the primary only)
    if isinstance(target_model, MultiGpuGptModelDP):
        target_model.sync_weights()

    return {
        "tokens_seen_init": tokens_seen_init,
        "resumed_step": resumed_step,
        "initial_epoch": initial_epoch,
        "resumed_step_in_epoch": resumed_step_in_epoch,
        "resumed_file_idx": resumed_file_idx,
        "resumed_step_in_file": resumed_step_in_file,
        "initial_train_losses": initial_train_losses,
        "initial_val_losses": initial_val_losses,
        "initial_track_tokens": initial_track_tokens,
        "initial_train_margins": initial_train_margins,
        "initial_val_margins": initial_val_margins,
        "accumulated_training_time": accumulated_training_time,
    }
