# Copyright (c) Sebastian Raschka under Apache License 2.0 (see LICENSE.txt).
# Consolidated GPT Training, Instruction Fine-Tuning, and Preference Optimization CLI.
# Orchestrator for train.py, tune.py, and optimize.py.

import copy
import json
import os
import sys
import time
import warnings
from typing import Any, Dict, List, Optional, Tuple

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "garbage_collection_threshold:0.8,max_split_size_mb:256"  # pretraining only: SFT/DPO re-set this in gpttrain/device.py before CUDA init; no expandable_segments here: pretraining shapes are static, and on Linux (where it is honored; Windows ignored it) it flooded the console with "memory mapping failed with OOM" warnings and forced a sync + full cache flush every ~2 steps (see "alloc retries" in the [VRAM] log lines)
os.environ.setdefault("TORCH_COMPILE_CACHE_KEY_TAG", "sdpa-cudnn")
os.environ.setdefault("TORCHINDUCTOR_USE_STATIC_CUDA_LAUNCHER", "0")
warnings.filterwarnings("ignore", message=".*expandable_segments not supported.*")

import torch
import torch.nn as nn
from torch.nn.attention import sdpa_kernel, SDPBackend

from argsutil import parse_arguments
from gptmodel.GptModel import GptModel, DYNAMO_RECOMPILE_LIMIT
from gptmodel.MultiGpuGptModelDP import MultiGpuGptModelDP
from gptmodel.Dataset import format_input, parse_instruction_text_file
from gptio.modelio import load_model_config
from gptio.precision import (
    resolve_precision_and_amp,
    is_fp8_supported,
    PRECISION_FP8,
)
from gptio.pathutil import (
    STAGE_TRAIN,
    STAGE_TUNE,
    STAGE_OPTIMIZE,
    resolve_path_with_override,
    resolve_data_files,
)
from gptutils.consoleutils import print, format_elapsed_time
from gptutils.metrics import print_stage_completion_summary, count_model_parameters

from gpttrain.device import setup_devices_and_allocator
from gpttrain.model_setup import setup_model_and_acceleration
from gpttrain.optimizer import freeze_lower_layers, setup_stage_optimizer
from gpttrain.checkpoint import resume_stage_checkpoint
from gpttrain.dataloaders import (
    create_instruction_dataloaders,
    create_preference_dataloaders,
)
from gpttrain.plots import (
    plot_training_losses,
    plot_tuning_losses,
    plot_dpo_losses_and_margins,
)
from gpttrain.train.training import train_model_fully_optimized
from gpttrain.tune.tuning import train_model_instruction_fully_optimized
from gpttrain.optimize.optimizing import train_model_dpo_fully_optimized
from gpttrain.optimize.json_precompute import (
    precompute_dataset_reference_logprobs,
    train_model_dpo_precomputed,
)
from gptinfer.inference import get_tokenizer

if torch.cuda.is_available():
    torch.set_float32_matmul_precision("high")

SDPA_BACKENDS = [SDPBackend.CUDNN_ATTENTION, SDPBackend.EFFICIENT_ATTENTION, SDPBackend.MATH]
torch._dynamo.config.recompile_limit = DYNAMO_RECOMPILE_LIMIT


def main():
    # Defaults <- <model_name>.options-<stage>.json <- command line (see argsutil.TrainingArgs)
    args = parse_arguments()
    stage = args.stage

    torch.manual_seed(123)
    if os.environ.get("AILIB_DETERMINISTIC") == "1":
        torch.use_deterministic_algorithms(True)
    torch._inductor.config.coordinate_descent_tuning = bool(args.coordinate_descent_tuning)

    # Load architecture parameters strictly from model configuration
    model_params = load_model_config(args)
    if model_params is None:
        raise FileNotFoundError(f"Model configuration not found for '{args.model_name}'.")
    gpt_config = dict(model_params)
    if args.vocab_padded and gpt_config.get("vocab_size") == 50257:
        gpt_config["vocab_size"] = 50304

    # Setup compute devices and allocator
    device, ref_device, use_cuda = setup_devices_and_allocator(args)

    # Mixed precision resolution
    model_dtype, use_amp, amp_dtype = resolve_precision_and_amp(device, precision=args.precision)
    weight_dtype = model_dtype
    use_float8 = args.precision == PRECISION_FP8 and is_fp8_supported(device)

    # Target and data resolution
    target_data_path = resolve_path_with_override(args, stage=stage, override_folder=args.override_data_folder)
    effective_model_name = args.model_name

    # Dataset loading
    all_files = resolve_data_files(target_data_path, stage=stage, models_dir=args.models_base_dir)
    total_files = len(all_files)
    if args.test_mode and total_files > 1:
        all_files = all_files[:1]
        print(f"[Test Mode] Truncated dataset to 1 file ({all_files[0].name}).")

    num_gpus = torch.cuda.device_count() if (use_cuda and not args.single_gpu) else 0
    amp_status = f"Enabled ({amp_dtype})" if use_amp else "Disabled"

    banner_titles = {
        STAGE_TRAIN: "FULLY-OPTIMIZED GPT TRAINING",
        STAGE_TUNE: "FULLY-OPTIMIZED GPT INSTRUCTION FINE-TUNING (SFT)",
        STAGE_OPTIMIZE: "GPT DIRECT PREFERENCE OPTIMIZATION (DPO)",
    }
    print("\n" + "=" * 65)
    print(f"      {banner_titles[stage]}")
    print("=" * 65)
    if stage == STAGE_OPTIMIZE:
        if args.json_precompute:
            print(f"Policy Device: {device} | Precomputed Mode: Active (No Ref Model) | Precision: {args.precision.upper()} | Model Dtype: {model_dtype} | AMP: {amp_status}")
        else:
            print(f"Policy Device: {device} | Ref Device: {ref_device} | Precision: {args.precision.upper()} | Model Dtype: {model_dtype} | AMP: {amp_status}")
    elif stage == STAGE_TRAIN:
        print(f"Model: {effective_model_name}")
        print(f"Device: {device} | Active GPUs: {num_gpus if num_gpus > 1 else 1} | Precision: {args.precision.upper()} | Model Dtype: {model_dtype} | AMP: {amp_status}")
    else:
        print(f"Device: {device} | Active GPUs: {num_gpus if num_gpus > 1 else 1} | Precision: {args.precision.upper()} | Model Dtype: {model_dtype} | AMP: {amp_status}")

    print(f"Model: {effective_model_name} ({gpt_config.get('n_layers', 12)} layers, {gpt_config.get('emb_dim', 768)} emb, {gpt_config.get('n_heads', 12)} heads)")

    if stage == STAGE_TRAIN:
        print(f"Batch Size: {args.batch_size} (Effective: {args.batch_size * args.accum_steps}) | Accum Steps: {args.accum_steps}")
        print(f"Epochs: {args.num_epochs} | AdamW LR: {args.learning_rate} | Muon LR: {args.muon_lr} | Warmup Steps: {args.warmup_steps}")
        print(f"Vocab: {gpt_config['vocab_size']:,} | Context: {gpt_config['context_length']} | Layers: {gpt_config['n_layers']} | Dim: {gpt_config['emb_dim']} | Heads: {gpt_config['n_heads']}")
        print(f"Training Data Path: {target_data_path}")
        print(f"Total training files found: {total_files}")
        for i, fp in enumerate(all_files, 1):
            print(f"  [{i}/{total_files}] {fp}")
    elif stage == STAGE_TUNE:
        print(f"Batch Size: {args.batch_size} (Accum Steps: {args.accum_steps}) | Epochs: {args.num_epochs} | Peak LR: {args.learning_rate:.6f}")
        print(f"Instruction Data: {target_data_path} ({total_files} file(s))")
        for i, fp in enumerate(all_files, 1):
            print(f"  [{i}/{total_files}] {fp.name}")
    else:
        print(f"Batch Size: {args.batch_size} (Accum Steps: {args.accum_steps}) | Epochs: {args.num_epochs} | LR: {args.learning_rate:.7f} | Beta: {args.beta}")
        print(f"Preference Data: {target_data_path} ({total_files} file(s))")
        for i, fp in enumerate(all_files, 1):
            print(f"  [{i}/{total_files}] {fp.name}")
        print(f"Base Model: {args.model_name}")
    print("=" * 65)

    # Model instantiation & acceleration
    model, reference_model = setup_model_and_acceleration(
        gpt_config=gpt_config,
        args=args,
        device=device,
        ref_device=ref_device,
        weight_dtype=weight_dtype,
        use_float8=use_float8,
        num_gpus=num_gpus,
        use_cuda=use_cuda,
        compute_dtype=amp_dtype,
    )
    policy_model = model if stage == STAGE_OPTIMIZE else None
    target_model = model
    replay_loader = None
    if stage == STAGE_OPTIMIZE and args.dpo_freeze_below_layer is not None:
        freeze_lower_layers(model, args.dpo_freeze_below_layer)

    # Optimizer setup
    optimizer = setup_stage_optimizer(
        target_model=target_model,
        args=args,
        use_cuda=use_cuda,
        weight_dtype=weight_dtype,
    )

    # Checkpoint resumption
    resumed = resume_stage_checkpoint(
        target_model=target_model,
        optimizer=optimizer,
        args=args,
        device=device,
        use_cuda=use_cuda,
    )
    if resumed is None:
        return

    resumed_step = resumed["resumed_step"]
    initial_epoch = resumed["initial_epoch"]
    resumed_step_in_epoch = resumed["resumed_step_in_epoch"]
    resumed_file_idx = resumed["resumed_file_idx"]
    resumed_step_in_file = resumed["resumed_step_in_file"]
    tokens_seen_init = resumed["tokens_seen_init"]
    accumulated_training_time = resumed["accumulated_training_time"]
    initial_train_losses = resumed["initial_train_losses"]
    initial_val_losses = resumed["initial_val_losses"]
    initial_track_tokens = resumed["initial_track_tokens"]
    initial_train_margins = resumed["initial_train_margins"]
    initial_val_margins = resumed["initial_val_margins"]

    tokenizer = get_tokenizer(gpt_config, args)
    num_workers = 2 if sys.platform != "win32" else 0

    if stage != STAGE_TRAIN:
        effective_max_length = args.max_length if args.max_length is not None else gpt_config.get("context_length", 1024)
        max_length = min(effective_max_length, gpt_config.get("context_length", 1024))

        if stage == STAGE_TUNE:
            start_context_entry = {"prompt": "Every effort moves you"}
            if all_files:
                try:
                    first_items = parse_instruction_text_file(all_files[0])
                    if first_items:
                        start_context_entry = next((e for e in first_items if len(format_input(e)) <= 2 * max_length), first_items[0])  # a prompt that leaves room for the sample reply (~half the context; the first Capybara DPO item is 1,335 tokens)
                except Exception:
                    pass

            train_loader, val_loader, test_data = create_instruction_dataloaders(
                data=all_files,
                tokenizer=tokenizer,
                args=args,
                max_length=max_length,
                num_workers=num_workers,
                device=device,
            )
        else:  # optimize
            start_context_entry = {"instruction": "Every effort moves you"}
            if all_files:
                try:
                    with open(all_files[0], "r", encoding="utf-8") as f:
                        fc = f.read().strip()
                        entries = json.loads(fc) if fc.startswith("[") else [json.loads(l) for l in fc.splitlines() if l.strip()]
                        if entries:
                            start_context_entry = next((e for e in entries if len(format_input(e)) <= 2 * max_length), entries[0])
                except Exception:
                    pass

            if args.json_precompute:
                for fp in all_files:
                    try:
                        with open(fp, "r", encoding="utf-8") as f:
                            c_data = json.load(f)
                        if isinstance(c_data, list) and c_data and not all("ref_chosen_logprob" in e and "ref_rejected_logprob" in e for e in c_data):
                            precompute_dataset_reference_logprobs(
                                preference_data=c_data,
                                args=args,
                                gpt_config=gpt_config,
                                tokenizer=tokenizer,
                                device=ref_device if ref_device != device else device,
                                max_length=max_length,
                                amp_dtype=amp_dtype,
                            )
                            with open(fp, "w", encoding="utf-8") as f:
                                json.dump(c_data, f, indent=2)
                    except Exception as pc_err:
                        print(f"[Precompute Warning] Could not check/annotate {fp.name}: {pc_err}")

            train_loader, val_loader, test_data = create_preference_dataloaders(
                data=all_files,
                tokenizer=tokenizer,
                args=args,
                max_length=max_length,
                num_workers=num_workers,
                device=device,
            )
            if args.dpo_replay_datasets:  # --dpo_replay_datasets: the model's own fine-tuning data for those sets, streamed next to the pairs with the SFT loss
                wanted = set(args.dpo_replay_datasets)
                replay_files = [f for f in resolve_data_files(resolve_path_with_override(args, stage=STAGE_TUNE), stage=STAGE_TUNE, models_dir=args.models_base_dir) if wanted & set(f.parts)]
                if not replay_files:
                    raise FileNotFoundError(f"--dpo_replay_datasets {sorted(wanted)}: no files under {resolve_path_with_override(args, stage=STAGE_TUNE)}; download them for this model first.")
                replay_args = copy.copy(args); replay_args.batch_size = args.dpo_replay_batch_size; replay_args.num_epochs_dataset_specific = None; replay_args.precompute_total_steps = False
                print(f"[DPO Replay] {len(replay_files)} fine-tuning file(s) from {sorted(wanted)} replayed with the SFT loss at weight {args.dpo_replay_weight}, {args.dpo_replay_batch_size} sequences per micro-step.")
                replay_loader, _, _ = create_instruction_dataloaders(data=replay_files, tokenizer=tokenizer, args=replay_args, max_length=max_length, num_workers=num_workers, device=device)

    # Engine Execution
    if stage == STAGE_TRAIN:
        if torch.cuda.is_available():
            torch.cuda.synchronize()

        train_losses, val_losses, tokens_seen, total_train_time = train_model_fully_optimized(
            model, all_files, optimizer, device, args,
            start_context="Every effort moves you", tokenizer=tokenizer,
            context_length=gpt_config["context_length"],
            max_grad_norm=1.0, amp_dtype=amp_dtype, num_workers=num_workers,
            gpt_config=gpt_config, resumed_step=resumed_step, initial_epoch=initial_epoch,
            resumed_step_in_epoch=resumed_step_in_epoch,
            tokens_seen_init=tokens_seen_init,
            initial_train_losses=initial_train_losses, initial_val_losses=initial_val_losses,
            initial_track_tokens=initial_track_tokens,
            use_amp=use_amp,
            accumulated_training_time=accumulated_training_time
        )

        if torch.cuda.is_available():
            torch.cuda.synchronize()
        total_tokens_int = tokens_seen if isinstance(tokens_seen, int) else (tokens_seen[-1] if isinstance(tokens_seen, (list, tuple)) and len(tokens_seen) > 0 else 0)
        param_count = count_model_parameters(model=model, config=gpt_config)

        print_stage_completion_summary(
            stage=STAGE_TRAIN,
            total_elapsed_time=total_train_time,
            total_tokens=total_tokens_int,
            train_loss=train_losses[-1] if train_losses else None,
            val_loss=val_losses[-1] if val_losses else None,
            model_name=args.model_name,
            param_count=param_count,
        )

        plot_training_losses(
            tokens_seen=tokens_seen if isinstance(tokens_seen, list) else [tokens_seen],
            train_losses=train_losses,
            val_losses=val_losses,
            args=args,
        )

    elif stage == STAGE_TUNE:
        if torch.cuda.is_available():
            torch.cuda.synchronize()

        train_losses, val_losses, track_tokens, track_epochs, total_train_time, val_seq_losses = train_model_instruction_fully_optimized(
            model=model,
            train_loader=train_loader,
            val_loader=val_loader,
            optimizer=optimizer,
            device=device,
            args=args,
            start_context_entry=start_context_entry,
            tokenizer=tokenizer,
            resumed_step=resumed_step,
            tokens_seen_init=tokens_seen_init,
            initial_epoch=initial_epoch,
            resumed_step_in_epoch=resumed_step_in_epoch,
            initial_train_losses=initial_train_losses,
            initial_val_losses=initial_val_losses,
            initial_track_tokens=initial_track_tokens,
            amp_dtype=amp_dtype,
            gpt_config=gpt_config,
            use_amp=use_amp,
            accumulated_training_time=accumulated_training_time
        )

        if torch.cuda.is_available():
            torch.cuda.synchronize()
        total_tokens_int = track_tokens[-1] if track_tokens else 0
        param_count = count_model_parameters(model=model, config=gpt_config)

        print_stage_completion_summary(
            stage=STAGE_TUNE,
            total_elapsed_time=total_train_time,
            total_tokens=total_tokens_int,
            train_loss=train_losses[-1] if train_losses else None,
            val_loss=val_losses[-1] if val_losses else None,
            model_name=args.model_name,
            param_count=param_count,
            val_seq_loss=val_seq_losses[-1] if val_seq_losses else None,
        )

        plot_tuning_losses(
            epochs_seen=track_epochs,
            tokens_seen=track_tokens,
            train_losses=train_losses,
            val_losses=val_losses,
            args=args,
        )

    else:  # optimize
        if args.json_precompute:
            train_losses, val_losses, train_margins, val_margins, track_tokens, track_epochs, total_train_time = train_model_dpo_precomputed(
                policy_model=policy_model,
                train_loader=train_loader,
                val_loader=val_loader,
                optimizer=optimizer,
                device=device,
                args=args,
                start_context_entry=start_context_entry,
                tokenizer=tokenizer,
                gpt_config=gpt_config,
                initial_epoch=initial_epoch,
                resumed_step=resumed_step,
                resumed_step_in_epoch=resumed_step_in_epoch,
                tokens_seen_init=tokens_seen_init,
                initial_train_losses=initial_train_losses,
                initial_val_losses=initial_val_losses,
                initial_train_margins=initial_train_margins,
                initial_val_margins=initial_val_margins,
                initial_track_tokens=initial_track_tokens,
                amp_dtype=amp_dtype,
                use_amp=use_amp,
                accumulated_training_time=accumulated_training_time
            )
        else:
            train_losses, val_losses, train_margins, val_margins, track_tokens, track_epochs, total_train_time = train_model_dpo_fully_optimized(
                policy_model=policy_model,
                reference_model=reference_model,
                train_loader=train_loader,
                val_loader=val_loader,
                optimizer=optimizer,
                device=device,
                ref_device=ref_device,
                args=args,
                start_context_entry=start_context_entry,
                tokenizer=tokenizer,
                gpt_config=gpt_config,
                initial_epoch=initial_epoch,
                resumed_step=resumed_step,
                resumed_step_in_epoch=resumed_step_in_epoch,
                tokens_seen_init=tokens_seen_init,
                initial_train_losses=initial_train_losses,
                initial_val_losses=initial_val_losses,
                initial_train_margins=initial_train_margins,
                initial_val_margins=initial_val_margins,
                initial_track_tokens=initial_track_tokens,
                amp_dtype=amp_dtype,
                use_amp=use_amp,
                accumulated_training_time=accumulated_training_time,
                replay_loader=replay_loader,
                replay_weight=args.dpo_replay_weight,
            )

        plot_dpo_losses_and_margins(
            epochs_seen=track_epochs,
            tokens_seen=track_tokens,
            train_losses=train_losses,
            val_losses=val_losses,
            train_margins=train_margins,
            val_margins=val_margins,
            args=args,
        )


if __name__ == "__main__":
    with sdpa_kernel(SDPA_BACKENDS, set_priority=True):
        main()
