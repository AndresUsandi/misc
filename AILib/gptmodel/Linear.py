import contextlib
from typing import Optional

import torch
import torch.nn as nn
import torch.nn.functional as F


def safe_linear(x: torch.Tensor, weight: torch.Tensor, bias: Optional[torch.Tensor] = None) -> torch.Tensor:
    """Executes linear projection with native FP8 support on Ada/Blackwell GPUs or safe fallback."""
    is_autocast_f8 = (
        x.is_cuda and
        torch.is_autocast_enabled("cuda") and
        hasattr(torch, "float8_e4m3fn") and
        (torch.get_autocast_dtype("cuda") in (torch.float8_e4m3fn, getattr(torch, "float8_e5m2", None)))
    )
    is_f8 = (
        is_autocast_f8 or
        (hasattr(torch, "float8_e4m3fn") and (
            x.dtype in (torch.float8_e4m3fn, getattr(torch, "float8_e5m2", None)) or
            weight.dtype in (torch.float8_e4m3fn, getattr(torch, "float8_e5m2", None))
        ))
    )
    if is_f8:
        if x.is_cuda and hasattr(torch, "_scaled_mm"):
            try:
                cap = torch.cuda.get_device_capability(x.device)
                if cap >= (8, 9):
                    x_shape = x.shape
                    x_flat = x.reshape(-1, x_shape[-1])
                    f8_dtype = torch.float8_e4m3fn
                    x_f8 = x_flat if x_flat.dtype == f8_dtype else x_flat.to(f8_dtype)
                    w_f8 = weight if weight.dtype == f8_dtype else weight.to(f8_dtype)
                    scale_a = torch.tensor(1.0, device=x.device)
                    scale_b = torch.tensor(1.0, device=x.device)
                    out_dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
                    out, _ = torch._scaled_mm(
                        x_f8, w_f8.t(),
                        out_dtype=out_dtype,
                        scale_a=scale_a, scale_b=scale_b
                    )
                    if bias is not None:
                        out = out + bias.to(out.dtype)
                    ret_dtype = x.dtype if x.dtype != f8_dtype else out_dtype
                    return out.to(ret_dtype).reshape(*x_shape[:-1], weight.shape[0])
            except Exception:
                pass
        comp_dtype = torch.bfloat16 if (x.is_cuda and torch.cuda.is_bf16_supported()) else torch.float16
        with torch.amp.autocast("cuda", enabled=False) if x.is_cuda else contextlib.nullcontext():
            out = F.linear(x.to(comp_dtype), weight.to(comp_dtype), bias.to(comp_dtype) if bias is not None else None)
        return out.to(x.dtype)
    return F.linear(x, weight, bias)
    
class Linear(nn.Linear):
    """Drop-in nn.Linear subclass supporting native FP8 hardware tensor cores and automatic precision casting."""
    def forward(self, input: torch.Tensor) -> torch.Tensor:
        return safe_linear(input, self.weight, self.bias)
