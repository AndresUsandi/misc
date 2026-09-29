import dataclasses
import math
from typing import Any, Dict, Optional, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.utils.checkpoint
from torchao.float8 import convert_to_float8_training, Float8LinearConfig


from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from gptmodel.Modules import SafeDropout
from gptmodel.Transformer import TransformerBlock, safe_add, create_norm
from gptmodel.Linear import Linear

LOGIT_CLAMP_MIN: float = -50.0
LOGIT_CLAMP_MAX: float = 50.0
UNEVEN_LAYERS_GPU0_RATIO: float = 0.60
FLOAT8_RECIPE: str = "tensorwise"  # rowwise scaling is not supported by torch._scaled_mm on consumer Blackwell (sm_120)
# Compiled variants of forward_features/chunked_loss are bounded (per GPU x train/eval x Inductor size classes) but exceed Dynamo's default of 8;
# past the limit a function silently runs eager. The value is thread-local, so it must be set in every thread that compiles (see MultiGpuGptModelDP)
DYNAMO_RECOMPILE_LIMIT: int = 64

def compute_rope_params(head_dim: int, theta_base: float = 10_000.0, context_length: int = 4096, freq_config: Optional[dict] = None) -> Tuple[torch.Tensor, torch.Tensor]:
    assert head_dim % 2 == 0, "head_dim must be even for RoPE"
    inv_freq = 1.0 / (theta_base ** (torch.arange(0, head_dim, 2).float() / head_dim))

    if freq_config is not None:
        low_freq_factor = freq_config.get("low_freq_factor", 1.0)
        high_freq_factor = freq_config.get("high_freq_factor", 4.0)
        old_context_length = freq_config.get("original_context_length", 8192)
        low_freq_wavelen = old_context_length / low_freq_factor
        high_freq_wavelen = old_context_length / high_freq_factor
        wavelen = 2 * math.pi / inv_freq
        inv_freq_llama = torch.where(wavelen > low_freq_wavelen, inv_freq / freq_config.get("factor", 32.0), inv_freq)
        smooth_factor = (old_context_length / wavelen - low_freq_factor) / (high_freq_factor - low_freq_factor)
        smooth_inv_freq = (1 - smooth_factor) * (inv_freq / freq_config.get("factor", 32.0)) + smooth_factor * inv_freq
        is_medium_freq = ~(wavelen < high_freq_wavelen) * ~(wavelen > low_freq_wavelen)
        inv_freq = torch.where(is_medium_freq, smooth_inv_freq, inv_freq_llama)

    positions = torch.arange(context_length)
    angles = positions.unsqueeze(1) * inv_freq.unsqueeze(0)
    angles = torch.cat([angles, angles], dim=1)
    cos = torch.cos(angles)
    sin = torch.sin(angles)
    return cos, sin

class GptModel(nn.Module):
    def __init__(self, cfg: Dict[str, Any]):
        super().__init__()
        self.cfg = cfg
        self.tok_emb = nn.Embedding(cfg["vocab_size"], cfg["emb_dim"])

        self.pos_emb_type = cfg.get("pos_emb_type", "rope" if cfg.get("arch_family") in ["llama3", "qwen3", "gemma"] else "absolute").lower()
        if self.pos_emb_type == "absolute":
            self.pos_emb = nn.Embedding(cfg["context_length"], cfg["emb_dim"])
        else:
            self.pos_emb = None
            head_dim = cfg.get("head_dim", cfg["emb_dim"] // cfg["n_heads"])
            cos, sin = compute_rope_params(
                head_dim=head_dim,
                theta_base=cfg.get("rope_base", 10_000.0 if cfg.get("arch_family") != "llama3" else 500_000.0),
                context_length=cfg.get("context_length", 4096),
                freq_config=cfg.get("rope_freq", None)
            )
            self.register_buffer("cos", cos, persistent=False)
            self.register_buffer("sin", sin, persistent=False)

        self.drop_emb = SafeDropout(cfg.get("drop_rate", 0.0))
        self.trf_blocks = nn.ModuleList([TransformerBlock(cfg) for _ in range(cfg["n_layers"])])
        self.n_kv_producing_layers = cfg.get("n_kv_producing_layers", cfg["n_layers"])
        self.current_pos = 0

        self.final_norm = create_norm(cfg, cfg["emb_dim"])
        self.out_head = Linear(cfg["emb_dim"], cfg["vocab_size"], bias=False)
        self.recompute_lmhead = True

        # Standard GPT weight initialization (std=0.02)
        self.apply(self._init_weights)

        # Scale residual projection layers by 1 / sqrt(2 * n_layers) (GPT-2 standard)
        res_std = 0.02 / math.sqrt(2 * max(cfg["n_layers"], 1))
        for blk in self.trf_blocks:
            torch.nn.init.normal_(blk.att.out_proj.weight, mean=0.0, std=res_std)
            if hasattr(blk.ff, "fc3"):
                torch.nn.init.normal_(blk.ff.fc3.weight, mean=0.0, std=res_std)
            elif hasattr(blk.ff, "fc2"):
                torch.nn.init.normal_(blk.ff.fc2.weight, mean=0.0, std=res_std)

        if cfg.get("tie_embeddings", cfg.get("tie_word_embeddings", False)):
            self.out_head.weight = self.tok_emb.weight

    def _init_weights(self, module: nn.Module):
        if isinstance(module, nn.Linear):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if module.bias is not None:
                torch.nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)

    def forward_features(self, in_idx: torch.Tensor, use_cache: bool = False, activation_checkpointing: bool = False) -> torch.Tensor:
        batch_size, seq_len = in_idx.shape
        x = self.tok_emb(in_idx)

        cos = getattr(self, "cos", None)
        sin = getattr(self, "sin", None)

        if use_cache:
            pos_ids = torch.arange(self.current_pos, self.current_pos + seq_len, device=in_idx.device, dtype=torch.long)
            self.current_pos += seq_len
        else:
            pos_ids = torch.arange(0, seq_len, device=in_idx.device, dtype=torch.long)

        if self.pos_emb_type == "absolute" and self.pos_emb is not None:
            x = safe_add(x, self.pos_emb(pos_ids).unsqueeze(0))

        x = self.drop_emb(x)

        use_ckpt = activation_checkpointing and self.training and not use_cache and not isinstance(x, tuple)
        shared_kv = None
        for layer_idx, blk in enumerate(self.trf_blocks):
            if use_ckpt:
                cur_shared = shared_kv if layer_idx >= self.n_kv_producing_layers else None
                x, shared_kv = torch.utils.checkpoint.checkpoint(
                    blk, x, use_cache, cur_shared, cos, sin, pos_ids, use_reentrant=False
                )
            else:
                if layer_idx < self.n_kv_producing_layers:
                    x, shared_kv = blk(x, use_cache=use_cache, shared_kv=None, cos=cos, sin=sin, pos_ids=pos_ids)
                else:
                    x, _ = blk(x, use_cache=use_cache, shared_kv=shared_kv, cos=cos, sin=sin, pos_ids=pos_ids)

        x = self.final_norm(x)
        return x

    def forward(self, in_idx: torch.Tensor, use_cache: bool = False, activation_checkpointing: bool = False) -> torch.Tensor:
        x = self.forward_features(in_idx, use_cache=use_cache, activation_checkpointing=activation_checkpointing)
        logits = self.out_head(x)
        return logits

    def chunked_loss(self, hidden: torch.Tensor, targets: torch.Tensor, chunk_size: int = 512) -> torch.Tensor:
        """Token-mean cross-entropy over the LM head in chunks; the fp32 softmax is always recomputed in backward, and with recompute_lmhead the head projection is too (otherwise each chunk's bf16 logits stay in VRAM)."""
        flat_hidden = hidden.view(-1, hidden.shape[-1])
        flat_targets = targets.view(-1)
        total_loss = 0.0
        # Chunk count as a ceil-division of the token count: under torch.compile Dynamo guards on the value of this expression, so with
        # variable SFT/DPO shapes it only recompiles when the number of chunks changes (a token-count loop would re-specialize on every
        # length, exhaust the recompile limit and silently fall back to eager with fp32 logits in VRAM)
        num_chunks = max(1, -(-flat_targets.numel() // chunk_size))
        for h, t in zip(flat_hidden.tensor_split(num_chunks), flat_targets.tensor_split(num_chunks)):
            if self.recompute_lmhead:
                total_loss = total_loss + torch.utils.checkpoint.checkpoint(self._chunk_loss, h, t, use_reentrant=False)
            else:
                total_loss = total_loss + torch.utils.checkpoint.checkpoint(self._chunk_ce, self.out_head(h), t, use_reentrant=False)
        return total_loss / (flat_targets != -100).sum().clamp(min=1)

    def _chunk_loss(self, hidden_chunk: torch.Tensor, target_chunk: torch.Tensor) -> torch.Tensor:
        return self._chunk_ce(self.out_head(hidden_chunk), target_chunk)

    def _chunk_ce(self, logits_chunk: torch.Tensor, target_chunk: torch.Tensor) -> torch.Tensor:
        logits = torch.clamp(logits_chunk.float(), min=LOGIT_CLAMP_MIN, max=LOGIT_CLAMP_MAX)
        return F.cross_entropy(logits, target_chunk, reduction="sum")

    def convert_to_float8(self):
        """Swaps every Linear (including the tied LM head) for a torchao Float8Linear: fp8 tensor-core matmuls with tensorwise dynamic scaling and bf16 master weights (parameter names and checkpoints stay unchanged). Only pays off under torch.compile; eager fp8 is slower than bf16."""
        # pad_inner_dim: fp8 GEMMs need 16-aligned inner dims; token counts are only aligned in pretraining (SFT pads batches to arbitrary lengths)
        convert_to_float8_training(self, config=dataclasses.replace(Float8LinearConfig.from_recipe_name(FLOAT8_RECIPE), pad_inner_dim=True))

    def reset_kv_cache(self):
        for blk in self.trf_blocks:
            blk.att.reset_cache()
        self.current_pos = 0

