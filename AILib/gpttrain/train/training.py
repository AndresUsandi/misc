# Copyright (c) Sebastian Raschka under Apache License 2.0 (see LICENSE.txt).
# Fully-Optimized GPT LLM Training Engine (Chapter 5)

from itertools import groupby
from pathlib import Path
import sys
import time
from typing import Any, List, Optional, Tuple, Union

import torch

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from argsutil import TrainingArgs
from gptio.checkpoint import save_checkpoint
from gptio.modelio import save_model
from gptio.precision import (
    resolve_precision_and_amp,
    create_grad_scaler,
    get_supported_amp_dtype,
)
from gptutils.consoleutils import (
    print,
    format_vram_str,
    print_gpu_memory_breakdown,
    print_step_telemetry,
    print_eta,
)
from gptutils.metrics import calculate_perplexity
from gpttrain.dataloaders import create_training_dataloader
from gpttrain.optimizer import (
    set_optimizer_lr,
    CustomMuon,
    Fp16AdamW,
    create_hybrid_optimizers,
)
from gpttrain.train.scheduler import get_lr_cosine_schedule
from gpttrain.train.system_check import check_torch_compile_working
from gpttrain.train.evaluation import (
    calc_loss_batch,
    calc_loss_loader,
    evaluate_model,
    generate_and_print_sample,
    text_to_token_ids,
    token_ids_to_text,
)


def train_model_fully_optimized(
    model: torch.nn.Module,
    all_files: List[Path],
    optimizers: Union[torch.optim.Optimizer, List[torch.optim.Optimizer]],
    device: torch.device,
    args: TrainingArgs,
    start_context: str,
    tokenizer: Any,
    context_length: int,
    max_grad_norm: float,
    amp_dtype: Optional[torch.dtype],
    num_workers: int,
    gpt_config: dict,
    resumed_step: int,
    initial_epoch: int,
    resumed_file_idx: int,
    resumed_step_in_file: int,
    tokens_seen_init: int,
    initial_train_losses: Optional[List[float]],
    initial_val_losses: Optional[List[float]],
    initial_track_tokens: Optional[List[int]],
    use_amp: Optional[bool] = None,
    accumulated_training_time: float = 0.0,
) -> Tuple[List[float], List[float], List[int], float]:
    start_time = time.time()
    def get_current_accum_time() -> float:
        return accumulated_training_time + (time.time() - start_time)

    train_losses = list(initial_train_losses) if initial_train_losses is not None else []
    val_losses = list(initial_val_losses) if initial_val_losses is not None else []
    track_tokens = list(initial_track_tokens) if initial_track_tokens is not None else []
    total_tokens = tokens_seen_init
    interval_tokens = 0
    interval_train_time = 0.0
    cumulative_train_time = 0.0
    start_step = resumed_step
    target_step = (start_step + args.step_limit) if args.step_limit is not None and args.step_limit > 0 else None
    global_step = start_step

    start_epoch = initial_epoch
    if start_epoch >= args.num_epochs:
        print(f"\n[Resume Notice] Checkpoint has already completed {start_epoch} epochs, which is >= requested num_epochs ({args.num_epochs}).")
        print(f"To train for additional epochs, please specify a higher --num_epochs (e.g. --num_epochs {start_epoch + 5}).")
        return train_losses, val_losses, track_tokens, get_current_accum_time()

    total_files = len(all_files)
    stopped_due_to_limit = False

    if target_step is not None:
        print(f"[Training Plan] Resumed from step {start_step}. Training for {args.step_limit} steps -> Target step: {target_step}.")
    if args.model_name and args.save_interval:
        print(f"[Checkpointing] Periodic saves enabled every {args.save_interval} steps -> '{args.model_name}'.")

    train_loader, dataset = create_training_dataloader(
        all_files=all_files,
        tokenizer=tokenizer,
        args=args,
        context_length=context_length,
        device=device,
    )
    num_known = dataset.num_known

    steps_per_epoch = sum(dataset.file_steps)
    global_total_steps = steps_per_epoch * args.num_epochs
    total_steps = max(1, global_total_steps)

    status_str = "complete" if num_known >= total_files else f"partial ({num_known}/{total_files} files known)"
    print(f"[Steps Cache] Loaded {status_str} steps cache for '{args.model_name}' ({steps_per_epoch:,} steps/epoch, {global_total_steps:,} total global steps).")
    min_lr = args.learning_rate * 0.1

    use_cuda = device.type == "cuda"
    if use_amp is None:
        use_amp = (use_cuda and amp_dtype is not None and amp_dtype != torch.float32)
    scaler = create_grad_scaler(model, device, use_amp=use_amp, amp_dtype=amp_dtype)

    start_time = time.time()

    step_idx = resumed_step_in_file
    index = resumed_file_idx
    epoch = start_epoch

    try:
        for epoch in range(start_epoch, args.num_epochs):
            print(f"\n{'='*50}\nStarting Epoch {epoch+1}/{args.num_epochs}\n{'='*50}")

            first_file_for_epoch = resumed_file_idx if epoch == start_epoch else 1
            dataset.seek(epoch, args.num_epochs, first_file_for_epoch, resumed_step_in_file if epoch == start_epoch else 0)

            # Batches stream across files as (inputs, targets, file_idx, step_in_file); group them per file to keep the per-file bookkeeping
            for index, file_batches in groupby(train_loader, key=lambda batch: batch[2]):
                file_start_time = time.time()
                # The dataset tokenized this file before yielding its first batch: exact step count, totals refreshed (unknown files were estimates)
                total_steps_in_file = dataset.file_steps[index - 1]
                steps_per_epoch = sum(dataset.file_steps)
                global_total_steps = steps_per_epoch * args.num_epochs
                total_steps = max(1, global_total_steps)

                model.train()
                for inp_batch, tgt_batch, _, step_idx in file_batches:
                    t_step_start = time.time()
                    epoch_step = step_idx
                    global_step += 1

                    lr = get_lr_cosine_schedule(global_step, args.learning_rate, min_lr, args.warmup_steps, total_steps)
                    set_optimizer_lr(optimizers, lr)

                    if (step_idx - 1) % args.accum_steps == 0:
                        opts = optimizers if isinstance(optimizers, list) else [optimizers]
                        for optimizer in opts:
                            optimizer.zero_grad(set_to_none=True)
                        if hasattr(model, "zero_grad") and hasattr(model, "raw_replicas"):
                            model.zero_grad(set_to_none=True)

                    if use_amp and amp_dtype is not None:
                        with torch.amp.autocast(device_type="cuda", dtype=amp_dtype):
                            loss, bwd_done = calc_loss_batch(
                                inp_batch, tgt_batch, model, device, amp_dtype=amp_dtype,
                                use_1f1b=args.use_1f1b,
                                multi_stage_micro_batching=args.multi_stage_micro_batching,
                                accum_steps=args.accum_steps, return_backward_status=True,
                                activation_checkpointing=args.activation_checkpointing,
                                use_amp=True,
                                scaler=scaler
                            )
                        if not bwd_done:
                            loss = loss / args.accum_steps
                            if scaler is not None:
                                scaler.scale(loss).backward()
                            else:
                                loss.backward()
                    else:
                        loss, bwd_done = calc_loss_batch(
                            inp_batch, tgt_batch, model, device, amp_dtype=None,
                            use_1f1b=args.use_1f1b,
                            multi_stage_micro_batching=args.multi_stage_micro_batching,
                            accum_steps=args.accum_steps, return_backward_status=True,
                            activation_checkpointing=args.activation_checkpointing,
                            use_amp=False
                        )
                        if not bwd_done:
                            loss = loss / args.accum_steps
                            loss.backward()

                    batch_tokens = inp_batch.numel()
                    total_tokens += batch_tokens
                    interval_tokens += batch_tokens

                    if step_idx % args.accum_steps == 0 or step_idx == total_steps_in_file:
                        if hasattr(model, "reduce_gradients"):
                            model.reduce_gradients()
                        opts = optimizers if isinstance(optimizers, list) else [optimizers]
                        if scaler is not None:
                            for opt in opts:
                                scaler.unscale_(opt)
                            grad_norm = torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=max_grad_norm)
                            if torch.isnan(grad_norm) or torch.isinf(grad_norm):
                                print(f"[Warning] NaN/Inf grad_norm ({grad_norm}) detected at Step {global_step}. Skipping optimizer update.")
                                for optimizer in opts:
                                    optimizer.zero_grad(set_to_none=True)
                            else:
                                for optimizer in opts:
                                    scaler.step(optimizer)
                                scaler.update()
                                if hasattr(model, "sync_weights"):
                                    model.sync_weights()
                        else:
                            grad_norm = torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=max_grad_norm)
                            if torch.isnan(grad_norm) or torch.isinf(grad_norm):
                                print(f"[Warning] NaN/Inf grad_norm ({grad_norm}) detected at Step {global_step}. Skipping optimizer update.")
                                for optimizer in opts:
                                    optimizer.zero_grad(set_to_none=True)
                            else:
                                for optimizer in opts:
                                    optimizer.step()
                                if hasattr(model, "sync_weights"):
                                    model.sync_weights()

                    t_step_end = time.time()
                    step_duration = t_step_end - t_step_start
                    interval_train_time += step_duration
                    cumulative_train_time += step_duration

                    if global_step % args.eval_freq == 0:
                        tps = interval_tokens / interval_train_time if interval_train_time > 0 else 0
                        avg_tps = (total_tokens - tokens_seen_init) / cumulative_train_time if cumulative_train_time > 0 else 0

                        interval_tokens = 0
                        interval_train_time = 0.0

                        vram_str = format_vram_str(device)

                        t_eval_start = time.time()
                        train_loss, val_loss = evaluate_model(model, *dataset.eval_loaders(index), device, args.eval_iter, amp_dtype=amp_dtype,
                                                              use_1f1b=args.use_1f1b,
                                                              multi_stage_micro_batching=args.multi_stage_micro_batching,
                                                              use_amp=use_amp)
                        eval_duration = time.time() - t_eval_start

                        train_losses.append(train_loss)
                        val_losses.append(val_loss)
                        track_tokens.append(total_tokens)
                        val_ppl = calculate_perplexity(val_loss)

                        print_step_telemetry(
                            epoch=epoch,
                            num_epochs=args.num_epochs,
                            step=epoch_step,
                            total_steps=total_steps_in_file,
                            global_step=global_step,
                            global_total_steps=global_total_steps,
                            train_loss=train_loss,
                            val_loss=val_loss,
                            tps=tps,
                            avg_tps=avg_tps,
                            eval_duration=eval_duration,
                            lr=lr,
                            vram_str=vram_str,
                            val_ppl=val_ppl,
                        )

                    # Periodic save
                    if args.model_name and args.save_interval and (global_step % args.save_interval == 0):
                        save_checkpoint(
                            model=model,
                            args=args,
                            config=gpt_config,
                            optimizer=optimizers,
                            global_step=global_step,
                            epoch=epoch,
                            current_epoch=epoch,
                            current_file_idx=index,
                            step_in_file=step_idx,
                            epoch_completed=False,
                            tokens_seen=total_tokens,
                            train_losses=train_losses,
                            val_losses=val_losses,
                            track_tokens=track_tokens,
                            accumulated_training_time=get_current_accum_time(),
                            save_timeout=args.save_timeout
                        )

                    # Stop limit check
                    if target_step is not None and global_step >= target_step:
                        # Flush pending gradients if mid-accumulation
                        if (step_idx + 1) % args.accum_steps != 0:
                            if hasattr(model, "reduce_gradients"):
                                model.reduce_gradients()
                            opts = optimizers if isinstance(optimizers, list) else [optimizers]
                            if scaler is not None:
                                for opt in opts:
                                    scaler.unscale_(opt)
                                grad_norm = torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=max_grad_norm)
                                if not (torch.isnan(grad_norm) or torch.isinf(grad_norm)):
                                    for optimizer in opts:
                                        scaler.step(optimizer)
                                    scaler.update()
                                    if hasattr(model, "sync_weights"):
                                        model.sync_weights()
                            else:
                                grad_norm = torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=max_grad_norm)
                                if not (torch.isnan(grad_norm) or torch.isinf(grad_norm)):
                                    for optimizer in opts:
                                        optimizer.step()
                                    if hasattr(model, "sync_weights"):
                                        model.sync_weights()

                        if args.model_name:
                            save_checkpoint(
                                model=model,
                                args=args,
                                config=gpt_config,
                                optimizer=optimizers,
                                global_step=global_step,
                                epoch=epoch,
                                current_epoch=epoch,
                                current_file_idx=index,
                                step_in_file=step_idx,
                                epoch_completed=False,
                                tokens_seen=total_tokens,
                                train_losses=train_losses,
                                val_losses=val_losses,
                                track_tokens=track_tokens,
                                accumulated_training_time=get_current_accum_time(),
                                save_timeout=args.save_timeout
                            )
                        print(f"\n[Step Limit Reached] Completed {args.step_limit} step(s) in this session (Global Step: {global_step}).")
                        print(f"Checkpoint saved for '{args.model_name}'. Training paused cleanly.")
                        stopped_due_to_limit = True
                        break

                if stopped_due_to_limit:
                    break

                generate_and_print_sample(model, tokenizer, device, start_context, temperature=args.temperature, top_k=args.top_k)

                print_gpu_memory_breakdown()

                print_eta(start_time, file_start_time, index + (epoch - start_epoch) * total_files, total_files * (args.num_epochs - start_epoch))

            if stopped_due_to_limit:
                break

            # Save completed epoch checkpoint
            if args.model_name:
                save_checkpoint(
                    model=model,
                    args=args,
                    config=gpt_config,
                    optimizer=optimizers,
                    global_step=global_step,
                    epoch=epoch + 1,
                    current_epoch=epoch + 1,
                    current_file_idx=1,
                    step_in_file=0,
                    epoch_completed=True,
                    tokens_seen=total_tokens,
                    train_losses=train_losses,
                    val_losses=val_losses,
                    track_tokens=track_tokens,
                    accumulated_training_time=get_current_accum_time(),
                    save_timeout=args.save_timeout
                )

        # Save final checkpoint (.chk) and clean exported model (.pth) for inference
        if args.model_name and not stopped_due_to_limit and global_step > start_step:
            save_checkpoint(
                model=model,
                args=args,
                config=gpt_config,
                optimizer=optimizers,
                global_step=global_step,
                epoch=args.num_epochs,
                current_epoch=args.num_epochs,
                current_file_idx=1,
                step_in_file=0,
                epoch_completed=True,
                tokens_seen=total_tokens,
                train_losses=train_losses,
                val_losses=val_losses,
                track_tokens=track_tokens,
                accumulated_training_time=get_current_accum_time(),
                save_timeout=args.save_timeout
            )
            save_model(
                model=model,
                args=args,
                config=gpt_config
            )

    except KeyboardInterrupt:
        print(f"\n\n[Interrupt] Pre-training cancelled by user (Ctrl+C).")
        if args.model_name:
            try:
                save_checkpoint(
                    model=model,
                    args=args,
                    config=gpt_config,
                    optimizer=optimizers,
                    global_step=global_step,
                    epoch=epoch,
                    current_epoch=epoch,
                    current_file_idx=index,
                    step_in_file=step_idx,
                    epoch_completed=False,
                    tokens_seen=total_tokens,
                    train_losses=train_losses,
                    val_losses=val_losses,
                    track_tokens=track_tokens,
                    accumulated_training_time=get_current_accum_time(),
                    save_timeout=args.save_timeout
                )
                print(f"[Interrupt] Checkpoint successfully saved for '{args.model_name}' at Global Step {global_step:,} (Epoch {epoch+1}, File {index}, Step {step_idx}).")
                print(f"[Interrupt] You can resume anytime by re-running the script with the same arguments.\n")
            except Exception as save_err:
                print(f"[Interrupt Warning] Could not save checkpoint on interrupt: {save_err}")
        return train_losses, val_losses, track_tokens, get_current_accum_time()

    except Exception as e:
        print(f"\n\n[Crash Recovery] Unexpected error during pre-training: {e}")
        if args.model_name:
            try:
                save_checkpoint(
                    model=model,
                    args=args,
                    config=gpt_config,
                    optimizer=optimizers,
                    global_step=global_step,
                    epoch=epoch,
                    current_epoch=epoch,
                    current_file_idx=index,
                    step_in_file=step_idx,
                    epoch_completed=False,
                    tokens_seen=total_tokens,
                    train_losses=train_losses,
                    val_losses=val_losses,
                    track_tokens=track_tokens,
                    accumulated_training_time=get_current_accum_time(),
                    save_timeout=args.save_timeout
                )
                print(f"[Crash Recovery] Emergency checkpoint saved for '{args.model_name}' at Global Step {global_step:,} (Epoch {epoch+1}, File {index}, Step {step_idx}).")
            except Exception as save_err:
                print(f"[Crash Recovery Warning] Could not save emergency checkpoint: {save_err}")
        raise e

    return train_losses, val_losses, track_tokens, get_current_accum_time()
