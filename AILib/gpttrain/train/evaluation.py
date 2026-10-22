# Copyright (c) Sebastian Raschka under Apache License 2.0 (see LICENSE.txt).
# Evaluation and loss computation routines for GPT training.

from contextlib import nullcontext
from pathlib import Path
import sys
from typing import Any, Optional, Tuple, Union

import torch
import torch.nn as nn
import torch.nn.functional as F

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from gptmodel.GptModel import LOGIT_CLAMP_MIN, LOGIT_CLAMP_MAX
from gptinfer.inference import generate_text
from gptutils.consoleutils import print


def text_to_token_ids(text: str, tokenizer: Any) -> torch.Tensor:
    encoded = tokenizer.encode(text)
    return torch.tensor(encoded).unsqueeze(0)


def token_ids_to_text(token_ids: torch.Tensor, tokenizer: Any) -> str:
    return tokenizer.decode(token_ids.squeeze(0).tolist())


def calc_loss_batch(
    input_batch: torch.Tensor,
    target_batch: torch.Tensor,
    model: nn.Module,
    device: torch.device,
    amp_dtype: Optional[torch.dtype] = None,
    chunk_size: int = 512,
    use_1f1b: bool = False,
    multi_stage_micro_batching: int = 0,
    accum_steps: int = 1,
    return_backward_status: bool = False,
    activation_checkpointing: bool = False,
    use_amp: Optional[bool] = None,
    scaler: Optional[Any] = None,
    seq_target_batch: Optional[torch.Tensor] = None,
    autocast_weight_cache: bool = False,
) -> Any:
    """seq_target_batch: optional second target mask scored on the same forward pass; when given, returns (loss, seq_loss).
    autocast_weight_cache (--use_autocast_weight_cache): autocast's weight cache for the single-GPU forward; never with activation checkpointing."""
    raw_model = getattr(model, "raw_model", getattr(model, "module", model))
    raw_model = getattr(raw_model, "_orig_mod", raw_model)

    first_device = getattr(model, "first_device", device)
    last_device = getattr(model, "last_device", device)

    if use_amp is None:
        dev_type = device.type if hasattr(device, "type") else torch.device(device).type
        use_amp = (dev_type == "cuda" and amp_dtype is not None and amp_dtype != torch.float32)

    should_autocast = use_amp and amp_dtype is not None and amp_dtype != torch.float32

    # Data-Parallel Multi-GPU Execution
    if hasattr(model, "forward_backward_dp") and input_batch.shape[0] >= 2:
        res = model.forward_backward_dp(
            input_batch, target_batch,
            chunk_size=chunk_size, accum_steps=accum_steps,
            activation_checkpointing=activation_checkpointing,
            amp_dtype=amp_dtype if should_autocast else None,
            scaler=scaler
        )
        return res if return_backward_status else res[0]

    # Multi-Stage Pipelined Execution (Forward and Backward overlapping across GPUs)
    effective_stages = multi_stage_micro_batching
    if effective_stages == 0 and use_1f1b:
        effective_stages = 2

    if effective_stages >= 2 and hasattr(model, "forward_backward_multi_stage_pipelined") and input_batch.shape[0] >= 2:
        if should_autocast:
            with torch.amp.autocast(device_type="cuda", dtype=amp_dtype, cache_enabled=not activation_checkpointing):
                res = model.forward_backward_multi_stage_pipelined(
                    input_batch, target_batch, num_micro_batches=effective_stages,
                    chunk_size=chunk_size, accum_steps=accum_steps,
                    activation_checkpointing=activation_checkpointing
                )
        else:
            res = model.forward_backward_multi_stage_pipelined(
                input_batch, target_batch, num_micro_batches=effective_stages,
                chunk_size=chunk_size, accum_steps=accum_steps,
                activation_checkpointing=activation_checkpointing
            )
        return res if return_backward_status else res[0]

    input_batch = input_batch.to(first_device, non_blocking=True)
    target_batch = target_batch.to(last_device, non_blocking=True)
    forward_features = getattr(model, "compiled_forward_features", getattr(model, "forward_features", None))
    chunked_loss = getattr(raw_model, "compiled_chunked_loss", getattr(raw_model, "chunked_loss", None))

    def _ce(logits, tgt):
        flat_targets = tgt.flatten()
        active_tokens = (flat_targets != -100).sum()
        return (logits.flatten(0, 1) * 0.0).sum() if active_tokens == 0 else F.cross_entropy(logits.flatten(0, 1), flat_targets)

    # cache_enabled=False by default: with activation checkpointing the cache would pin the bf16 copy of every weight until the forward ends (~2 bytes
    # per parameter); without it the cache makes the loss chunks share one copy of the LM head, so autograd sums their partial gradients in the
    # autocast dtype instead of fp32 (measured: 2.8e-4 relative change of the head gradient in fp16). --use_autocast_weight_cache opts into that
    # trade for the memory ((chunks - 1) head copies); --recompute_lmhead frees those copies exactly.
    with (torch.amp.autocast(device_type="cuda", dtype=amp_dtype, cache_enabled=autocast_weight_cache and not activation_checkpointing) if should_autocast else nullcontext()):
        if hasattr(model, "forward_features"):
            hidden = forward_features(input_batch, activation_checkpointing=activation_checkpointing)
            loss_fn = lambda tgt: chunked_loss(hidden, tgt, chunk_size)
        else:
            logits = torch.clamp(model(input_batch, activation_checkpointing=activation_checkpointing).float(), min=LOGIT_CLAMP_MIN, max=LOGIT_CLAMP_MAX)
            loss_fn = lambda tgt: _ce(logits, tgt)
        loss = loss_fn(target_batch)
        if seq_target_batch is not None:  # same forward pass, second target mask
            loss = (loss, loss_fn(seq_target_batch.to(last_device, non_blocking=True)))

    return (loss, False) if return_backward_status else loss


def calc_loss_loader(
    data_loader: Any,
    model: nn.Module,
    device: torch.device,
    num_batches: Optional[int] = None,
    amp_dtype: Optional[torch.dtype] = None,
    use_1f1b: bool = False,
    multi_stage_micro_batching: int = 0,
    activation_checkpointing: bool = False,
    use_amp: Optional[bool] = None,
    chunk_size: int = 512,
    return_seq_loss: bool = False,
) -> Any:
    total_loss = 0.0
    total_seq_loss = 0.0
    has_seq = False
    if data_loader is None or len(data_loader) == 0:
        return (float("nan"), float("nan")) if return_seq_loss else float("nan")
    num_batches = len(data_loader) if num_batches is None else min(num_batches, len(data_loader))
    actual_batches = 0
    for i, batch in enumerate(data_loader):
        if i >= num_batches:
            break
        actual_batches += 1
        if isinstance(batch, (list, tuple)) and len(batch) >= 3:
            input_batch, target_batch, seq_target_batch = batch[0], batch[1], batch[2]
            has_seq = True
        else:
            input_batch, target_batch = batch[0], batch[1]
            seq_target_batch = None

        want_seq = return_seq_loss and seq_target_batch is not None
        loss = calc_loss_batch(input_batch, target_batch, model, device, amp_dtype=amp_dtype,
                               use_1f1b=use_1f1b,
                               multi_stage_micro_batching=multi_stage_micro_batching,
                               activation_checkpointing=activation_checkpointing,
                               use_amp=use_amp, chunk_size=chunk_size,
                               seq_target_batch=seq_target_batch if want_seq else None)  # both masks scored on one forward pass
        if want_seq and not isinstance(loss, tuple):  # multi-GPU paths return early without the second mask: fall back to a second pass
            loss = (loss, calc_loss_batch(input_batch, seq_target_batch, model, device, amp_dtype=amp_dtype,
                                          use_1f1b=use_1f1b,
                                          multi_stage_micro_batching=multi_stage_micro_batching,
                                          activation_checkpointing=activation_checkpointing,
                                          use_amp=use_amp, chunk_size=chunk_size))
        if want_seq:
            total_seq_loss += loss[1].item()
            loss = loss[0]
        total_loss += loss.item()

    if actual_batches == 0:
        return (float("nan"), float("nan")) if return_seq_loss else float("nan")

    avg_loss = total_loss / actual_batches
    if return_seq_loss:
        avg_seq_loss = (total_seq_loss / actual_batches) if has_seq else None
        return avg_loss, avg_seq_loss
    return avg_loss


def evaluate_model(
    model: nn.Module,
    train_loader: Any,
    val_loader: Any,
    device: torch.device,
    eval_iter: int,
    amp_dtype: Optional[torch.dtype] = None,
    use_1f1b: bool = False,
    multi_stage_micro_batching: int = 0,
    use_amp: Optional[bool] = None,
    chunk_size: int = 512,
    return_seq_loss: bool = False,
) -> Any:
    model.eval()
    with torch.no_grad():
        if return_seq_loss:
            train_res = calc_loss_loader(train_loader, model, device, num_batches=eval_iter, amp_dtype=amp_dtype,
                                          use_1f1b=use_1f1b,
                                          multi_stage_micro_batching=multi_stage_micro_batching,
                                          activation_checkpointing=False,
                                          use_amp=use_amp, chunk_size=chunk_size, return_seq_loss=True)
            val_res = calc_loss_loader(val_loader, model, device, num_batches=eval_iter, amp_dtype=amp_dtype,
                                        use_1f1b=use_1f1b,
                                        multi_stage_micro_batching=multi_stage_micro_batching,
                                        activation_checkpointing=False,
                                        use_amp=use_amp, chunk_size=chunk_size, return_seq_loss=True)
            model.train()
            train_loss, train_seq = train_res if isinstance(train_res, tuple) else (train_res, None)
            val_loss, val_seq = val_res if isinstance(val_res, tuple) else (val_res, None)
            return train_loss, val_loss, train_seq, val_seq
        else:
            train_loss = calc_loss_loader(train_loader, model, device, num_batches=eval_iter, amp_dtype=amp_dtype,
                                          use_1f1b=use_1f1b,
                                          multi_stage_micro_batching=multi_stage_micro_batching,
                                          activation_checkpointing=False,
                                          use_amp=use_amp, chunk_size=chunk_size)
            val_loss = calc_loss_loader(val_loader, model, device, num_batches=eval_iter, amp_dtype=amp_dtype,
                                        use_1f1b=use_1f1b,
                                        multi_stage_micro_batching=multi_stage_micro_batching,
                                        activation_checkpointing=False,
                                        use_amp=use_amp, chunk_size=chunk_size)
            model.train()
            return train_loss, val_loss


def generate_and_print_sample(
    model: nn.Module,
    tokenizer: Any,
    device: torch.device,
    start_context: str,
    temperature: float = 0.0,
    top_k: Optional[int] = None,
) -> None:
    model.eval()
    raw_model = getattr(model, "raw_model", getattr(model, "module", model))
    raw_model = getattr(raw_model, "_orig_mod", raw_model)
    first_device = getattr(model, "first_device", device)
    pos_emb_mod = getattr(raw_model, "pos_emb", None)
    context_size = pos_emb_mod.weight.shape[0] if pos_emb_mod is not None else getattr(raw_model, "cfg", {}).get("context_length", 1024)

    encoded = text_to_token_ids(start_context, tokenizer).to(first_device)
    with torch.no_grad():
        token_ids = generate_text(
            model=model,
            idx=encoded,
            max_new_tokens=50,
            context_size=context_size,
            temperature=temperature,
            top_k=top_k,
        )
        decoded_text = token_ids_to_text(token_ids, tokenizer)
        out_encoding = sys.stdout.encoding or "utf-8"
        safe_text = decoded_text.encode(out_encoding, errors="replace").decode(out_encoding, errors="replace")
        print(f"Sample: {safe_text.replace(chr(10), ' ')}")
    model.train()
