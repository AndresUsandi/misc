# Copyright (c) Sebastian Raschka under Apache License 2.0 (see LICENSE.txt).
# Fully-Optimized Instruction Fine-Tuning Engine for GPT LLMs (Chapter 7 SFT)

import math
from pathlib import Path
import sys
import time
from typing import Any, Dict, List, Optional, Tuple, Union

import torch
import torch.nn as nn
from torch.utils.data import DataLoader

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from argsutil import TrainingArgs
from gptmodel.Dataset import format_input, plan_provenance
from gpttrain.train.evaluation import (
    calc_loss_batch,
    evaluate_model,
    text_to_token_ids,
    token_ids_to_text,
)
from gptio.checkpoint import save_checkpoint
from gptio.modelio import save_model
from gptio.precision import create_grad_scaler
from gpttrain.optimizer import lr_schedule_from_resume, set_optimizer_lr
from gpttrain.tune.scheduler import get_cosine_lr_with_warmup
from gptutils.consoleutils import (
    print,
    format_vram_report,
    print_gpu_memory_breakdown,
    print_step_telemetry,
    print_eta,
)
from gptutils.metrics import calculate_perplexity
from gptinfer.inference import generate_text


def train_model_instruction_fully_optimized(
    model: nn.Module,
    train_loader: DataLoader,
    val_loader: DataLoader,
    optimizer: Any,
    device: torch.device,
    args: TrainingArgs,
    start_context_entry: Dict[str, Any],
    tokenizer: Any,
    resumed_step: int = 0,
    tokens_seen_init: int = 0,
    initial_epoch: int = 0,
    resumed_step_in_epoch: int = 0,
    initial_train_losses: Optional[List[float]] = None,
    initial_val_losses: Optional[List[float]] = None,
    initial_track_tokens: Optional[List[int]] = None,
    amp_dtype: Optional[torch.dtype] = torch.bfloat16,
    gpt_config: Optional[Dict[str, Any]] = None,
    use_amp: Optional[bool] = None,
    accumulated_training_time: float = 0.0,
) -> Tuple[List[float], List[float], List[int], List[float], float, List[float]]:
    """
    Fully-optimized instruction fine-tuning training loop with multi-GPU/AMP support,
    hybrid Muon + AdamW optimization, cosine warmup scheduling, and real-time telemetry.
    """
    raw_model = getattr(model, "raw_model", getattr(model, "module", model))
    raw_model = getattr(raw_model, "_orig_mod", raw_model)

    train_losses = initial_train_losses if initial_train_losses is not None else []
    val_losses = initial_val_losses if initial_val_losses is not None else []
    val_seq_losses: List[float] = []
    track_tokens_seen = initial_track_tokens if initial_track_tokens is not None else []
    track_epochs: List[float] = []

    tokens_seen = tokens_seen_init
    start_step = resumed_step
    target_step = (start_step + args.step_limit) if args.step_limit is not None and args.step_limit > 0 else None
    global_step = start_step

    start_epoch = initial_epoch
    if start_epoch >= args.num_epochs:
        print(f"\n[Resume Notice] Checkpoint has already completed {start_epoch} epochs (>= requested {args.num_epochs}).")
        return train_losses, val_losses, track_tokens_seen, track_epochs, accumulated_training_time, val_seq_losses

    total_steps_in_epoch = len(train_loader)
    effective_steps_in_epoch = math.ceil(total_steps_in_epoch / args.accum_steps)
    global_total_steps = effective_steps_in_epoch * args.num_epochs
    warmup_steps = int(global_total_steps * args.warmup_ratio)

    print(f"\n[Training Plan] Target epochs: {args.num_epochs} | Steps per epoch: {total_steps_in_epoch:,} (Optimizer updates: {effective_steps_in_epoch:,}) | Planned updates: {global_total_steps:,} | Step plan: {plan_provenance(train_loader.dataset)}")
    lr_at = lr_schedule_from_resume(optimizer, start_step, lambda s: get_cosine_lr_with_warmup(s, warmup_steps, global_total_steps, args.learning_rate, args.min_lr), global_total_steps, warmup_steps, args.min_lr)
    if target_step is not None:
        print(f"[Training Plan] Resumed from step {start_step}. Training for {args.step_limit} steps -> Target step: {target_step}.")
    if args.accum_steps > 1:
        print(f"[Gradient Accumulation] Accumulating gradients over {args.accum_steps} sub-steps before optimizer update.")
    if args.model_name:
        print(f"[Checkpointing] Model target: '{args.model_name}'")

    sample_prompt = format_input(start_context_entry)
    use_cuda = (device.type == "cuda")
    if use_amp is None:
        use_amp = (use_cuda and amp_dtype is not None and amp_dtype != torch.float32)
    scaler = create_grad_scaler(model, device, use_amp=use_amp, amp_dtype=amp_dtype)

    # Initial evaluation
    print("\n[Initial State Evaluation]")
    t_init_eval_start = time.time()
    initial_train_loss, initial_val_loss, _, init_val_seq_loss = evaluate_model(
        model, train_loader, val_loader, device, args.eval_iter, amp_dtype=amp_dtype, use_amp=use_amp, chunk_size=args.chunk_size, return_seq_loss=True
    )
    init_eval_time = time.time() - t_init_eval_start
    init_val_ppl = calculate_perplexity(initial_val_loss)
    if init_val_seq_loss is not None:
        init_seq_ppl = calculate_perplexity(init_val_seq_loss)
        val_seq_losses.append(init_val_seq_loss)
        print(f"  Initial Train Loss : {initial_train_loss:.4f}")
        print(f"  Initial Val Loss   : {initial_val_loss:.4f} (Seq: {init_val_seq_loss:.4f}) (PPL: Resp {init_val_ppl:.2f} | Seq {init_seq_ppl:.2f}) (Eval took {init_eval_time:.2f}s)")
    else:
        print(f"  Initial Train Loss : {initial_train_loss:.4f}")
        print(f"  Initial Val Loss   : {initial_val_loss:.4f} (PPL: {init_val_ppl:.2f}) (Eval took {init_eval_time:.2f}s)")

    start_time = time.time()
    def get_current_accum_time() -> float:
        return accumulated_training_time + (time.time() - start_time)

    interval_train_time = 0.0
    interval_tokens = 0
    interval_loss_sum, interval_loss_count = 0.0, 0
    cumulative_train_time = 0.0
    stopped_due_to_limit = False

    step_in_epoch = resumed_step_in_epoch
    epoch = start_epoch

    try:
        for epoch in range(start_epoch, args.num_epochs):
            print(f"\n{'='*70}\nStarting Fine-Tuning Epoch {epoch+1}/{args.num_epochs}\n{'='*70}")
            epoch_start_time = time.time()
            model.train()

            skip_steps = resumed_step_in_epoch if epoch == start_epoch else 0
            if skip_steps > 0:
                print(f"[Resume] Fast-forwarding {skip_steps} step(s) in Epoch {epoch+1} -> Resuming from step {skip_steps + 1}/{total_steps_in_epoch}...")

            if isinstance(optimizer, list):
                for opt in optimizer:
                    opt.zero_grad()
            else:
                optimizer.zero_grad()

            train_loader.dataset.seek(epoch)
            for step_in_epoch, (input_batch, target_batch) in enumerate(train_loader, 1):
                if step_in_epoch <= skip_steps:
                    continue

                t_step_start = time.time()

                if (step_in_epoch - 1) % args.accum_steps == 0:
                    if hasattr(model, "zero_grad") and hasattr(model, "raw_replicas"):
                        model.zero_grad(set_to_none=True)

                loss, bwd_done = calc_loss_batch(
                    input_batch, target_batch, model, device,
                    amp_dtype=amp_dtype, chunk_size=args.chunk_size,
                    accum_steps=args.accum_steps, return_backward_status=True,
                    activation_checkpointing=args.activation_checkpointing,
                    use_amp=use_amp, scaler=scaler, autocast_weight_cache=args.use_autocast_weight_cache
                )
                assert isinstance(loss, torch.Tensor)
                interval_loss_sum = interval_loss_sum + loss.detach().float()
                interval_loss_count += 1
                if not bwd_done:
                    if args.accum_steps > 1:
                        loss = loss / args.accum_steps
                    if scaler:
                        scaler.scale(loss).backward()
                    else:
                        loss.backward()

                del loss

                batch_tokens = int((input_batch != tokenizer.pad_id).sum().item())
                tokens_seen += batch_tokens
                interval_tokens += batch_tokens

                is_accum_step = (step_in_epoch % args.accum_steps == 0) or (step_in_epoch == total_steps_in_epoch)

                if is_accum_step:
                    global_step += 1

                    if hasattr(model, "reduce_gradients"):
                        model.reduce_gradients()

                    current_lr = lr_at(global_step)
                    set_optimizer_lr(optimizer, current_lr)

                    if scaler:
                        if isinstance(optimizer, list):
                            for opt in optimizer:
                                scaler.unscale_(opt)
                            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)  # the wrapper's parameters: under ZeRO-1 the averaged gradients live on the shard masters, not all on raw_model
                            for opt in optimizer:
                                scaler.step(opt)
                        else:
                            scaler.unscale_(optimizer)
                            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)  # the wrapper's parameters: under ZeRO-1 the averaged gradients live on the shard masters, not all on raw_model
                            scaler.step(optimizer)
                        scaler.update()
                    else:
                        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)  # the wrapper's parameters: under ZeRO-1 the averaged gradients live on the shard masters, not all on raw_model
                        if isinstance(optimizer, list):
                            for opt in optimizer:
                                opt.step()
                        else:
                            optimizer.step()

                    if hasattr(model, "sync_weights"):
                        model.sync_weights()

                    if isinstance(optimizer, list):
                        for opt in optimizer:
                            opt.zero_grad()
                    else:
                        optimizer.zero_grad()

                    if hasattr(model, "zero_grad") and hasattr(model, "raw_replicas"):
                        model.zero_grad(set_to_none=True)

                t_step_end = time.time()
                step_duration = t_step_end - t_step_start
                interval_train_time += step_duration
                cumulative_train_time += step_duration

                if is_accum_step and (global_step % args.eval_freq == 0 or (target_step is not None and global_step >= target_step)):
                    tps = interval_tokens / interval_train_time if interval_train_time > 0 else 0
                    avg_tps = (tokens_seen - tokens_seen_init) / cumulative_train_time if cumulative_train_time > 0 else 0

                    interval_tokens = 0
                    interval_train_time = 0.0

                    vram_str = format_vram_report(model, optimizer, device)
                    lr_val = optimizer[0].param_groups[0]["lr"] if isinstance(optimizer, list) else optimizer.param_groups[0]["lr"]

                    t_eval_start = time.time()
                    train_loss = float(interval_loss_sum / interval_loss_count)
                    interval_loss_sum, interval_loss_count = 0.0, 0
                    _, val_loss, _, val_seq_loss = evaluate_model(
                        model, None, val_loader, device, args.eval_iter,
                        amp_dtype=amp_dtype, use_amp=use_amp, chunk_size=args.chunk_size,
                        return_seq_loss=True
                    )
                    eval_duration = time.time() - t_eval_start

                    train_losses.append(train_loss)
                    val_losses.append(val_loss)
                    if val_seq_loss is not None:
                        val_seq_losses.append(val_seq_loss)
                    track_tokens_seen.append(tokens_seen)
                    epoch_fraction = epoch + (step_in_epoch / total_steps_in_epoch)
                    track_epochs.append(epoch_fraction)
                    val_ppl = calculate_perplexity(val_loss)
                    val_seq_ppl = calculate_perplexity(val_seq_loss) if val_seq_loss is not None else None

                    print_step_telemetry(
                        epoch=epoch,
                        num_epochs=args.num_epochs,
                        step=step_in_epoch,
                        total_steps=total_steps_in_epoch,
                        global_step=global_step,
                        global_total_steps=global_total_steps,
                        train_loss=train_loss,
                        val_loss=val_loss,
                        tps=tps,
                        avg_tps=avg_tps,
                        eval_duration=eval_duration,
                        lr=lr_val,
                        vram_str=vram_str,
                        val_ppl=val_ppl,
                        val_seq_loss=val_seq_loss,
                        val_seq_ppl=val_seq_ppl,
                    )

                    if args.verbose:
                        pos_emb_mod = getattr(raw_model, "pos_emb", None)
                        context_size = pos_emb_mod.weight.shape[0] if pos_emb_mod is not None else getattr(raw_model, "cfg", {}).get("context_length", 1024)
                        encoded = text_to_token_ids(sample_prompt, tokenizer).to(device)
                        model.eval()
                        with torch.no_grad():
                            if use_amp and amp_dtype is not None:
                                with torch.amp.autocast(device_type="cuda", dtype=amp_dtype):  # type: ignore
                                    gen_ids = generate_text(
                                        model=model, idx=encoded, max_new_tokens=64,
                                        context_size=context_size, eos_id=tokenizer.eos_id, temperature=0.0
                                    )
                            else:
                                gen_ids = generate_text(
                                    model=model, idx=encoded, max_new_tokens=64,
                                    context_size=context_size, eos_id=tokenizer.eos_id, temperature=0.0
                                )
                            gen_str = token_ids_to_text(gen_ids[:, encoded.shape[1]:], tokenizer)  # the new tokens only: slicing the decoded text by len(sample_prompt) breaks when the decode differs from the prompt text
                            resp_sample = gen_str.replace("### Response:", "").strip()
                            safe_sample = resp_sample.replace("\n", " ").strip()
                            if len(safe_sample) > 100:
                                safe_sample = safe_sample[:100] + "..."
                            print(f"  [Sample]: {safe_sample}")
                        model.train()

                    if args.model_name and global_step % args.save_interval == 0:
                        save_checkpoint(
                            model=raw_model,
                            args=args,
                            optimizer=optimizer,
                            config=gpt_config,
                            global_step=global_step,
                            epoch=epoch,
                            current_epoch=epoch,
                            step_in_epoch=step_in_epoch,
                            epoch_completed=False,
                            tokens_seen=tokens_seen,
                            train_losses=train_losses,
                            val_losses=val_losses,
                            track_tokens=track_tokens_seen,
                            is_sft=True,
                            accumulated_training_time=get_current_accum_time()
                        )

                    if target_step is not None and global_step >= target_step:  # inside is_accum_step: this step's update (incl. an epoch-end partial accumulation) is already applied, nothing to flush
                        if args.model_name:
                            save_checkpoint(
                                model=raw_model,
                                args=args,
                                optimizer=optimizer,
                                config=gpt_config,
                                global_step=global_step,
                                epoch=epoch,
                                current_epoch=epoch,
                                step_in_epoch=step_in_epoch,
                                epoch_completed=False,
                                tokens_seen=tokens_seen,
                                train_losses=train_losses,
                                val_losses=val_losses,
                                track_tokens=track_tokens_seen,
                                is_sft=True,
                                accumulated_training_time=get_current_accum_time()
                            )
                        print(f"\n[Step Limit Reached] Reached target step {target_step}. Pausing fine-tuning cleanly.")
                        stopped_due_to_limit = True
                        break

            if stopped_due_to_limit:
                break

            print("\n" + "-" * 70)
            print(f"[Sample Response @ Epoch {epoch+1}]")
            pos_emb_mod = getattr(raw_model, "pos_emb", None)
            context_size = pos_emb_mod.weight.shape[0] if pos_emb_mod is not None else getattr(raw_model, "cfg", {}).get("context_length", 1024)
            encoded = text_to_token_ids(sample_prompt, tokenizer).to(device)
            model.eval()
            tune_stops = ["<|im_end|>", "<|user|>", "<|assistant|>", "<|endoftext|>"]
            with torch.no_grad():
                if use_cuda and amp_dtype is not None:
                    with torch.amp.autocast(device_type="cuda", dtype=amp_dtype):  # type: ignore
                        gen_ids = generate_text(
                            model=model, idx=encoded, max_new_tokens=100,
                            context_size=context_size, eos_id=tokenizer.eos_id, temperature=0.0,
                            stop_strings=tune_stops, tokenizer=tokenizer
                        )
                else:
                    gen_ids = generate_text(
                        model=model, idx=encoded, max_new_tokens=100,
                        context_size=context_size, eos_id=tokenizer.eos_id, temperature=0.0,
                        stop_strings=tune_stops, tokenizer=tokenizer
                    )
                gen_str = token_ids_to_text(gen_ids[:, encoded.shape[1]:], tokenizer)  # the new tokens only: slicing the decoded text by len(sample_prompt) breaks when the decode differs from the prompt text
                resp_sample = gen_str
                for stop_tag in tune_stops + ["### Response:"]:
                    resp_sample = resp_sample.replace(stop_tag, "")
                resp_sample = resp_sample.strip()
                inst_text = start_context_entry.get("instruction") or start_context_entry.get("prompt", "")
                if len(inst_text) > 80:
                    inst_text = inst_text[:80] + "..."
                print(f"  Prompt/Inst : {inst_text}")
                print(f"  Response    : {resp_sample}")
            print("-" * 70)
            model.train()

            if args.model_name:
                save_checkpoint(
                    model=raw_model,
                    args=args,
                    optimizer=optimizer,
                    config=gpt_config,
                    global_step=global_step,
                    epoch=epoch + 1,
                    current_epoch=epoch + 1,
                    step_in_epoch=0,
                    epoch_completed=True,
                    tokens_seen=tokens_seen,
                    train_losses=train_losses,
                    val_losses=val_losses,
                    track_tokens=track_tokens_seen,
                    is_sft=True,
                    accumulated_training_time=get_current_accum_time()
                )

            print_gpu_memory_breakdown(model, optimizer)
            print_eta(start_time, epoch_start_time, (epoch - start_epoch + 1), (args.num_epochs - start_epoch))

            if stopped_due_to_limit:
                break

        if args.model_name and not stopped_due_to_limit:
            save_checkpoint(
                model=raw_model,
                args=args,
                optimizer=optimizer,
                config=gpt_config,
                global_step=global_step,
                epoch=args.num_epochs,
                current_epoch=args.num_epochs,
                step_in_epoch=0,
                epoch_completed=True,
                tokens_seen=tokens_seen,
                train_losses=train_losses,
                val_losses=val_losses,
                track_tokens=track_tokens_seen,
                is_sft=True,
                accumulated_training_time=get_current_accum_time()
            )
            save_model(
                model=raw_model,
                args=args,
                config=gpt_config
            )

    except KeyboardInterrupt:
        print(f"\n\n[Interrupt] Fine-tuning cancelled by user (Ctrl+C).")
        if args.model_name:
            try:
                save_checkpoint(
                    model=raw_model,
                    args=args,
                    optimizer=optimizer,
                    config=gpt_config,
                    global_step=global_step,
                    epoch=epoch,
                    current_epoch=epoch,
                    step_in_epoch=step_in_epoch,
                    epoch_completed=False,
                    tokens_seen=tokens_seen,
                    train_losses=train_losses,
                    val_losses=val_losses,
                    track_tokens=track_tokens_seen,
                    is_sft=True,
                    accumulated_training_time=get_current_accum_time()
                )
                print(f"[Interrupt] Checkpoint successfully saved for '{args.model_name}' at Global Step {global_step:,} (Epoch {epoch+1}, Step {step_in_epoch}).")
                print(f"[Interrupt] You can resume anytime by re-running the script with the same arguments.\n")
            except Exception as save_err:
                print(f"[Interrupt Warning] Could not save checkpoint on interrupt: {save_err}")
        return train_losses, val_losses, track_tokens_seen, track_epochs, get_current_accum_time(), val_seq_losses

    except Exception as e:
        print(f"\n\n[Crash Recovery] Unexpected error during fine-tuning: {e}")
        if args.model_name:
            try:
                save_checkpoint(
                    model=raw_model,
                    args=args,
                    optimizer=optimizer,
                    config=gpt_config,
                    global_step=global_step,
                    epoch=epoch,
                    current_epoch=epoch,
                    step_in_epoch=step_in_epoch,
                    epoch_completed=False,
                    tokens_seen=tokens_seen,
                    train_losses=train_losses,
                    val_losses=val_losses,
                    track_tokens=track_tokens_seen,
                    is_sft=True,
                    accumulated_training_time=get_current_accum_time()
                )
                print(f"[Crash Recovery] Emergency checkpoint saved for '{args.model_name}' at Global Step {global_step:,} (Epoch {epoch+1}, Step {step_in_epoch}).")
            except Exception as save_err:
                print(f"[Crash Recovery Warning] Could not save emergency checkpoint: {save_err}")
        raise e

    return train_losses, val_losses, track_tokens_seen, track_epochs, get_current_accum_time(), val_seq_losses
