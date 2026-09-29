import torch
import torch.nn as nn
import torch.nn.functional as F

class SafeDropout(nn.Module):
    """Dropout module supporting Float8 tensors by executing masked dropout in float32 when required."""
    def __init__(self, p: float = 0.0):
        super().__init__()
        self.p = p

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if self.p == 0.0 or not self.training:
            return x
        if hasattr(torch, "float8_e4m3fn") and x.dtype in (torch.float8_e4m3fn, getattr(torch, "float8_e5m2", None)):
            return F.dropout(x.float(), p=self.p, training=True).to(x.dtype)
        return F.dropout(x, p=self.p, training=True)

class RMSNorm(nn.Module):
    def __init__(self, emb_dim: int, eps: float = 1e-5):
        super().__init__()
        self.eps = eps
        self.scale = nn.Parameter(torch.ones(emb_dim))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        input_dtype = x.dtype
        x_f = x.float()
        variance = x_f.pow(2).mean(-1, keepdim=True)
        norm = x_f * torch.rsqrt(variance + self.eps)
        return (self.scale.float() * norm).to(input_dtype)

class LayerNorm(nn.Module):
    def __init__(self, emb_dim: int, eps: float = 1e-5):
        super().__init__()
        self.eps = eps
        self.scale = nn.Parameter(torch.ones(emb_dim))
        self.shift = nn.Parameter(torch.zeros(emb_dim))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if hasattr(torch, "float8_e4m3fn") and x.dtype in (torch.float8_e4m3fn, getattr(torch, "float8_e5m2", None)):
            return F.layer_norm(x.float(), (x.shape[-1],), self.scale.float(), self.shift.float(), eps=self.eps).to(x.dtype)
        return F.layer_norm(x, (x.shape[-1],), self.scale, self.shift, eps=self.eps)

class GELU(nn.Module):
    def __init__(self):
        super().__init__()
        self.gelu = nn.GELU(approximate="tanh")

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if hasattr(torch, "float8_e4m3fn") and x.dtype in (torch.float8_e4m3fn, getattr(torch, "float8_e5m2", None)):
            return self.gelu(x.float()).to(x.dtype)
        return self.gelu(x)

class GemmaRMSNorm(nn.Module):
    def __init__(self, emb_dim: int, eps: float = 1e-6):
        super().__init__()
        self.eps = eps
        self.scale = nn.Parameter(torch.zeros(emb_dim))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        input_dtype = x.dtype
        x_f = x.float()
        variance = x_f.pow(2).mean(-1, keepdim=True)
        norm = x_f * torch.rsqrt(variance + self.eps)
        return ((1.0 + self.scale.float()) * norm).to(input_dtype)
