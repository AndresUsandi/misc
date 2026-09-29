# Copyright (c) Sebastian Raschka under Apache License 2.0 (see LICENSE.txt).
# Fused log-probability computation and Direct Preference Optimization (DPO) loss routines.

from contextlib import nullcontext
from typing import Any, Dict, Optional, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader


def compute_logprobs(
    logits: torch.Tensor,
    labels: torch.Tensor,
    selection_mask: Optional[torch.Tensor] = None
) -> torch.Tensor:
    """
    Computes sequence log probabilities for given labels without materializing
    the massive (B, S, V) log_softmax tensor in VRAM.
    Uses the mathematical identity: log P(y|x) = -cross_entropy(logits, labels, reduction='none')
    """
    shift_labels = labels[:, 1:].contiguous()
    shift_logits = logits[:, :-1, :].contiguous()

    batch_size, seq_len, vocab_size = shift_logits.shape

    # Native fused cross-entropy avoids allocating the (B, S, V) float tensor
    per_token_neg_loss = -F.cross_entropy(
        shift_logits.view(batch_size * seq_len, vocab_size),
        shift_labels.view(batch_size * seq_len),
        reduction="none"
    ).view(batch_size, seq_len)

    if selection_mask is not None:
        shift_mask = selection_mask[:, 1:].contiguous().to(dtype=per_token_neg_loss.dtype)
        selected_log_probs = per_token_neg_loss * shift_mask
        denom = shift_mask.sum(dim=-1).clamp(min=1.0)
        return selected_log_probs.sum(dim=-1) / denom
    else:
        return per_token_neg_loss.mean(dim=-1)


def compute_dpo_loss(
    model_chosen_logprobs: torch.Tensor,
    model_rejected_logprobs: torch.Tensor,
    reference_chosen_logprobs: torch.Tensor,
    reference_rejected_logprobs: torch.Tensor,
    beta: float = 0.1,
) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
    """
    Computes Direct Preference Optimization loss and tracking rewards (Rafailov et al. 2023).
    """
    model_logratios = model_chosen_logprobs - model_rejected_logprobs
    reference_logratios = reference_chosen_logprobs - reference_rejected_logprobs
    logits = model_logratios - reference_logratios

    losses = -F.logsigmoid(beta * logits)

    chosen_rewards = (model_chosen_logprobs - reference_chosen_logprobs).detach()
    rejected_rewards = (model_rejected_logprobs - reference_rejected_logprobs).detach()
    reward_margins = (chosen_rewards - rejected_rewards).detach()
    accuracy = (logits > 0).float().detach()

    return losses.mean(), chosen_rewards.mean(), rejected_rewards.mean(), reward_margins.mean(), accuracy.mean()


def compute_dpo_loss_batch(
    batch: Dict[str, Any],
    policy_model: nn.Module,
    reference_model: nn.Module,
    beta: float = 0.1,
    policy_device: torch.device = torch.device("cpu"),
    ref_device: Optional[torch.device] = None,
    amp_dtype: Optional[torch.dtype] = None,
    activation_checkpointing: bool = False,
    use_amp: Optional[bool] = None,
) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
    """
    Runs policy and reference models on chosen and rejected sequences with AMP autocast
    and computes batch DPO loss, reward margins, and preference accuracy.
    """
    if ref_device is None:
        ref_device = policy_device

    chosen_in = batch["chosen"].to(policy_device)
    chosen_mask = batch["chosen_mask"].to(policy_device)
    rejected_in = batch["rejected"].to(policy_device)
    rejected_mask = batch["rejected_mask"].to(policy_device)

    use_cuda = policy_device.type == "cuda"
    if use_amp is None:
        use_amp = (use_cuda and amp_dtype is not None and amp_dtype != torch.float32)
    autocast_ctx = torch.amp.autocast(device_type="cuda", dtype=amp_dtype) if (use_amp and amp_dtype is not None) else nullcontext()  # type: ignore

    # Policy model forward passes
    with autocast_ctx:
        policy_chosen_logits = policy_model(chosen_in, activation_checkpointing=activation_checkpointing)
        policy_chosen_logprobs = compute_logprobs(
            logits=policy_chosen_logits,
            labels=chosen_in,
            selection_mask=chosen_mask
        )
        del policy_chosen_logits

        policy_rejected_logits = policy_model(rejected_in, activation_checkpointing=activation_checkpointing)
        policy_rejected_logprobs = compute_logprobs(
            logits=policy_rejected_logits,
            labels=rejected_in,
            selection_mask=rejected_mask
        )
        del policy_rejected_logits

    # Reference model forward passes (frozen under torch.no_grad, native amp_dtype)
    ref_autocast_ctx = torch.amp.autocast(device_type="cuda", dtype=amp_dtype) if (ref_device.type == "cuda" and use_amp and amp_dtype is not None) else nullcontext()  # type: ignore
    with torch.no_grad(), ref_autocast_ctx:
        ref_chosen_in = chosen_in.to(ref_device)
        ref_chosen_mask = chosen_mask.to(ref_device)
        ref_rejected_in = rejected_in.to(ref_device)
        ref_rejected_mask = rejected_mask.to(ref_device)

        ref_chosen_logits = reference_model(ref_chosen_in)
        ref_chosen_logprobs = compute_logprobs(
            logits=ref_chosen_logits,
            labels=ref_chosen_in,
            selection_mask=ref_chosen_mask
        ).to(policy_device)
        del ref_chosen_logits

        ref_rejected_logits = reference_model(ref_rejected_in)
        ref_rejected_logprobs = compute_logprobs(
            logits=ref_rejected_logits,
            labels=ref_rejected_in,
            selection_mask=ref_rejected_mask
        ).to(policy_device)
        del ref_rejected_logits

    loss, chosen_rewards, rejected_rewards, reward_margins, accuracy = compute_dpo_loss(
        model_chosen_logprobs=policy_chosen_logprobs,
        model_rejected_logprobs=policy_rejected_logprobs,
        reference_chosen_logprobs=ref_chosen_logprobs,
        reference_rejected_logprobs=ref_rejected_logprobs,
        beta=beta
    )

    return loss, chosen_rewards, rejected_rewards, reward_margins, accuracy


def evaluate_dpo_loader(
    data_loader: DataLoader,
    policy_model: nn.Module,
    reference_model: nn.Module,
    beta: float = 0.1,
    policy_device: torch.device = torch.device("cpu"),
    ref_device: Optional[torch.device] = None,
    num_batches: Optional[int] = None,
    amp_dtype: Optional[torch.dtype] = None,
    use_amp: Optional[bool] = None,
) -> Dict[str, float]:
    """
    Computes average DPO loss, reward margin, and accuracy across num_batches of a DataLoader.
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
            loss, chosen_rewards, rejected_rewards, reward_margins, acc = compute_dpo_loss_batch(
                batch=batch,
                policy_model=policy_model,
                reference_model=reference_model,
                beta=beta,
                policy_device=policy_device,
                ref_device=ref_device,
                amp_dtype=amp_dtype,
                activation_checkpointing=False,
                use_amp=use_amp,
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
