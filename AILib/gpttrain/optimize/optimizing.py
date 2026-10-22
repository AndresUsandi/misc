# Copyright (c) Sebastian Raschka under Apache License 2.0 (see LICENSE.txt).
# Fully-Optimized Direct Preference Optimization (DPO) Engine for GPT Models (Chapter 7 Preference Tuning)

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
from gpttrain.train.evaluation import calc_loss_batch, text_to_token_ids, token_ids_to_text
from gptio.checkpoint import save_checkpoint
from gptio.modelio import save_model
from gptio.pathutil import STAGE_OPTIMIZE
from gptio.precision import create_grad_scaler
from gpttrain.optimizer import lr_schedule_from_resume, set_optimizer_lr
from gpttrain.optimize.scheduler import get_cosine_lr_with_warmup
from gpttrain.optimize.dpo_loss import compute_dpo_loss_batch, evaluate_dpo_loader
from gptutils.consoleutils import (
    print,
    format_vram_report,
    print_gpu_memory_breakdown,
    print_step_telemetry,
    print_eta,
)
from gptutils.metrics import print_stage_completion_summary, count_model_parameters
from gptinfer.inference import generate_text


def train_model_dpo_fully_optimized(
    policy_model: nn.Module,
    reference_model: nn.Module,
    train_loader: DataLoader,
    val_loader: DataLoader,
    optimizer: Any,
    device: torch.device,
    ref_device: torch.device,
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
    amp_dtype: Optional[torch.dtype] = torch.bfloat16,
    use_amp: Optional[bool] = None,
    accumulated_training_time: float = 0.0,
    replay_loader: Optional[DataLoader] = None,
    replay_weight: float = 1.0,
) -> Tuple[List[float], List[float], List[float], List[float], List[int], List[float], float]:
    """
    Executes DPO preference tuning with multi-GPU/AMP acceleration, gradient accumulation,
    reward margin tracking, real-time throughput telemetry, and robust checkpointing.
    replay_loader (--dpo_replay_datasets): an instruction loader whose batches are scored with the ordinary SFT loss, times replay_weight,
    in every micro-step next to the preference loss, so the skills in that data keep being trained while the pairs pull elsewhere.
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

    print(f"\n[DPO Plan] Target epochs: {args.num_epochs} | Steps per epoch: {total_steps_in_epoch:,} (Updates: {effective_steps_in_epoch:,}) | Total updates: {global_total_steps:,} | Step plan: {plan_provenance(train_loader.dataset)}")
    lr_at = lr_schedule_from_resume(optimizer, start_step, lambda s: get_cosine_lr_with_warmup(s, warmup_steps, global_total_steps, args.learning_rate, args.min_lr), global_total_steps, warmup_steps, args.min_lr)
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
    init_tr = evaluate_dpo_loader(train_loader, policy_model, reference_model, args.beta, device, ref_device, args.eval_iter, amp_dtype=amp_dtype, use_amp=use_amp, sft_weight=args.dpo_sft_weight)
    init_val = evaluate_dpo_loader(val_loader, policy_model, reference_model, args.beta, device, ref_device, args.eval_iter, amp_dtype=amp_dtype, use_amp=use_amp, sft_weight=args.dpo_sft_weight)
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
    replay_iter, replay_epoch, replay_loss_sum, replay_loss_n = None, 0, 0.0, 0

    def next_replay_batch():
        """The next replayed SFT batch; the stream restarts (with a fresh shuffle) whenever it runs out, so it never gates the DPO run."""
        nonlocal replay_iter, replay_epoch
        for _ in range(2):
            if replay_iter is None:
                replay_loader.dataset.seek(replay_epoch); replay_iter = iter(replay_loader)
            try:
                return next(replay_iter)
            except StopIteration:
                replay_iter, replay_epoch = None, replay_epoch + 1
        raise RuntimeError("--dpo_replay_datasets: the replay stream yielded no batch")

    step_in_epoch = resumed_step_in_epoch
    epoch = start_epoch

    try:
        for epoch in range(start_epoch, args.num_epochs):
            print(f"\n{'='*70}\nStarting DPO Optimization Epoch {epoch+1}/{args.num_epochs}\n{'='*70}")
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

            train_loader.dataset.seek(epoch)
            for step_in_epoch, batch in enumerate(train_loader, 1):
                if step_in_epoch <= skip_steps:
                    continue

                t_step_start = time.time()

                loss, chosen_rew, rej_rew, margin, acc = compute_dpo_loss_batch(
                    batch=batch,
                    policy_model=policy_model,
                    reference_model=reference_model,
                    beta=args.beta,
                    sft_weight=args.dpo_sft_weight,
                    policy_device=device,
                    ref_device=ref_device,
                    amp_dtype=amp_dtype,
                    activation_checkpointing=args.activation_checkpointing,
                    use_amp=use_amp,
                    chunk_size=args.chunk_size,
                    backward_accum_steps=args.accum_steps,
                    scaler=scaler,
                )

                del loss

                if replay_loader is not None:  # the replayed SFT loss goes into the same accumulated gradients as the preference loss
                    r_in, r_tgt = next_replay_batch()
                    r_loss, r_done = calc_loss_batch(r_in, r_tgt, policy_model, device, amp_dtype=amp_dtype, chunk_size=args.chunk_size, accum_steps=args.accum_steps / replay_weight,
                                                     return_backward_status=True, activation_checkpointing=args.activation_checkpointing, use_amp=use_amp, scaler=scaler)
                    if not r_done:  # single-device path: the loss comes back unscaled and without its backward
                        scaled = r_loss * replay_weight / args.accum_steps
                        (scaler.scale(scaled) if scaler else scaled).backward()
                    replay_loss_sum += float(r_loss.detach()); replay_loss_n += 1
                    del r_loss

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
                    eval_tr = evaluate_dpo_loader(train_loader, policy_model, reference_model, args.beta, device, ref_device, args.eval_iter, amp_dtype=amp_dtype, use_amp=use_amp, sft_weight=args.dpo_sft_weight)
                    eval_val = evaluate_dpo_loader(val_loader, policy_model, reference_model, args.beta, device, ref_device, args.eval_iter, amp_dtype=amp_dtype, use_amp=use_amp, sft_weight=args.dpo_sft_weight)
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
                    if replay_loader is not None and replay_loss_n:
                        print(f"  [Replay] SFT loss on the replayed fine-tuning data over the interval: {replay_loss_sum / replay_loss_n:.4f} ({replay_loss_n} micro-steps, weight {replay_weight})")
                        replay_loss_sum, replay_loss_n = 0.0, 0

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
                        print(f"\n[Step Limit Reached] Reached target step {target_step}. Pausing DPO optimization cleanly.")
                        stopped_due_to_limit = True
                        break

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
        print(f"\n\n[Interrupt] DPO optimization cancelled by user (Ctrl+C).")
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
        print(f"\n\n[Crash Recovery] Unexpected error during DPO optimization: {e}")
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
