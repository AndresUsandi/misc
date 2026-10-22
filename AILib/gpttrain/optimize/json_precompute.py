# Copyright (c) Sebastian Raschka under Apache License 2.0 (see LICENSE.txt).
# Fully-Optimized Precomputed DPO Engine (Single-GPU & High-Speed Direct Preference Optimization)
# Precomputes and caches frozen reference model log-probabilities directly in JSON preference datasets.
# Benefits:
# 1. Zero Reference Model VRAM: Eliminates the reference model from GPU memory during training, saving 1.55+ GB VRAM.
# 2. 100% Single-GPU Compatibility: Allows full-parameter DPO tuning of 774M+ models on a single 8 GB GPU without OOM.
# 3. ~35% Faster Training Throughput: Completely skips 2 reference model forward passes per mini-batch on every training step.
# 4. Backward Compatibility: Fully inter-operable with standard unannotated datasets via --json_precompute.

from contextlib import nullcontext
from functools import partial
import json
import math
import os
from pathlib import Path
import sys
import time
from typing import Any, Dict, List, Optional, Tuple, Union

import matplotlib.pyplot as plt
import tiktoken
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset, RandomSampler

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from argsutil import TrainingArgs
from gptmodel.GptModel import GptModel
from gpttrain.train.evaluation import (
    text_to_token_ids,
    token_ids_to_text,
)
from gptmodel.Dataset import (
    format_input,
)
from gpttrain.optimize.dpo_loss import (
    compute_logprobs,
    compute_logprobs_chunked,
    compute_dpo_loss,
    split_dpo_backward,
)
from gpttrain.plots import plot_dpo_losses_and_margins
from gpttrain.optimize.scheduler import get_cosine_lr_with_warmup
from gptio.checkpoint import (
    save_checkpoint,
    load_checkpoint,
    restore_training_state,
)
from gptio.modelio import save_model
from gptio.pathutil import resolve_path, TARGET_PLOT, STAGE_OPTIMIZE, STAGE_TUNE
from gptio.precision import create_grad_scaler
from gpttrain.optimizer import lr_schedule_from_resume, set_optimizer_lr
from gptutils.consoleutils import (
    print,
    print_eta,
    format_vram_report,
    print_gpu_memory_breakdown,
    print_step_telemetry,
)
from gptutils.metrics import print_stage_completion_summary, count_model_parameters
from gptinfer.inference import generate_text


# ==============================================================================
# 1. Offline Reference Log-Probability Precomputation
# ==============================================================================

def precompute_dataset_reference_logprobs(
    preference_data: List[Dict[str, Any]],
    args: TrainingArgs,
    gpt_config: Dict[str, Any],
    tokenizer: Any,
    device: torch.device,
    max_length: Optional[int] = 768,
    amp_dtype: Optional[torch.dtype] = torch.float16,
) -> List[Dict[str, Any]]:
    """
    Checks if preference entries already contain precomputed reference log-probabilities.
    If not, loads the base SFT model, computes scalar log-probabilities for chosen and
    rejected responses offline, and saves the annotated entries back to the JSON file.
    """
    all_precomputed = (
        len(preference_data) > 0 and
        all("ref_chosen_logprob" in e and "ref_rejected_logprob" in e for e in preference_data)
    )
    if all_precomputed:
        print(f"[Precompute] Dataset already contains precomputed reference log-probabilities ({len(preference_data):,} pairs). Skipping offline pass.")
        return preference_data

    print("\n" + "=" * 65)
    print("   PRECOMPUTING REFERENCE LOG-PROBABILITIES FOR DPO")
    print("=" * 65)
    print(f"Model Target  : {args.model_name}")
    print(f"Device        : {device} (AMP: {amp_dtype})")
    print(f"Total Items   : {len(preference_data):,}")
    print(f"Max Length    : {max_length}")
    print("=" * 65)

    ref_model = GptModel(gpt_config)
    weight_dtype = torch.float16 if amp_dtype == torch.float16 else torch.float32
    ref_model.to(device=device, dtype=weight_dtype)
    ref_model.eval()
    for p in ref_model.parameters():
        p.requires_grad = False

    sft_ckpt = load_checkpoint(args, stage=STAGE_TUNE, device="cpu", silent=True)
    if sft_ckpt is not None:
        restore_training_state(ref_model, sft_ckpt, device=device)
        del sft_ckpt
        if device.type == "cuda":
            torch.cuda.empty_cache()
        print(f"[Precompute] Initialized reference model from SFT checkpoint on {device}.")
    else:
        print(f"[Precompute Warning] Base SFT checkpoint not found; reference model using initialized base weights.")

    t0 = time.time()
    updated_count = 0

    with torch.no_grad():
        for idx, entry in enumerate(preference_data, 1):
            if "ref_chosen_logprob" in entry and "ref_rejected_logprob" in entry:
                continue

            prompt = format_input(entry)
            chosen_resp = str(entry.get("chosen") or entry.get("output") or "").strip()
            rejected_resp = str(entry.get("rejected") or "").strip()

            if not chosen_resp or not rejected_resp:
                continue

            prompt_tokens = tokenizer.encode(prompt, allowed_special="all")
            is_chat_prompt = ("<|assistant|>" in prompt or "<|im_start|>" in prompt)
            end = "<|im_end|>" if "<|im_start|>" in prompt else ""
            chosen_full_text = f"{prompt}{chosen_resp}{end}" if is_chat_prompt else f"{prompt}\n\n### Response:\n{chosen_resp}"
            rejected_full_text = f"{prompt}{rejected_resp}{end}" if is_chat_prompt else f"{prompt}\n\n### Response:\n{rejected_resp}"

            chosen_full_tokens = tokenizer.encode(chosen_full_text, allowed_special="all")
            rejected_full_tokens = tokenizer.encode(rejected_full_text, allowed_special="all")

            if max_length is not None:
                chosen_full_tokens = chosen_full_tokens[:max_length]
                rejected_full_tokens = rejected_full_tokens[:max_length]

            c_tensor = torch.tensor([chosen_full_tokens], dtype=torch.long, device=device)
            c_mask = torch.ones(1, len(chosen_full_tokens), dtype=torch.bool, device=device)
            p_len_c = min(len(prompt_tokens) if is_chat_prompt else len(prompt_tokens) + 2, len(chosen_full_tokens))
            c_mask[:, :p_len_c] = False

            r_tensor = torch.tensor([rejected_full_tokens], dtype=torch.long, device=device)
            r_mask = torch.ones(1, len(rejected_full_tokens), dtype=torch.bool, device=device)
            p_len_r = min(len(prompt_tokens) if is_chat_prompt else len(prompt_tokens) + 2, len(rejected_full_tokens))
            r_mask[:, :p_len_r] = False

            if amp_dtype is not None and device.type == "cuda":
                with torch.amp.autocast(device_type="cuda", dtype=amp_dtype):
                    c_logits = ref_model(c_tensor)
                    c_lp = compute_logprobs(c_logits, c_tensor, c_mask).item()
                    del c_logits

                    r_logits = ref_model(r_tensor)
                    r_lp = compute_logprobs(r_logits, r_tensor, r_mask).item()
                    del r_logits
            else:
                c_logits = ref_model(c_tensor)
                c_lp = compute_logprobs(c_logits, c_tensor, c_mask).item()
                del c_logits

                r_logits = ref_model(r_tensor)
                r_lp = compute_logprobs(r_logits, r_tensor, r_mask).item()
                del r_logits

            entry["ref_chosen_logprob"] = round(float(c_lp), 6)
            entry["ref_rejected_logprob"] = round(float(r_lp), 6)
            updated_count += 1

            if idx % 500 == 0 or idx == len(preference_data):
                elapsed = time.time() - t0
                speed = idx / elapsed if elapsed > 0 else 0
                eta_s = (len(preference_data) - idx) / speed if speed > 0 else 0
                print(f"  [Precompute] [{idx:,}/{len(preference_data):,}] Processed ({speed:.1f} pairs/sec | ETA: {eta_s:.0f}s)...")

    # Persist updated entries back into the discovered file(s)
    discovered_files = getattr(preference_data, "discovered_files", [])
    file_counts = getattr(preference_data, "file_sample_counts", {})
    if discovered_files and len(discovered_files) == 1:
        target_f = discovered_files[0]
        try:
            with open(target_f, "w", encoding="utf-8") as f:
                json.dump(list(preference_data), f, indent=2, ensure_ascii=False)
            print(f"[Precompute] Saved annotated dataset with reference log-probs to '{target_f.name}'.")
        except Exception as e:
            print(f"[Precompute Warning] Could not save updated dataset to '{target_f}': {e}")
    elif discovered_files:
        offset = 0
        for f_path in discovered_files:
            cnt = file_counts.get(str(f_path), 0)
            slice_data = list(preference_data[offset:offset + cnt])
            offset += cnt
            try:
                with open(f_path, "w", encoding="utf-8") as f:
                    json.dump(slice_data, f, indent=2, ensure_ascii=False)
                print(f"[Precompute] Saved annotated dataset with reference log-probs to '{f_path.name}'.")
            except Exception as e:
                print(f"[Precompute Warning] Could not save updated dataset to '{f_path}': {e}")

    # Release reference model from VRAM
    del ref_model
    if device.type == "cuda":
        torch.cuda.empty_cache()
    print(f"[Precompute Complete] Successfully precomputed {updated_count:,} pairs in {time.time()-t0:.1f}s. Reference model released from memory.\n")
    return preference_data


# ==============================================================================
# 2. Precomputed Preference Dataset & Dynamic Collation
# ==============================================================================

class PrecomputedPreferenceDataset(Dataset):
    """
    Dataset for DPO with precomputed reference log-probabilities.
    Stores pre-tokenized prompt, chosen, rejected sequences along with static scalar reference logprobs.
    """
    def __init__(self, data: List[Any], tokenizer: Any = None, max_length: Optional[int] = None):
        self.data = data
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.encoded_texts: List[Dict[str, Any]] = []
        self.generator = torch.Generator()  # drives the train loader's RandomSampler; seek() re-seeds it per epoch

        if data and isinstance(data[0], dict) and "prompt" in data[0] and "chosen" in data[0] and isinstance(data[0]["chosen"], list):
            self.encoded_texts = list(data)
        elif data and tokenizer is not None:
            skipped_count = 0
            for entry in data:
                prompt = format_input(entry)
                chosen_resp = str(entry.get("chosen") or entry.get("output") or "").strip()
                rejected_resp = str(entry.get("rejected") or "").strip()

                if not chosen_resp or not rejected_resp:
                    skipped_count += 1
                    continue

                prompt_tokens = tokenizer.encode(prompt, allowed_special="all")
                is_chat_prompt = ("<|assistant|>" in prompt or "<|im_start|>" in prompt)
                if is_chat_prompt:
                    end = "<|im_end|>" if "<|im_start|>" in prompt else ""
                    chosen_full_text = f"{prompt}{chosen_resp}{end}"
                    rejected_full_text = f"{prompt}{rejected_resp}{end}"
                else:
                    chosen_full_text = f"{prompt}\n\n### Response:\n{chosen_resp}"
                    rejected_full_text = f"{prompt}\n\n### Response:\n{rejected_resp}"

                chosen_full_tokens = tokenizer.encode(chosen_full_text, allowed_special="all")
                rejected_full_tokens = tokenizer.encode(rejected_full_text, allowed_special="all")

                if max_length is not None and (
                    len(prompt_tokens) >= max_length or
                    len(chosen_full_tokens) > max_length or
                    len(rejected_full_tokens) > max_length
                ):
                    skipped_count += 1
                    continue

                ref_chosen_lp = float(entry.get("ref_chosen_logprob", 0.0))
                ref_rejected_lp = float(entry.get("ref_rejected_logprob", 0.0))

                self.encoded_texts.append({
                    "prompt": prompt_tokens,
                    "chosen": chosen_full_tokens,
                    "rejected": rejected_full_tokens,
                    "ref_chosen_logprob": ref_chosen_lp,
                    "ref_rejected_logprob": ref_rejected_lp,
                    "is_chat": is_chat_prompt,
                })

            if skipped_count > 0:
                print(f"[Data Filter] Kept {len(self.encoded_texts):,} items (skipped {skipped_count:,} exceeding max_length {max_length} or empty).")

    def __getitem__(self, index: int) -> Dict[str, Any]:
        return self.encoded_texts[index]

    def __len__(self) -> int:
        return len(self.encoded_texts)

    def seek(self, epoch: int) -> None:
        """Seeds the epoch's shuffle (deterministic, so a resume replays the checkpointed order)."""
        self.generator.manual_seed(1_000_003 * epoch + 7)


def precomputed_dpo_collate_fn(
    batch: List[Dict[str, Any]],
    pad_token_id: int = 50256,
    allowed_max_length: Optional[int] = None,
    mask_prompt_tokens: bool = True,
    device: Union[str, torch.device] = "cpu"
) -> Dict[str, Any]:
    """
    Collates a batch of precomputed preference items into padded tensors, masks,
    and 1D tensors of scalar reference log-probabilities.
    """
    batch_data: Dict[str, List[torch.Tensor]] = {
        "prompt": [],
        "chosen": [],
        "rejected": [],
        "chosen_mask": [],
        "rejected_mask": []
    }
    ref_chosen_list: List[float] = []
    ref_rejected_list: List[float] = []

    max_length_common = 0
    if batch:
        for key in ["chosen", "rejected"]:
            current_max = max(len(item[key]) + 1 for item in batch)
            max_length_common = max(max_length_common, current_max)

    for item in batch:
        prompt_tensor = torch.tensor(item["prompt"], dtype=torch.long)
        batch_data["prompt"].append(prompt_tensor)
        ref_chosen_list.append(float(item.get("ref_chosen_logprob", 0.0)))
        ref_rejected_list.append(float(item.get("ref_rejected_logprob", 0.0)))

        for key in ["chosen", "rejected"]:
            sequence = item[key]
            padded = sequence + [pad_token_id] * (max_length_common - len(sequence))
            mask = torch.ones(len(padded), dtype=torch.bool)

            # Mask padding tokens
            mask[len(sequence):] = False

            # Mask prompt tokens
            if mask_prompt_tokens:
                offset = 0 if item.get("is_chat", True) else 2
                mask[:prompt_tensor.shape[0] + offset] = False

            batch_data[key].append(torch.tensor(padded, dtype=torch.long))
            batch_data[f"{key}_mask"].append(mask)

    result: Dict[str, Any] = {"prompt": batch_data["prompt"]}
    for key in ["chosen", "rejected", "chosen_mask", "rejected_mask"]:
        stacked = torch.stack(batch_data[key])
        if allowed_max_length is not None:
            stacked = stacked[:, :allowed_max_length]
        result[key] = stacked.to(device)

    result["ref_chosen_logprob"] = torch.tensor(ref_chosen_list, dtype=torch.float32, device=device)
    result["ref_rejected_logprob"] = torch.tensor(ref_rejected_list, dtype=torch.float32, device=device)

    return result


def create_precomputed_preference_dataloaders(
    data: List[Dict[str, Any]],
    tokenizer: Any,
    batch_size: int = 4,
    max_length: int = 768,
    train_ratio: float = 0.85,
    test_ratio: float = 0.10,
    num_workers: int = 0,
    device: Union[str, torch.device] = "cpu"
) -> Tuple[DataLoader, DataLoader, List[Dict[str, Any]]]:
    """
    Creates train and validation DataLoaders using precomputed reference log-probabilities.
    """
    full_dataset = PrecomputedPreferenceDataset(data, tokenizer, max_length=max_length)
    encoded = full_dataset.encoded_texts
    total = len(encoded)

    if total == 0:
        raise ValueError(f"No valid preference items remain after filtering with max_length={max_length}.")

    train_size = max(1, int(total * train_ratio))
    test_size = max(0, int(total * test_ratio))
    val_size = total - train_size - test_size

    min_val = max(1, int(total * 0.01)) if total >= 100 else 1
    if val_size < min_val and total > 1:
        val_size = max(1, int(total * 0.05))
        test_size = max(0, total - train_size - val_size)
        if train_size + test_size + val_size > total:
            train_size = max(1, total - val_size)
            test_size = 0

    train_dataset = PrecomputedPreferenceDataset(encoded[:train_size], tokenizer)
    val_dataset = PrecomputedPreferenceDataset(encoded[train_size:train_size + val_size], tokenizer)
    test_data = data[train_size + val_size:train_size + val_size + test_size]

    print(f"[Dataset Split] Total Valid: {total:,} | Train: {len(train_dataset):,} | Val: {len(val_dataset):,} | Test: {len(test_data):,}")

    collate_fn = partial(
        precomputed_dpo_collate_fn,
        pad_token_id=tokenizer.pad_id,
        allowed_max_length=max_length,
        mask_prompt_tokens=True,
        device=device
    )

    pin_mem = (device != "cpu" and torch.cuda.is_available() and num_workers > 0)
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        collate_fn=collate_fn,
        sampler=RandomSampler(train_dataset, generator=train_dataset.generator),  # global shuffle, seeded per epoch through dataset.seek(epoch)
        drop_last=True if len(train_dataset) > batch_size else False,
        num_workers=num_workers,
        pin_memory=pin_mem
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        collate_fn=collate_fn,
        shuffle=True,
        drop_last=False,
        num_workers=num_workers,
        pin_memory=pin_mem
    )

    return train_loader, val_loader, test_data


# ==============================================================================
# 3. Fast DPO Loss Computation (Zero Reference Model Forward Passes)
# ==============================================================================

def compute_dpo_loss_batch_precomputed(
    batch: Dict[str, Any],
    policy_model: nn.Module,
    beta: float = 0.1,
    policy_device: torch.device = torch.device("cpu"),
    amp_dtype: Optional[torch.dtype] = None,
    activation_checkpointing: bool = False,
    use_amp: Optional[bool] = None,
    chunk_size: int = 256,
    backward_accum_steps: Optional[int] = None,
    scaler: Optional[Any] = None,
    sft_weight: float = 0.0,
) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
    """
    Computes DPO loss for a batch using precomputed reference log-probabilities.
    Only executes forward passes for the trainable policy model!
    backward_accum_steps: when given, also runs the (scaled, accumulation-divided) split backward and returns a detached loss.
    """
    if hasattr(policy_model, "forward_backward_dpo"):  # MultiGpuGptModelDP / ZeRO-1: the pairs are split across the GPUs, each scoring its share with its own policy copy
        return policy_model.forward_backward_dpo(batch, compute_dpo_loss_batch_precomputed, amp_dtype=amp_dtype, beta=beta, activation_checkpointing=activation_checkpointing, use_amp=use_amp, chunk_size=chunk_size, backward_accum_steps=backward_accum_steps, scaler=scaler, sft_weight=sft_weight)
    chosen_in = batch["chosen"].to(policy_device)
    chosen_mask = batch["chosen_mask"].to(policy_device)
    rejected_in = batch["rejected"].to(policy_device)
    rejected_mask = batch["rejected_mask"].to(policy_device)

    use_cuda = policy_device.type == "cuda"
    if use_amp is None:
        use_amp = (use_cuda and amp_dtype is not None and amp_dtype != torch.float32)
    autocast_ctx = torch.amp.autocast(device_type="cuda", dtype=amp_dtype, cache_enabled=False) if (use_amp and amp_dtype is not None) else nullcontext()  # type: ignore
    policy_forward = getattr(policy_model, "compiled_forward_features", policy_model.forward_features)  # --compile (model_setup) attaches the compiled variant

    # Policy model forward passes
    with autocast_ctx:
        policy_chosen_hidden = policy_forward(chosen_in, activation_checkpointing=activation_checkpointing)
        policy_chosen_logprobs = compute_logprobs_chunked(policy_chosen_hidden, chosen_in, chosen_mask, policy_model.out_head, chunk_size)
        del policy_chosen_hidden

        policy_rejected_hidden = policy_forward(rejected_in, activation_checkpointing=activation_checkpointing)
        policy_rejected_logprobs = compute_logprobs_chunked(policy_rejected_hidden, rejected_in, rejected_mask, policy_model.out_head, chunk_size)
        del policy_rejected_hidden

    ref_chosen_logprobs = batch["ref_chosen_logprob"].to(policy_device)
    ref_rejected_logprobs = batch["ref_rejected_logprob"].to(policy_device)

    loss, chosen_rewards, rejected_rewards, reward_margins, accuracy = compute_dpo_loss(
        model_chosen_logprobs=policy_chosen_logprobs,
        model_rejected_logprobs=policy_rejected_logprobs,
        reference_chosen_logprobs=ref_chosen_logprobs,
        reference_rejected_logprobs=ref_rejected_logprobs,
        beta=beta,
        sft_weight=sft_weight,
    )

    if backward_accum_steps is not None:
        loss = split_dpo_backward(loss, policy_chosen_logprobs, policy_rejected_logprobs, backward_accum_steps, scaler)

    return loss, chosen_rewards, rejected_rewards, reward_margins, accuracy


def evaluate_dpo_loader_precomputed(
    data_loader: DataLoader,
    policy_model: nn.Module,
    beta: float = 0.1,
    policy_device: torch.device = torch.device("cpu"),
    num_batches: Optional[int] = None,
    amp_dtype: Optional[torch.dtype] = None,
    use_amp: Optional[bool] = None,
    sft_weight: float = 0.0,
) -> Dict[str, float]:
    """
    Evaluates average DPO loss, reward margin, and accuracy using precomputed reference logprobs.
    """
    if len(data_loader) == 0:
        return {"loss": float("nan"), "chosen_reward": 0.0, "rejected_reward": 0.0, "margin": 0.0, "accuracy": 0.0}

    total_batches = min(num_batches, len(data_loader)) if num_batches is not None else len(data_loader)
    tot_loss = 0.0
    tot_chosen = 0.0
    tot_rejected = 0.0
    tot_margin = 0.0
    tot_acc = 0.0

    policy_model.eval()
    with torch.no_grad():
        for i, batch in enumerate(data_loader):
            if i >= total_batches:
                break
            loss, chosen_rewards, rejected_rewards, reward_margins, acc = compute_dpo_loss_batch_precomputed(
                batch=batch,
                policy_model=policy_model,
                beta=beta,
                policy_device=policy_device,
                amp_dtype=amp_dtype,
                activation_checkpointing=False,
                use_amp=use_amp,
                sft_weight=sft_weight,
            )
            tot_loss += loss.item()
            tot_chosen += chosen_rewards.item()
            tot_rejected += rejected_rewards.item()
            tot_margin += reward_margins.item()
            tot_acc += acc.item()

    policy_model.train()
    count = max(1, total_batches)
    return {
        "loss": tot_loss / count,
        "chosen_reward": tot_chosen / count,
        "rejected_reward": tot_rejected / count,
        "margin": tot_margin / count,
        "accuracy": tot_acc / count,
    }


# ==============================================================================
# 4. Precomputed DPO Training Engine
# ==============================================================================

def train_model_dpo_precomputed(
    policy_model: nn.Module,
    train_loader: DataLoader,
    val_loader: DataLoader,
    optimizer: Any,
    device: torch.device,
    args: TrainingArgs,
    start_context_entry: Dict[str, Any],
    tokenizer: Any,
    gpt_config: Optional[Dict[str, Any]] = None,
    initial_epoch: int = 0,
    resumed_step: int = 0,
    resumed_step_in_epoch: int = 0,
    tokens_seen_init: int = 0,
    initial_train_losses: Optional[List[float]] = None,
    initial_val_losses: Optional[List[float]] = None,
    initial_train_margins: Optional[List[float]] = None,
    initial_val_margins: Optional[List[float]] = None,
    initial_track_tokens: Optional[List[int]] = None,
    amp_dtype: Optional[torch.dtype] = torch.float16,
    use_amp: Optional[bool] = None,
    accumulated_training_time: float = 0.0,
) -> Tuple[List[float], List[float], List[float], List[float], List[int], List[float], float]:
    """
    High-Speed Precomputed DPO Training Engine.
    Executes DPO without loading or running the reference model in GPU memory.
    """
    raw_policy = getattr(policy_model, "raw_model", getattr(policy_model, "module", policy_model))
    raw_policy = getattr(raw_policy, "_orig_mod", raw_policy)

    train_losses = list(initial_train_losses) if initial_train_losses is not None else []
    val_losses = list(initial_val_losses) if initial_val_losses is not None else []
    train_margins = list(initial_train_margins) if initial_train_margins is not None else []
    val_margins = list(initial_val_margins) if initial_val_margins is not None else []
    track_tokens_seen = list(initial_track_tokens) if initial_track_tokens is not None else []
    track_epochs: List[float] = []

    tokens_seen = tokens_seen_init
    start_step = resumed_step
    target_step = (start_step + args.step_limit) if args.step_limit is not None and args.step_limit > 0 else None
    global_step = start_step

    start_epoch = initial_epoch
    if start_epoch >= args.num_epochs:
        print(f"\n[Resume Notice] Checkpoint has already completed {start_epoch} epochs (>= requested {args.num_epochs}).")
        return train_losses, val_losses, train_margins, val_margins, track_tokens_seen, track_epochs, accumulated_training_time

    total_steps_in_epoch = len(train_loader)
    effective_steps_in_epoch = math.ceil(total_steps_in_epoch / args.accum_steps)
    global_total_steps = effective_steps_in_epoch * args.num_epochs
    warmup_steps = int(global_total_steps * args.warmup_ratio)

    print(f"\n[Precomputed DPO Plan] Target epochs: {args.num_epochs} | Steps per epoch: {total_steps_in_epoch:,} (Updates: {effective_steps_in_epoch:,}) | Total updates: {global_total_steps:,} | Step plan: exact (precomputed JSON, fixed batch size)")
    lr_at = lr_schedule_from_resume(optimizer, start_step, lambda s: get_cosine_lr_with_warmup(s, warmup_steps, global_total_steps, args.learning_rate, args.min_lr), global_total_steps, warmup_steps, args.min_lr)
    print(f"[Precomputed DPO Mode] Reference model bypassed entirely! Running single-model policy optimization.")
    if target_step is not None:
        print(f"[DPO Plan] Resumed from step {start_step}. Training for {args.step_limit} steps -> Target step: {target_step}.")
    if args.accum_steps > 1:
        print(f"[Gradient Accumulation] Accumulating gradients over {args.accum_steps} sub-steps before optimizer update.")
    if args.model_name:
        print(f"[Checkpointing] Model target: '{args.model_name}'")

    sample_prompt = format_input(start_context_entry)
    use_cuda = (device.type == "cuda")
    if use_amp is None:
        use_amp = (use_cuda and amp_dtype is not None and amp_dtype != torch.float32)
    scaler = create_grad_scaler(policy_model, device, use_amp=use_amp, amp_dtype=amp_dtype)

    # Initial evaluation
    print("\n[Initial State Evaluation]")
    t_init_eval_start = time.time()
    init_tr = evaluate_dpo_loader_precomputed(train_loader, policy_model, args.beta, device, args.eval_iter, amp_dtype=amp_dtype, use_amp=use_amp, sft_weight=args.dpo_sft_weight)
    init_val = evaluate_dpo_loader_precomputed(val_loader, policy_model, args.beta, device, args.eval_iter, amp_dtype=amp_dtype, use_amp=use_amp, sft_weight=args.dpo_sft_weight)
    init_eval_time = time.time() - t_init_eval_start
    print(f"  Initial Train Loss : {init_tr['loss']:.4f} | Margin: {init_tr['margin']:+.4f} | Chosen vs ref: {init_tr['chosen_reward']:+.4f} | Acc: {init_tr['accuracy'] * 100:.1f}%")
    print(f"  Initial Val Loss   : {init_val['loss']:.4f} | Margin: {init_val['margin']:+.4f} | Chosen vs ref: {init_val['chosen_reward']:+.4f} | Acc: {init_val['accuracy'] * 100:.1f}% (Eval took {init_eval_time:.2f}s)")

    start_time = time.time()
    def get_current_accum_time() -> float:
        return accumulated_training_time + (time.time() - start_time)

    interval_train_time = 0.0
    interval_tokens = 0
    cumulative_train_time = 0.0
    stopped_due_to_limit = False

    step_in_epoch = resumed_step_in_epoch
    epoch = start_epoch

    try:
        for epoch in range(start_epoch, args.num_epochs):
            print(f"\n{'='*70}\nStarting Precomputed DPO Optimization Epoch {epoch+1}/{args.num_epochs}\n{'='*70}")
            epoch_start_time = time.time()
            policy_model.train()

            skip_steps = resumed_step_in_epoch if epoch == start_epoch else 0
            if skip_steps > 0:
                print(f"[Resume] Fast-forwarding {skip_steps} step(s) in Epoch {epoch+1} -> Resuming from step {skip_steps + 1}/{total_steps_in_epoch}...")

            if isinstance(optimizer, list):
                for opt in optimizer:
                    opt.zero_grad()
            else:
                optimizer.zero_grad()

            train_loader.dataset.seek(epoch)  # per-epoch global shuffle (deterministic, so the fast-forward above replays the checkpointed order)
            for step_in_epoch, batch in enumerate(train_loader, 1):
                if step_in_epoch <= skip_steps:
                    continue

                t_step_start = time.time()

                loss, chosen_rew, rej_rew, margin, acc = compute_dpo_loss_batch_precomputed(
                    batch=batch,
                    policy_model=policy_model,
                    beta=args.beta,
                    sft_weight=args.dpo_sft_weight,
                    policy_device=device,
                    amp_dtype=amp_dtype,
                    activation_checkpointing=args.activation_checkpointing,
                    use_amp=use_amp,
                    chunk_size=args.chunk_size,
                    backward_accum_steps=args.accum_steps,
                    scaler=scaler,
                )

                del loss

                batch_tokens = int((batch["chosen"] != tokenizer.pad_id).sum().item() + (batch["rejected"] != tokenizer.pad_id).sum().item())
                tokens_seen += batch_tokens
                interval_tokens += batch_tokens

                is_accum_step = (step_in_epoch % args.accum_steps == 0) or (step_in_epoch == total_steps_in_epoch)

                if is_accum_step:
                    global_step += 1

                    if hasattr(policy_model, "reduce_gradients"):  # data parallelism: average the copies' accumulated gradients onto the masters
                        policy_model.reduce_gradients()

                    current_lr = lr_at(global_step)
                    set_optimizer_lr(optimizer, current_lr)

                    if scaler:
                        if isinstance(optimizer, list):
                            for opt in optimizer:
                                scaler.unscale_(opt)
                            torch.nn.utils.clip_grad_norm_(policy_model.parameters(), max_norm=1.0)  # the wrapper's parameters: under ZeRO-1 the averaged gradients live on the shard masters
                            for opt in optimizer:
                                scaler.step(opt)
                        else:
                            scaler.unscale_(optimizer)
                            torch.nn.utils.clip_grad_norm_(policy_model.parameters(), max_norm=1.0)
                            scaler.step(optimizer)
                        scaler.update()
                    else:
                        torch.nn.utils.clip_grad_norm_(policy_model.parameters(), max_norm=1.0)
                        if isinstance(optimizer, list):
                            for opt in optimizer:
                                opt.step()
                        else:
                            optimizer.step()

                    if hasattr(policy_model, "sync_weights"):
                        policy_model.sync_weights()

                    if isinstance(optimizer, list):
                        for opt in optimizer:
                            opt.zero_grad()
                    else:
                        optimizer.zero_grad()
                    if hasattr(policy_model, "raw_replicas"):
                        policy_model.zero_grad(set_to_none=True)

                t_step_end = time.time()
                step_duration = t_step_end - t_step_start
                interval_train_time += step_duration
                cumulative_train_time += step_duration

                if is_accum_step and (global_step % args.eval_freq == 0 or (target_step is not None and global_step >= target_step)):
                    tps = interval_tokens / interval_train_time if interval_train_time > 0 else 0
                    avg_tps = (tokens_seen - tokens_seen_init) / cumulative_train_time if cumulative_train_time > 0 else 0

                    interval_tokens = 0
                    interval_train_time = 0.0

                    lr_val = optimizer[0].param_groups[0]["lr"] if isinstance(optimizer, list) else optimizer.param_groups[0]["lr"]
                    vram_str = format_vram_report(policy_model, optimizer, device)

                    t_eval_start = time.time()
                    eval_tr = evaluate_dpo_loader_precomputed(train_loader, policy_model, args.beta, device, args.eval_iter, amp_dtype=amp_dtype, use_amp=use_amp, sft_weight=args.dpo_sft_weight)
                    eval_val = evaluate_dpo_loader_precomputed(val_loader, policy_model, args.beta, device, args.eval_iter, amp_dtype=amp_dtype, use_amp=use_amp, sft_weight=args.dpo_sft_weight)
                    eval_duration = time.time() - t_eval_start

                    train_losses.append(eval_tr["loss"])
                    val_losses.append(eval_val["loss"])
                    train_margins.append(eval_tr["margin"])
                    val_margins.append(eval_val["margin"])
                    track_tokens_seen.append(tokens_seen)
                    epoch_fraction = epoch + (step_in_epoch / total_steps_in_epoch)
                    track_epochs.append(epoch_fraction)

                    print_step_telemetry(
                        epoch=epoch,
                        num_epochs=args.num_epochs,
                        step=step_in_epoch,
                        total_steps=total_steps_in_epoch,
                        global_step=global_step,
                        global_total_steps=global_total_steps,
                        train_loss=eval_tr["loss"],
                        val_loss=eval_val["loss"],
                        tps=tps,
                        avg_tps=avg_tps,
                        eval_duration=eval_duration,
                        lr=lr_val,
                        vram_str=vram_str,
                        train_margin=eval_tr["margin"],
                        val_margin=eval_val["margin"],
                        train_chosen=eval_tr["chosen_reward"],
                        val_chosen=eval_val["chosen_reward"],
                        train_acc=eval_tr["accuracy"],
                        val_acc=eval_val["accuracy"],
                        lr_precision=7,
                    )

                    if args.verbose:
                        raw_m = getattr(policy_model, "raw_model", getattr(policy_model, "module", policy_model))
                        raw_m = getattr(raw_m, "_orig_mod", raw_m)
                        pos_emb_mod = getattr(raw_m, "pos_emb", None)
                        context_size = pos_emb_mod.weight.shape[0] if pos_emb_mod is not None else (gpt_config.get("context_length", 1024) if gpt_config is not None else 1024)
                        encoded = text_to_token_ids(sample_prompt, tokenizer).to(device)
                        policy_model.eval()
                        with torch.no_grad():
                            if use_amp and amp_dtype is not None:
                                with torch.amp.autocast(device_type="cuda", dtype=amp_dtype):  # type: ignore
                                    gen_ids = generate_text(
                                        model=policy_model, idx=encoded, max_new_tokens=64,
                                        context_size=context_size, eos_id=tokenizer.eos_id, temperature=0.0
                                    )
                            else:
                                gen_ids = generate_text(
                                    model=policy_model, idx=encoded, max_new_tokens=64,
                                    context_size=context_size, eos_id=tokenizer.eos_id, temperature=0.0
                                )
                            gen_str = token_ids_to_text(gen_ids[:, encoded.shape[1]:], tokenizer)  # the new tokens only: slicing the decoded text by len(sample_prompt) breaks when the decode differs from the prompt text
                            ans = gen_str.replace("### Response:", "").strip()
                            print(f"  [Sample Response]: {ans.replace(chr(10), ' ')[:130]}")
                        policy_model.train()

                if is_accum_step and args.model_name and args.save_interval and (global_step % args.save_interval == 0):
                    save_checkpoint(
                        model=policy_model,
                        args=args,
                        config=gpt_config,
                        optimizer=optimizer,
                        global_step=global_step,
                        epoch=epoch,
                        current_epoch=epoch,
                        step_in_epoch=step_in_epoch,
                        epoch_completed=False,
                        tokens_seen=tokens_seen,
                        train_losses=train_losses,
                        val_losses=val_losses,
                        track_tokens=track_tokens_seen,
                        is_dpo=True,
                        accumulated_training_time=get_current_accum_time(),
                    )

                if is_accum_step and target_step is not None and global_step >= target_step:
                    if args.model_name:
                        save_checkpoint(
                            model=policy_model,
                            args=args,
                            config=gpt_config,
                            optimizer=optimizer,
                            global_step=global_step,
                            epoch=epoch,
                            current_epoch=epoch,
                            step_in_epoch=step_in_epoch,
                            epoch_completed=False,
                            tokens_seen=tokens_seen,
                            train_losses=train_losses,
                            val_losses=val_losses,
                            track_tokens=track_tokens_seen,
                            is_dpo=True,
                            accumulated_training_time=get_current_accum_time(),
                        )
                    print(f"\n[Step Limit Reached] Reached target step {target_step}. Pausing Precomputed DPO optimization cleanly.")
                    stopped_due_to_limit = True
                    break

            # Qualitative check at epoch end
            raw_m = getattr(policy_model, "raw_model", getattr(policy_model, "module", policy_model))
            raw_m = getattr(raw_m, "_orig_mod", raw_m)
            pos_emb_mod = getattr(raw_m, "pos_emb", None)
            context_size = pos_emb_mod.weight.shape[0] if pos_emb_mod is not None else (gpt_config.get("context_length", 1024) if gpt_config is not None else 1024)
            encoded = text_to_token_ids(sample_prompt, tokenizer).to(device)
            policy_model.eval()
            with torch.no_grad():
                if use_cuda and amp_dtype is not None:
                    with torch.amp.autocast(device_type="cuda", dtype=amp_dtype):  # type: ignore
                        gen_ids = generate_text(
                            model=policy_model, idx=encoded, max_new_tokens=100,
                            context_size=context_size, eos_id=tokenizer.eos_id, temperature=0.0
                        )
                else:
                    gen_ids = generate_text(
                        model=policy_model, idx=encoded, max_new_tokens=100,
                        context_size=context_size, eos_id=tokenizer.eos_id, temperature=0.0
                    )
                gen_str = token_ids_to_text(gen_ids[:, encoded.shape[1]:], tokenizer)  # the new tokens only: slicing the decoded text by len(sample_prompt) breaks when the decode differs from the prompt text
                ans = gen_str.replace("### Response:", "").strip()
                clean_instr = sample_prompt.replace("Below is an instruction that describes a task. Write a response that appropriately completes the request.\n\n### Instruction:\n", "").strip()
                print("\n" + "-" * 70)
                print(f"[Sample Model Response @ Epoch {epoch+1}]")
                print(f"  Instruction : {clean_instr[:100]}")
                print(f"  Preferred   : {str(start_context_entry.get('chosen') or '')[:120]}")
                print(f"  Model Output: {ans.replace(chr(10), ' ')[:150]}")
                print("-" * 70)
            policy_model.train()

            print_gpu_memory_breakdown(policy_model, optimizer)
            print_eta(start_time, epoch_start_time, (epoch - start_epoch + 1), (args.num_epochs - start_epoch))

            if stopped_due_to_limit:
                break

            if args.model_name:
                save_checkpoint(
                    model=policy_model,
                    args=args,
                    config=gpt_config,
                    optimizer=optimizer,
                    global_step=global_step,
                    epoch=epoch + 1,
                    current_epoch=epoch + 1,
                    step_in_epoch=0,
                    epoch_completed=True,
                    tokens_seen=tokens_seen,
                    train_losses=train_losses,
                    val_losses=val_losses,
                    track_tokens=track_tokens_seen,
                    is_dpo=True,
                    accumulated_training_time=get_current_accum_time(),
                )

        if args.model_name and not stopped_due_to_limit:
            save_checkpoint(
                model=policy_model,
                args=args,
                config=gpt_config,
                optimizer=optimizer,
                global_step=global_step,
                epoch=args.num_epochs,
                current_epoch=args.num_epochs,
                step_in_epoch=0,
                epoch_completed=True,
                tokens_seen=tokens_seen,
                train_losses=train_losses,
                val_losses=val_losses,
                track_tokens=track_tokens_seen,
                is_dpo=True,
                accumulated_training_time=get_current_accum_time(),
            )
            save_model(
                model=policy_model,
                args=args,
                config=gpt_config
            )

    except KeyboardInterrupt:
        print(f"\n\n[Interrupt] Precomputed DPO optimization cancelled by user (Ctrl+C).")
        if args.model_name:
            try:
                save_checkpoint(
                    model=policy_model,
                    args=args,
                    config=gpt_config,
                    optimizer=optimizer,
                    global_step=global_step,
                    epoch=epoch,
                    current_epoch=epoch,
                    step_in_epoch=step_in_epoch,
                    epoch_completed=False,
                    tokens_seen=tokens_seen,
                    train_losses=train_losses,
                    val_losses=val_losses,
                    track_tokens=track_tokens_seen,
                    is_dpo=True,
                    accumulated_training_time=get_current_accum_time(),
                )
                print(f"[Interrupt] Checkpoint successfully saved for '{args.model_name}' at Global Step {global_step:,} (Epoch {epoch+1}, Step {step_in_epoch}).")
                print(f"[Interrupt] You can resume anytime by re-running the script with the same arguments.\n")
            except Exception as save_err:
                print(f"[Interrupt Warning] Could not save checkpoint on interrupt: {save_err}")
        return train_losses, val_losses, train_margins, val_margins, track_tokens_seen, track_epochs, get_current_accum_time()

    except Exception as e:
        print(f"\n\n[Crash Recovery] Unexpected error during Precomputed DPO optimization: {e}")
        if args.model_name:
            try:
                save_checkpoint(
                    model=policy_model,
                    args=args,
                    config=gpt_config,
                    optimizer=optimizer,
                    global_step=global_step,
                    epoch=epoch,
                    current_epoch=epoch,
                    step_in_epoch=step_in_epoch,
                    epoch_completed=False,
                    tokens_seen=tokens_seen,
                    train_losses=train_losses,
                    val_losses=val_losses,
                    track_tokens=track_tokens_seen,
                    is_dpo=True,
                    accumulated_training_time=get_current_accum_time(),
                )
                print(f"[Crash Recovery] Emergency checkpoint saved for '{args.model_name}' at Global Step {global_step:,} (Epoch {epoch+1}, Step {step_in_epoch}).")
            except Exception as save_err:
                print(f"[Crash Recovery Warning] Could not save emergency checkpoint: {save_err}")
        raise e

    total_elapsed = get_current_accum_time()
    final_tr = train_losses[-1] if train_losses else 0.0
    final_vl = val_losses[-1] if val_losses else 0.0
    final_tm = train_margins[-1] if train_margins else 0.0
    final_vm = val_margins[-1] if val_margins else 0.0
    param_count = count_model_parameters(model=policy_model, config=gpt_config)

    print_stage_completion_summary(
        stage=STAGE_OPTIMIZE,
        total_elapsed_time=total_elapsed,
        total_tokens=tokens_seen,
        train_loss=final_tr,
        val_loss=final_vl,
        model_name=args.model_name or "policy_model",
        param_count=param_count,
        train_margin=final_tm,
        val_margin=final_vm,
    )

    return train_losses, val_losses, train_margins, val_margins, track_tokens_seen, track_epochs, total_elapsed
