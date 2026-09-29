# Copyright (c) Sebastian Raschka under Apache License 2.0 (see LICENSE.txt).
# Model instantiation, acceleration wrappers, and reference model setup for GPT training pipelines.

from pathlib import Path
import sys
from typing import Any, Dict, Optional, Tuple

import torch
import torch.nn as nn

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from argsutil import TrainingArgs
from gptmodel.GptModel import GptModel
from gptmodel.MultiGpuGptModelPP import MultiGpuGptModelPP
from gptmodel.MultiGpuGptModelDP import MultiGpuGptModelDP
from gptio.pathutil import (
    STAGE_TRAIN,
    STAGE_TUNE,
    STAGE_OPTIMIZE,
    MULTI_GPU_DP,
)
from gptio.checkpoint import (
    load_checkpoint,
    restore_training_state,
)
from gptio.modelio import load_model_weights
from gptutils.consoleutils import print
from gpttrain.train.system_check import check_torch_compile_working


def setup_model_and_acceleration(
    gpt_config: Dict[str, Any],
    args: TrainingArgs,
    device: torch.device,
    ref_device: torch.device,
    weight_dtype: torch.dtype,
    use_float8: bool,
    num_gpus: int,
    use_cuda: bool,
) -> Tuple[nn.Module, Optional[nn.Module]]:
    """
    Instantiates model architecture, applies low-VRAM options (FP8, grad checkpointing, frozen embeddings),
    attaches multi-GPU wrappers (DP / PP), applies torch.compile, and instantiates reference model for DPO.
    Returns (model, reference_model).
    """
    stage = args.stage
    model = GptModel(gpt_config)
    model.recompute_lmhead = args.recompute_lmhead
    if use_float8:
        model.convert_to_float8()
        print(f"[Precision] Float8 training: Linear layers converted to torchao Float8Linear (tensorwise dynamic scaling, bf16 master weights).{'' if args.compile else ' WARNING: enable --compile, eager fp8 is slower than fp16.'}")

    use_grad_ckpt = args.activation_checkpointing
    if use_grad_ckpt:
        print(f"[Low-VRAM Optimization] Activation / Gradient Checkpointing enabled (cuts activation VRAM by ~80%).")

    if args.freeze_embeddings and stage != STAGE_TRAIN:
        if hasattr(model, "tok_emb"):
            for p in model.tok_emb.parameters():
                p.requires_grad = False
        if hasattr(model, "pos_emb") and model.pos_emb is not None:
            for p in model.pos_emb.parameters():
                p.requires_grad = False
        print(f"[Low-VRAM Optimization] Token and position embeddings frozen (requires_grad = False).")

    reference_model = None
    if stage == STAGE_TRAIN:
        model.to(device=device, dtype=weight_dtype)
        if num_gpus > 1:
            dev_idx = device.index if device.index is not None else 0
            gpu_devices = [torch.device(f"cuda:{(dev_idx + i) % num_gpus}") for i in range(num_gpus)]
            if args.multi_gpu_strategy == MULTI_GPU_DP:
                print(f"Multi-GPU Mode: Wrapping model in MultiGpuGptModelDP across {num_gpus} GPUs (Data Parallelism, compile={args.compile}, primary={device})!")
                model = MultiGpuGptModelDP(model, devices=gpu_devices, compile=args.compile)
            else:
                use_uneven_layers = not args.even_layers
                split_desc = "even (50% GPU 0 / 50% GPU 1)" if args.even_layers else "uneven (60% GPU 0 / 40% GPU 1, default)"
                mb_desc = f"{args.multi_stage_micro_batching} stages" if args.multi_stage_micro_batching >= 2 else "disabled"
                print(f"Multi-GPU Mode: Wrapping model in MultiGpuGptModelPP across {num_gpus} GPUs (Layers: {split_desc}, async_pcie={args.async_pcie}, micro_batching={mb_desc}, 1f1b={args.use_1f1b}, primary={device})!")
                model = MultiGpuGptModelPP(model, uneven_layers=use_uneven_layers, async_pcie=args.async_pcie, use_1f1b=args.use_1f1b, multi_stage_micro_batching=args.multi_stage_micro_batching, devices=gpu_devices)
        if args.compile:
            if isinstance(model, (MultiGpuGptModelDP, MultiGpuGptModelPP)):
                pass
            elif check_torch_compile_working(device):
                try:
                    print("Applying torch.compile(model.forward_features)...")
                    model.compiled_forward_features = torch.compile(model.forward_features)
                    model.compiled_chunked_loss = torch.compile(model.chunked_loss)
                except Exception as e:
                    print(f"torch.compile skipped ({e})")
            else:
                print("torch.compile skipped (Triton compiler toolchain not installed or unsupported on this GPU/OS)")
        else:
            print("torch.compile skipped (default: disabled, use --compile to enable)")
    elif stage == STAGE_TUNE:
        model.to(device=device, dtype=weight_dtype)
        if use_cuda and not args.single_gpu and num_gpus > 1:
            dev_idx = device.index if device.index is not None else 0
            gpu_devices = [torch.device(f"cuda:{(dev_idx + i) % num_gpus}") for i in range(num_gpus)]
            if args.multi_gpu_strategy == MULTI_GPU_DP:
                print(f"Multi-GPU Mode: Wrapping model in MultiGpuGptModelDP across {num_gpus} GPUs (Data Parallelism, compile={args.compile}, primary={device})!")
                model = MultiGpuGptModelDP(model, devices=gpu_devices, compile=args.compile)
            else:
                use_uneven_layers = not args.even_layers
                split_desc = "even (50% GPU 0 / 50% GPU 1)" if args.even_layers else "uneven (60% GPU 0 / 40% GPU 1, default)"
                print(f"Multi-GPU Mode: Wrapping model in MultiGpuGptModelPP across {num_gpus} GPUs (Layers: {split_desc}, primary={device})!")
                model = MultiGpuGptModelPP(model, uneven_layers=use_uneven_layers, devices=gpu_devices)
    else:  # optimize
        policy_model = model
        policy_model.to(device=device, dtype=weight_dtype)
        policy_model.to(device)
        if not args.json_precompute:
            reference_model = GptModel(gpt_config)
            if use_float8:
                reference_model.convert_to_float8()
            reference_model.to(device=ref_device, dtype=weight_dtype)
            reference_model.to(ref_device)
            for param in reference_model.parameters():
                param.requires_grad = False
            reference_model.eval()

            ref_ckpt = load_checkpoint(args, stage=STAGE_TUNE, device="cpu", silent=True)
            if ref_ckpt is not None:
                restore_training_state(reference_model, ref_ckpt, device=ref_device)
                ref_src = "SFT checkpoint (.sft.chk)" if ref_ckpt.get("is_sft") else "pre-training checkpoint (.trn.chk)"
                del ref_ckpt
                if use_cuda:
                    torch.cuda.empty_cache()
                print(f"[Reference Model] Initialized frozen reference model from {ref_src} on {ref_device}.")
            else:
                load_model_weights(reference_model, args, device=ref_device)
                print(f"[Reference Model] No SFT/pre-training checkpoint found; initialized frozen reference model from base model weights (.pth) on {ref_device}.")
        else:
            reference_model = None
            print(f"[Precompute Mode] Zero Reference Model VRAM enabled (--json_precompute). Reference model will not be loaded into GPU memory during training.")
        model = policy_model

    return model, reference_model
