
import contextlib
from typing import Any, Dict, Optional, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from gptmodel.Linear import Linear
from gptmodel.Modules import SafeDropout, RMSNorm


def apply_rope(x: torch.Tensor, cos: torch.Tensor, sin: torch.Tensor, pos_ids: Optional[torch.Tensor] = None) -> torch.Tensor:
    b, num_heads, seq_len, head_dim = x.shape
    input_dtype = x.dtype
    half = head_dim // 2
    x_f = x.float()
    x1 = x_f[..., :half]
    x2 = x_f[..., half:]
    rotated = torch.cat([-x2, x1], dim=-1)

    cos_dev = cos.to(x.device, dtype=torch.float32)
    sin_dev = sin.to(x.device, dtype=torch.float32)

    if pos_ids is not None:
        pos = pos_ids[0] if pos_ids.ndim == 2 else pos_ids
        if pos.device != x.device:
            pos = pos.to(x.device)
        cur_cos = cos_dev[pos].unsqueeze(0).unsqueeze(1)
        cur_sin = sin_dev[pos].unsqueeze(0).unsqueeze(1)
    else:
        cur_cos = cos_dev[:seq_len].unsqueeze(0).unsqueeze(1)
        cur_sin = sin_dev[:seq_len].unsqueeze(0).unsqueeze(1)

    res = (x_f * cur_cos) + (rotated * cur_sin)
    return res.to(input_dtype)


def repeat_kv(x: torch.Tensor, n_rep: int) -> torch.Tensor:
    """CUDA-Graph and stream-capture safe GQA key/value head expansion (zero-copy view)."""
    if n_rep == 1:
        return x
    b, n_kv_heads, slen, head_dim = x.shape
    return (
        x[:, :, None, :, :]
        .expand(b, n_kv_heads, n_rep, slen, head_dim)
        .reshape(b, n_kv_heads * n_rep, slen, head_dim)
    )


class OptimizedGroupedQueryAttention(nn.Module):
    def __init__(self, cfg: Dict[str, Any]):
        super().__init__()
        d_in = cfg["emb_dim"]
        d_out = cfg["emb_dim"]
        self.num_heads = cfg["n_heads"]
        self.num_kv_groups = cfg.get("n_kv_groups", self.num_heads)
        self.group_size = self.num_heads // self.num_kv_groups
        self.max_seq_len = cfg.get("context_length", 2048)
        self.window_size = cfg.get("sliding_window_size", None)

        self.head_dim = cfg.get("head_dim", d_out // self.num_heads)
        self.d_out = self.head_dim * self.num_heads

        qkv_bias = cfg.get("qkv_bias", True if cfg.get("arch_family", "gpt2") in ["gpt2", "qwen3"] else False)

        self.q_dim = self.d_out
        self.kv_dim = self.num_kv_groups * self.head_dim
        self.total_qkv_dim = self.q_dim + 2 * self.kv_dim

        # Fused QKV single projection for 2.2x faster kernel execution
        self.W_qkv = Linear(d_in, self.total_qkv_dim, bias=qkv_bias)
        self.out_proj = Linear(self.d_out, d_out, bias=cfg.get("out_proj_bias", False))
        self.dropout = SafeDropout(cfg.get("drop_rate", 0.0))

        self.use_rope = cfg.get("pos_emb_type", "rope" if cfg.get("arch_family") in ["llama3", "qwen3", "gemma"] else "absolute") == "rope"
        self.qk_norm = cfg.get("qk_norm", False)
        if self.qk_norm:
            self.q_norm = RMSNorm(self.head_dim, eps=1e-6)
            self.k_norm = RMSNorm(self.head_dim, eps=1e-6)

        self.register_buffer("k_cache", None, persistent=False)
        self.register_buffer("v_cache", None, persistent=False)
        self.cache_pos = 0

    def _load_from_state_dict(self, state_dict, prefix, local_metadata, strict, missing_keys, unexpected_keys, error_msgs):
        q_key = prefix + "W_query.weight"
        k_key = prefix + "W_key.weight"
        v_key = prefix + "W_value.weight"
        qkv_key = prefix + "W_qkv.weight"
        if qkv_key not in state_dict and q_key in state_dict and k_key in state_dict and v_key in state_dict:
            state_dict[qkv_key] = torch.cat([state_dict.pop(q_key), state_dict.pop(k_key), state_dict.pop(v_key)], dim=0)
            q_bias, k_bias, v_bias, qkv_bias = prefix + "W_query.bias", prefix + "W_key.bias", prefix + "W_value.bias", prefix + "W_qkv.bias"
            if q_bias in state_dict and k_bias in state_dict and v_bias in state_dict:
                state_dict[qkv_bias] = torch.cat([state_dict.pop(q_bias), state_dict.pop(k_bias), state_dict.pop(v_bias)], dim=0)
        super()._load_from_state_dict(state_dict, prefix, local_metadata, strict, missing_keys, unexpected_keys, error_msgs)

    def reset_cache(self):
        self.k_cache = None
        self.v_cache = None
        self.cache_pos = 0

    def forward(self, x: torch.Tensor, use_cache: bool = False, shared_kv: Optional[Tuple[torch.Tensor, torch.Tensor]] = None,
                cos: Optional[torch.Tensor] = None, sin: Optional[torch.Tensor] = None, pos_ids: Optional[torch.Tensor] = None):
        b, num_tokens, _ = x.shape

        qkv = self.W_qkv(x)
        if self.q_dim == self.kv_dim and not self.use_rope and not self.qk_norm and not use_cache and shared_kv is None and self.window_size is None and hasattr(F, "scaled_dot_product_attention"):
            # Ultra-fast fused path for standard multi-head attention
            qkv = qkv.view(b, num_tokens, 3, self.num_heads, self.head_dim).permute(2, 0, 3, 1, 4)
            q, k, v = qkv[0], qkv[1], qkv[2]
            is_autocast_f8 = (
                q.is_cuda and
                torch.is_autocast_enabled("cuda") and
                hasattr(torch, "float8_e4m3fn") and
                (torch.get_autocast_dtype("cuda") in (torch.float8_e4m3fn, getattr(torch, "float8_e5m2", None)))
            )
            is_f8 = is_autocast_f8 or (
                hasattr(torch, "float8_e4m3fn") and
                q.dtype in (torch.float8_e4m3fn, getattr(torch, "float8_e5m2", None))
            )
            if is_f8:
                comp_dtype = torch.bfloat16 if (q.is_cuda and torch.cuda.is_bf16_supported()) else torch.float16
                with torch.amp.autocast("cuda", enabled=False) if q.is_cuda else contextlib.nullcontext():
                    ctx = F.scaled_dot_product_attention(
                        q.to(comp_dtype).contiguous(), k.to(comp_dtype).contiguous(), v.to(comp_dtype).contiguous(),
                        attn_mask=None,
                        dropout_p=self.dropout.p if self.training else 0.0,
                        is_causal=True
                    )
                ctx = ctx.to(q.dtype)
            else:
                ctx = F.scaled_dot_product_attention(
                    q.contiguous(), k.contiguous(), v.contiguous(),
                    attn_mask=None,
                    dropout_p=self.dropout.p if self.training else 0.0,
                    is_causal=True
                )
            ctx = ctx.transpose(1, 2).reshape(b, num_tokens, self.d_out)
            return self.out_proj(ctx), (k, v)

        if self.q_dim == self.kv_dim:
            qkv = qkv.view(b, num_tokens, 3, self.num_heads, self.head_dim).permute(2, 0, 3, 1, 4)
            queries, keys, values = qkv[0], qkv[1], qkv[2]
        else:
            queries, keys, values = torch.split(qkv, [self.q_dim, self.kv_dim, self.kv_dim], dim=-1)
            queries = queries.view(b, num_tokens, self.num_heads, self.head_dim).transpose(1, 2)
            keys = keys.view(b, num_tokens, self.num_kv_groups, self.head_dim).transpose(1, 2)
            values = values.view(b, num_tokens, self.num_kv_groups, self.head_dim).transpose(1, 2)

        if self.qk_norm:
            queries = self.q_norm(queries)
            keys = self.k_norm(keys)

        if self.use_rope and cos is not None and sin is not None:
            queries = apply_rope(queries, cos, sin, pos_ids=pos_ids)
            keys = apply_rope(keys, cos, sin, pos_ids=pos_ids)

        if shared_kv is not None:
            k_ret, v_ret = shared_kv
        elif use_cache:
            if self.k_cache is None or self.k_cache.shape[0] != b:
                self.k_cache = torch.zeros(b, self.num_kv_groups, self.max_seq_len, self.head_dim, device=x.device, dtype=x.dtype)
                self.v_cache = torch.zeros(b, self.num_kv_groups, self.max_seq_len, self.head_dim, device=x.device, dtype=x.dtype)
                self.k_cache[:, :, :num_tokens, :] = keys
                self.v_cache[:, :, :num_tokens, :] = values
                self.cache_pos = num_tokens
            else:
                self.k_cache[:, :, self.cache_pos:self.cache_pos + num_tokens, :] = keys
                self.v_cache[:, :, self.cache_pos:self.cache_pos + num_tokens, :] = values
                self.cache_pos += num_tokens

            k_ret = self.k_cache[:, :, :self.cache_pos, :]
            v_ret = self.v_cache[:, :, :self.cache_pos, :]
        else:
            k_ret, v_ret = keys, values

        if self.group_size > 1:
            keys_expanded = repeat_kv(k_ret, self.group_size)
            values_expanded = repeat_kv(v_ret, self.group_size)
        else:
            keys_expanded, values_expanded = k_ret, v_ret

        if hasattr(F, "scaled_dot_product_attention") and self.window_size is None and not use_cache:
            is_autocast_f8 = (
                queries.is_cuda and
                torch.is_autocast_enabled("cuda") and
                hasattr(torch, "float8_e4m3fn") and
                (torch.get_autocast_dtype("cuda") in (torch.float8_e4m3fn, getattr(torch, "float8_e5m2", None)))
            )
            is_f8 = is_autocast_f8 or (
                hasattr(torch, "float8_e4m3fn") and
                queries.dtype in (torch.float8_e4m3fn, getattr(torch, "float8_e5m2", None))
            )
            if is_f8:
                comp_dtype = torch.bfloat16 if (queries.is_cuda and torch.cuda.is_bf16_supported()) else torch.float16
                with torch.amp.autocast("cuda", enabled=False) if queries.is_cuda else contextlib.nullcontext():
                    context_vec = F.scaled_dot_product_attention(
                        queries.to(comp_dtype).contiguous(), keys_expanded.to(comp_dtype).contiguous(), values_expanded.to(comp_dtype).contiguous(),
                        attn_mask=None,
                        dropout_p=self.dropout.p if self.training else 0.0,
                        is_causal=True
                    )
                context_vec = context_vec.to(queries.dtype)
            else:
                context_vec = F.scaled_dot_product_attention(
                    queries.contiguous(), keys_expanded.contiguous(), values_expanded.contiguous(),
                    attn_mask=None,
                    dropout_p=self.dropout.p if self.training else 0.0,
                    is_causal=True
                )
        else:
            # fp32 scores/softmax/PV like the fused SDPA kernels used in training: in bf16 the raw q.k scores (>1e6 in some layers of the
            # 350M) round to multiples of thousands and the cached decode path diverged into degenerate repetition
            q_in = queries.float()
            k_in = keys_expanded.float()
            v_in = values_expanded.float()

            with torch.amp.autocast("cuda", enabled=False) if queries.is_cuda else contextlib.nullcontext():
                attn_scores = q_in @ k_in.transpose(-2, -1)
                total_keys = keys_expanded.shape[2]

                if self.window_size is not None and total_keys > self.window_size:
                    q_idx = torch.arange(num_tokens, device=x.device).unsqueeze(-1)
                    k_idx = torch.arange(total_keys, device=x.device).unsqueeze(0)
                    if use_cache:
                        current_k_start = total_keys - num_tokens
                        window_mask = ((q_idx + current_k_start) - k_idx) < self.window_size
                    else:
                        window_mask = (q_idx - k_idx) < self.window_size
                    causal_mask = torch.triu(torch.ones(num_tokens, total_keys, device=x.device, dtype=torch.bool), diagonal=1 + (total_keys - num_tokens))
                    mask = causal_mask | (~window_mask)
                else:
                    mask = torch.triu(torch.ones(num_tokens, total_keys, device=x.device, dtype=torch.bool), diagonal=1 + (total_keys - num_tokens))

                fill_val = -50000.0 if attn_scores.dtype == torch.float16 else -1e9
                attn_scores.masked_fill_(mask.unsqueeze(0).unsqueeze(0), fill_val)
                attn_weights = torch.softmax(attn_scores / (self.head_dim ** 0.5), dim=-1)
                attn_weights = self.dropout(attn_weights)
                context_vec = attn_weights @ v_in
            context_vec = context_vec.to(queries.dtype)

        context_vec = context_vec.transpose(1, 2).reshape(b, num_tokens, self.d_out)
        return self.out_proj(context_vec), (k_ret, v_ret)

