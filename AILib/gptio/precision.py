# Copyright (c) Sebastian Raschka under Apache License 2.0 (see LICENSE.txt).
# Precision and Automatic Mixed Precision (AMP) utilities for GPT models.

from pathlib import Path
import sys
from typing import Any, Optional, Tuple, Union

import torch

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from gptutils.consoleutils import print

PRECISION_FP8: str = "fp8"


def is_fp8_supported(device: Optional[Union[str, torch.device]] = None) -> bool:
    """
    Checks whether native hardware FP8 (Float8) tensor core compute is supported.
    Requires NVIDIA GPU with Compute Capability >= 8.9 (Ada Lovelace, Hopper, Blackwell like RTX 40-series, H100, RTX 5070 Ti).
    """
    if not torch.cuda.is_available():
        return False
    if not hasattr(torch, "float8_e4m3fn"):
        return False
    try:
        if device is None:
            dev = torch.device("cuda:0")
        elif isinstance(device, str):
            dev = torch.device(device)
        else:
            dev = device
        if dev.type != "cuda":
            return False
        cap = torch.cuda.get_device_capability(dev)
        return cap >= (8, 9)
    except Exception:
        return False


def get_supported_precision_dtype(device: Optional[torch.device], precision: str = "fp16") -> torch.dtype:
    """
    Resolves requested precision ('fp16', 'fp8', or 'fp32') to the optimal concrete torch.dtype.
    Always returns a valid torch.dtype (e.g. torch.float32, torch.bfloat16, torch.float16, or torch.float8_e4m3fn).
    """
    if device is None or getattr(device, "type", "") != "cuda":
        return torch.float32

    p = str(precision).lower().strip() if precision is not None else "fp16"
    if p in ("fp32", "float32", "32"):
        return torch.float32

    try:
        cap = torch.cuda.get_device_capability(device)
    except Exception:
        cap = (0, 0)

    if p in ("fp8", "float8", "8", "8bit"):
        if is_fp8_supported(device):
            return torch.float8_e4m3fn
        else:
            cap_str = f"Compute {cap[0]}.{cap[1]}"
            dev_name = torch.cuda.get_device_name(device) if torch.cuda.is_available() else "CUDA device"
            print(
                f"[Precision Warning] FP8 precision requested, but {dev_name} ({cap_str}) does not support "
                f"native FP8 compute (requires Compute Capability >= 8.9, e.g. RTX 5070 Ti, RTX 40-series, H100). "
                f"Falling back safely to FP16/BF16."
            )
            if cap[0] >= 8 and torch.cuda.is_bf16_supported():
                return torch.bfloat16
            return torch.float16

    # Default: fp16
    if cap[0] >= 8 and torch.cuda.is_bf16_supported():
        return torch.bfloat16
    return torch.float16


def resolve_precision_and_amp(
    device: Optional[torch.device],
    precision: str = "fp16"
) -> Tuple[torch.dtype, bool, Optional[torch.dtype]]:
    """
    Resolves precision configuration into:
    1. model_dtype: Concrete torch.dtype for weights/models (torch.float32, torch.bfloat16, torch.float16).
       For 'fp8' the master weights and autocast stay bf16/fp16; the fp8 tensor-core matmuls come from converting the
       Linear layers with torchao (GptModel.convert_to_float8), not from fp8-typed weights or autocast.
    2. use_amp: Boolean flag indicating if automatic mixed precision is active on CUDA.
    3. amp_dtype: Target dtype for torch.amp.autocast, or None if use_amp is False.
    """
    model_dtype = get_supported_precision_dtype(device, precision=precision)
    if model_dtype == getattr(torch, "float8_e4m3fn", None):
        model_dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
    use_cuda = device is not None and getattr(device, "type", "") == "cuda"
    use_amp = use_cuda and (model_dtype != torch.float32)
    amp_dtype = model_dtype if use_amp else None
    return model_dtype, use_amp, amp_dtype


def get_supported_amp_dtype(device: Optional[torch.device], precision: str = "fp16") -> Optional[torch.dtype]:
    """Helper returning target dtype for AMP autocast (None when AMP is inactive or FP32)."""
    _, _, amp_dtype = resolve_precision_and_amp(device, precision=precision)
    return amp_dtype


class Fp16GradScaler(torch.amp.GradScaler):
    """GradScaler for float16 weights. Without loss scaling, small gradients round to zero in float16 during the backward pass.
    GradScaler refuses float16 gradients because unscaling them can round the tiniest values to zero again, but that costs
    little: the scaling already kept the backward pass itself accurate."""
    def _unscale_grads_(self, optimizer, inv_scale, found_inf, allow_fp16):
        return super()._unscale_grads_(optimizer, inv_scale, found_inf, True)


def create_grad_scaler(
    model: torch.nn.Module,
    device: Optional[torch.device],
    use_amp: bool = False,
    amp_dtype: Optional[torch.dtype] = None,
    fine_tuning: bool = False,
) -> Optional[Any]:
    """
    Instantiates a CUDA GradScaler when using FP16 mixed precision with FP32 parameters, or an Fp16GradScaler for fine-tuning/DPO
    with FP16 parameters. GradScaler is not needed for BFloat16 or FP8, whose range matches FP32.
    """
    use_cuda = device is not None and getattr(device, "type", "") == "cuda"
    if not (use_cuda and use_amp and amp_dtype == torch.float16):
        return None
    trainable_dtypes = {p.dtype for p in model.parameters() if p.requires_grad}
    if fine_tuning and trainable_dtypes == {torch.float16}:
        print("[Precision] Dynamic loss scaling enabled so small fp16 gradients don't round to zero in the backward pass.")
        return Fp16GradScaler("cuda")
    if trainable_dtypes != {torch.float32}:
        return None
    return torch.amp.GradScaler("cuda")
