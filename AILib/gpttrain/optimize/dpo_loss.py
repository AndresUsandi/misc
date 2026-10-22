# Copyright (c) Sebastian Raschka under Apache License 2.0 (see LICENSE.txt).
# Fused log-probability computation and Direct Preference Optimization (DPO) loss routines.

from contextlib import nullcontext
from typing import Any, Dict, Optional, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.utils.checkpoint
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


def compute_logprobs_chunked(
    hidden: torch.Tensor,
    labels: torch.Tensor,
    selection_mask: Optional[torch.Tensor],
    out_head: nn.Module,
    chunk_size: int,
) -> torch.Tensor:
    """Computes sequence log-probabilities without retaining full-vocabulary logits."""
    shift_hidden = hidden[:, :-1, :]
    shift_labels = labels[:, 1:].contiguous()
    shift_mask = selection_mask[:, 1:].to(dtype=torch.float32) if selection_mask is not None else torch.ones_like(shift_labels, dtype=torch.float32)

    def chunk_logprobs(h: torch.Tensor, y: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
        return -F.cross_entropy(out_head(h), y, reduction="none") * mask

    # Chunks of chunk_size tokens over the flattened batch (as GptModel.chunked_loss): the head projection + fp32 softmax of a chunk is the
    # peak-memory term and this keeps it independent of how many sequences the token-budget packer put into the batch.
    flat_hidden, flat_labels, flat_mask = shift_hidden.reshape(-1, shift_hidden.shape[-1]), shift_labels.reshape(-1), shift_mask.reshape(-1)
    num_chunks = max(1, -(-flat_labels.numel() // max(1, chunk_size)))
    parts = [torch.utils.checkpoint.checkpoint(chunk_logprobs, h, y, m, use_reentrant=False) if flat_hidden.requires_grad else chunk_logprobs(h, y, m)
             for h, y, m in zip(flat_hidden.tensor_split(num_chunks), flat_labels.tensor_split(num_chunks), flat_mask.tensor_split(num_chunks))]
    return torch.cat(parts).view(shift_mask.shape).sum(dim=1) / shift_mask.sum(dim=1).clamp(min=1.0)


def compute_dpo_loss(
    model_chosen_logprobs: torch.Tensor,
    model_rejected_logprobs: torch.Tensor,
    reference_chosen_logprobs: torch.Tensor,
    reference_rejected_logprobs: torch.Tensor,
    beta: float = 0.1,
    sft_weight: float = 0.0,
) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
    """
    Computes Direct Preference Optimization loss and tracking rewards (Rafailov et al. 2023).
    sft_weight > 0 adds sft_weight x the per-token negative log-likelihood of the chosen answer (the ordinary SFT loss) to the DPO loss
    (the RPO / Llama 3 "NLL on chosen" term). Plain DPO only rewards a growing gap between chosen and rejected, so it is also minimised
    by making both answers less likely as long as the rejected one falls faster; the probability then flows to something degenerate
    (andres-350M-2-fp8v2c, 2026-10-14: "stop after three words"). The NLL term keeps the chosen answers themselves likely.
    """
    model_logratios = model_chosen_logprobs - model_rejected_logprobs
    reference_logratios = reference_chosen_logprobs - reference_rejected_logprobs
    logits = model_logratios - reference_logratios

    losses = -F.logsigmoid(beta * logits) - sft_weight * model_chosen_logprobs  # logprobs are per-token means, so this is the mean token NLL of the chosen answer

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
    chunk_size: int = 256,
    backward_accum_steps: Optional[int] = None,
    scaler: Optional[Any] = None,
    sft_weight: float = 0.0,
) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
    """
    Runs policy and reference models on chosen and rejected sequences with AMP autocast
    and computes batch DPO loss, reward margins, and preference accuracy.
    backward_accum_steps: when given, also runs the (scaled, accumulation-divided) backward and returns a detached loss.
    """
    if hasattr(policy_model, "forward_backward_dpo"):  # MultiGpuGptModelDP / ZeRO-1: the pairs are split across the GPUs, each scoring its share with its own policy and reference copy
        return policy_model.forward_backward_dpo(batch, compute_dpo_loss_batch, amp_dtype=amp_dtype, beta=beta, activation_checkpointing=activation_checkpointing, use_amp=use_amp, chunk_size=chunk_size, backward_accum_steps=backward_accum_steps, scaler=scaler, sft_weight=sft_weight)
    if ref_device is None:
        ref_device = policy_device

    chosen_in = batch["chosen"].to(policy_device)
    chosen_mask = batch["chosen_mask"].to(policy_device)
    rejected_in = batch["rejected"].to(policy_device)
    rejected_mask = batch["rejected_mask"].to(policy_device)

    use_cuda = policy_device.type == "cuda"
    if use_amp is None:
        use_amp = (use_cuda and amp_dtype is not None and amp_dtype != torch.float32)
    autocast_ctx = torch.amp.autocast(device_type="cuda", dtype=amp_dtype, cache_enabled=False) if (use_amp and amp_dtype is not None) else nullcontext()  # type: ignore
    policy_forward = getattr(policy_model, "compiled_forward_features", policy_model.forward_features)  # --compile (model_setup) attaches the compiled variant
    ref_forward = getattr(reference_model, "compiled_forward_features", reference_model.forward_features)

    # Policy model forward passes
    with autocast_ctx:
        policy_chosen_hidden = policy_forward(chosen_in, activation_checkpointing=activation_checkpointing)
        policy_chosen_logprobs = compute_logprobs_chunked(policy_chosen_hidden, chosen_in, chosen_mask, policy_model.out_head, chunk_size)
        del policy_chosen_hidden

        policy_rejected_hidden = policy_forward(rejected_in, activation_checkpointing=activation_checkpointing)
        policy_rejected_logprobs = compute_logprobs_chunked(policy_rejected_hidden, rejected_in, rejected_mask, policy_model.out_head, chunk_size)
        del policy_rejected_hidden

    # Reference model forward passes (frozen under torch.no_grad, native amp_dtype; cache_enabled=False as for the policy: the cast cache is
    # process-global and the data-parallel worker threads would race on it under torch.compile)
    ref_autocast_ctx = torch.amp.autocast(device_type="cuda", dtype=amp_dtype, cache_enabled=False) if (ref_device.type == "cuda" and use_amp and amp_dtype is not None) else nullcontext()  # type: ignore
    with torch.no_grad(), ref_autocast_ctx:
        ref_chosen_in = chosen_in.to(ref_device)
        ref_chosen_mask = chosen_mask.to(ref_device)
        ref_rejected_in = rejected_in.to(ref_device)
        ref_rejected_mask = rejected_mask.to(ref_device)

        ref_chosen_hidden = ref_forward(ref_chosen_in)
        ref_chosen_logprobs = compute_logprobs_chunked(ref_chosen_hidden, ref_chosen_in, ref_chosen_mask, reference_model.out_head, chunk_size).to(policy_device)
        del ref_chosen_hidden

        ref_rejected_hidden = ref_forward(ref_rejected_in)
        ref_rejected_logprobs = compute_logprobs_chunked(ref_rejected_hidden, ref_rejected_in, ref_rejected_mask, reference_model.out_head, chunk_size).to(policy_device)
        del ref_rejected_hidden

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


def split_dpo_backward(loss: torch.Tensor, policy_chosen_logprobs: torch.Tensor, policy_rejected_logprobs: torch.Tensor,
                       accum_steps: int, scaler: Optional[Any] = None) -> torch.Tensor:
    """Backward as two single-graph passes. One backward over both policy graphs makes autograd finish the rejected pass first
    and park a second full copy of every weight gradient until the chosen pass arrives (2.7 GiB for gpt2-774M)."""
    scaled = (scaler.scale(loss) if scaler else loss) / accum_steps
    g_chosen, g_rejected = torch.autograd.grad(scaled, [policy_chosen_logprobs, policy_rejected_logprobs])
    policy_rejected_logprobs.backward(g_rejected)
    policy_chosen_logprobs.backward(g_chosen)
    return loss.detach()


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
    sft_weight: float = 0.0,
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
