from typing import Any, Dict

import torch
import torch.nn as nn
import torch.nn.functional as F

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from gptmodel.Linear import Linear
from gptmodel.Modules import GELU


class FeedForward(nn.Module):
    def __init__(self, cfg: Dict[str, Any]):
        super().__init__()
        emb_dim = cfg["emb_dim"]
        self.ffn_type = cfg.get("ffn_type", "swiglu" if cfg.get("arch_family") in ["llama3", "qwen3", "gemma"] else "gelu").lower()

        if self.ffn_type == "swiglu":
            hidden_dim = cfg.get("hidden_dim", int(8 / 3 * emb_dim))
            self.fc1 = Linear(emb_dim, hidden_dim, bias=False)
            self.fc2 = Linear(emb_dim, hidden_dim, bias=False)
            self.fc3 = Linear(hidden_dim, emb_dim, bias=False)
        else:
            hidden_dim = cfg.get("hidden_dim", 4 * emb_dim)
            self.fc1 = Linear(emb_dim, hidden_dim)
            self.act = GELU()
            self.fc2 = Linear(hidden_dim, emb_dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if self.ffn_type == "swiglu":
            h1 = self.fc1(x)
            h2 = self.fc2(x)
            if hasattr(torch, "float8_e4m3fn") and h1.dtype in (torch.float8_e4m3fn, getattr(torch, "float8_e5m2", None)):
                act = (F.silu(h1.float()) * h2.float()).to(h1.dtype)
            else:
                act = F.silu(h1) * h2
            return self.fc3(act)
        return self.fc2(self.act(self.fc1(x)))

