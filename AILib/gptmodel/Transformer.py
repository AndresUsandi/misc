from typing import Any, Dict, Optional, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F


from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from gptmodel.FeedForward import FeedForward
from gptmodel.Attention import OptimizedGroupedQueryAttention
from gptmodel.Modules import GemmaRMSNorm, RMSNorm, LayerNorm, SafeDropout


def create_norm(cfg: Dict[str, Any], emb_dim: int) -> nn.Module:
    norm_type = cfg.get("norm_type", "rmsnorm" if cfg.get("arch_family") in ["llama3", "qwen3", "gemma"] else "layernorm").lower()
    eps = cfg.get("norm_eps", 1e-6 if norm_type == "gemma_rmsnorm" else 1e-5)
    if norm_type == "gemma_rmsnorm":
        return GemmaRMSNorm(emb_dim, eps=eps)
    elif norm_type == "rmsnorm":
        return RMSNorm(emb_dim, eps=eps)
    return LayerNorm(emb_dim, eps=eps)


def safe_add(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    """Safely adds two tensors with support for FP8 dtypes lacking native CUDA ufunc_add."""
    if hasattr(torch, "float8_e4m3fn") and (
        a.dtype in (torch.float8_e4m3fn, getattr(torch, "float8_e5m2", None)) or
        b.dtype in (torch.float8_e4m3fn, getattr(torch, "float8_e5m2", None))
    ):
        return (a.float() + b.float()).to(a.dtype)
    return a + b


class TransformerBlock(nn.Module):
    def __init__(self, cfg: Dict[str, Any]):
        super().__init__()
        self.att = OptimizedGroupedQueryAttention(cfg)
        self.ff = FeedForward(cfg)
        self.norm1 = create_norm(cfg, cfg["emb_dim"])
        self.norm2 = create_norm(cfg, cfg["emb_dim"])
        self.drop_shortcut = SafeDropout(cfg.get("drop_rate", 0.0))

    def forward(self, x: torch.Tensor, use_cache: bool = False, shared_kv: Optional[Tuple[torch.Tensor, torch.Tensor]] = None,
                cos: Optional[torch.Tensor] = None, sin: Optional[torch.Tensor] = None, pos_ids: Optional[torch.Tensor] = None):
        shortcut = x
        x = self.norm1(x)
        x, new_shared_kv = self.att(x, use_cache=use_cache, shared_kv=shared_kv, cos=cos, sin=sin, pos_ids=pos_ids)
        x = self.drop_shortcut(x)
        x = safe_add(x, shortcut)

        shortcut = x
        x = self.norm2(x)
        x = self.ff(x)
        x = self.drop_shortcut(x)
        x = safe_add(x, shortcut)
        return x, new_shared_kv

