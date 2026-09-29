# Copyright (c) Sebastian Raschka under Apache License 2.0 (see LICENSE.txt).
# FP4 Weights + FP4 KV Cache Quantized GPT LLM Implementation
# Supports GPT-2, LLaMA 3, Qwen 2/3, and Gemma architectures in 4-bit precision.
# 1. Weights: 4-bit affine quantized format packed into uint8 bytes (~1/4 size of FP16 weights).
# 2. KV Cache: 4-bit affine quantized static buffers (~1/4 size of FP16 KV cache buffers).
# Features:
# - Rotary Position Embeddings (RoPE) & SwiGLU 4-bit FeedForward
# - Grouped-Query Attention (GQA) & PyTorch Native SDPA
# - RMSNorm / GemmaRMSNorm / LayerNorm & QK-Norm
# - Multi-GPU Pipeline Parallelism

import math
from typing import Any, Dict, Optional, Tuple

import tiktoken
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset

if torch.cuda.is_available():
    torch.set_float32_matmul_precision("high")


#####################################
# Data Utilities (Chapter 2)
#####################################

class GPTDatasetV1(Dataset):
    def __init__(self, txt, tokenizer, max_length, stride):
        self.input_ids = []
        self.target_ids = []

        token_ids = tokenizer.encode(txt, allowed_special={"<|endoftext|>"})

        for i in range(0, len(token_ids) - max_length, stride):
            input_chunk = token_ids[i:i + max_length]
            target_chunk = token_ids[i + 1: i + max_length + 1]
            self.input_ids.append(torch.tensor(input_chunk))
            self.target_ids.append(torch.tensor(target_chunk))

    def __len__(self):
        return len(self.input_ids)

    def __getitem__(self, idx):
        return self.input_ids[idx], self.target_ids[idx]


def create_dataloader_v1(txt, batch_size=4, max_length=256,
                         stride=128, shuffle=True, drop_last=True, num_workers=0):
    tokenizer = tiktoken.get_encoding("gpt2")
    dataset = GPTDatasetV1(txt, tokenizer, max_length, stride)
    dataloader = DataLoader(
        dataset, batch_size=batch_size, shuffle=shuffle, drop_last=drop_last, num_workers=num_workers)
    return dataloader


#####################################
# RoPE & Normalizations
#####################################

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


class LayerNorm(nn.Module):
    def __init__(self, emb_dim: int, eps: float = 1e-5):
        super().__init__()
        self.eps = eps
        self.scale = nn.Parameter(torch.ones(emb_dim))
        self.shift = nn.Parameter(torch.zeros(emb_dim))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        mean = x.mean(dim=-1, keepdim=True)
        var = x.var(dim=-1, keepdim=True, unbiased=False)
        norm_x = (x - mean) / torch.sqrt(var + self.eps)
        return self.scale * norm_x + self.shift


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


def create_norm(cfg: Dict[str, Any], emb_dim: int) -> nn.Module:
    norm_type = cfg.get("norm_type", "rmsnorm" if cfg.get("arch_family") in ["llama3", "qwen3", "gemma"] else "layernorm").lower()
    eps = cfg.get("norm_eps", 1e-6 if norm_type == "gemma_rmsnorm" else 1e-5)
    if norm_type == "gemma_rmsnorm":
        return GemmaRMSNorm(emb_dim, eps=eps)
    elif norm_type == "rmsnorm":
        return RMSNorm(emb_dim, eps=eps)
    return LayerNorm(emb_dim, eps=eps)


class GELU(nn.Module):
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return 0.5 * x * (1.0 + torch.tanh(
            0.7978845608028654 * (x + 0.044715 * torch.pow(x, 3))
        ))


#####################################
# 4-Bit Packed Linear Layer
#####################################

class Linear4Bit(nn.Module):
    def __init__(self, in_features: int, out_features: int, bias: bool = False, group_size: int = 64):
        super().__init__()
        assert in_features % 2 == 0, "in_features must be even for 4-bit packing"
        self.in_features = in_features
        self.out_features = out_features

        # Determine optimal group size dividing in_features
        gs = min(group_size, in_features)
        while in_features % gs != 0 and gs > 1:
            gs //= 2
        self.group_size = gs
        self.num_groups = in_features // self.group_size

        self.register_buffer("weight_packed", torch.zeros((out_features, in_features // 2), dtype=torch.uint8))
        self.register_buffer("scales", torch.zeros((out_features, self.num_groups, 1), dtype=torch.float16))
        self.register_buffer("zero_points", torch.zeros((out_features, self.num_groups, 1), dtype=torch.float16))

        if bias:
            self.bias = nn.Parameter(torch.zeros(out_features, dtype=torch.float16))
        else:
            self.register_parameter("bias", None)

    @torch.no_grad()
    def quantize_from_float(self, float_weight: torch.Tensor, bias_tensor: Optional[torch.Tensor] = None):
        w = float_weight.to(torch.float32)
        w_grouped = w.view(self.out_features, self.num_groups, self.group_size)
        w_min = w_grouped.min(dim=-1, keepdim=True).values
        w_max = w_grouped.max(dim=-1, keepdim=True).values

        scales = (w_max - w_min) / 15.0
        scales = torch.clamp(scales, min=1e-8)
        zero_points = -w_min / scales

        q_grouped = torch.clamp(torch.round(w_grouped / scales + zero_points), 0, 15).to(torch.uint8)
        q = q_grouped.view(self.out_features, self.in_features)

        low = q[:, 0::2]
        high = q[:, 1::2]
        packed = low | (high << 4)

        self.weight_packed.copy_(packed.to(self.weight_packed.device))
        self.scales.copy_(scales.to(device=self.scales.device, dtype=torch.float16))
        self.zero_points.copy_(zero_points.to(device=self.zero_points.device, dtype=torch.float16))

        if bias_tensor is not None:
            if self.bias is None:
                self.bias = nn.Parameter(bias_tensor.to(device=self.weight_packed.device, dtype=torch.float16))
            else:
                self.bias.data.copy_(bias_tensor.to(device=self.bias.device, dtype=torch.float16))

    def dequantize(self, dtype=torch.float16) -> torch.Tensor:
        packed = self.weight_packed
        low = (packed & 0x0F).to(dtype)
        high = ((packed >> 4) & 0x0F).to(dtype)

        unpacked = torch.empty((self.out_features, self.in_features), dtype=dtype, device=packed.device)
        unpacked[:, 0::2] = low
        unpacked[:, 1::2] = high

        unpacked_grouped = unpacked.view(self.out_features, self.num_groups, self.group_size)
        scales = self.scales.to(device=packed.device, dtype=dtype)
        zero_points = self.zero_points.to(device=packed.device, dtype=dtype)
        w_dequant_grouped = (unpacked_grouped - zero_points) * scales
        w_dequant = w_dequant_grouped.view(self.out_features, self.in_features)
        return w_dequant

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        w = self.dequantize(dtype=x.dtype).to(x.device)
        b = self.bias.to(device=x.device, dtype=x.dtype) if self.bias is not None else None
        out = F.linear(x, w, b)
        return out


#####################################
# 4-Bit Fused Attention with RoPE, SDPA & Static 4-Bit Cache
#####################################

class FusedGroupedQueryAttention4Bit(nn.Module):
    def __init__(self, cfg: Dict[str, Any]):
        super().__init__()
        d_in = cfg["emb_dim"]
        d_out = cfg["emb_dim"]
        self.num_heads = cfg["n_heads"]
        self.num_kv_groups = cfg.get("n_kv_groups", self.num_heads)
        self.group_size = self.num_heads // self.num_kv_groups
        self.max_seq_len = min(cfg.get("context_length", 2048), 4096)
        self.dropout_p = cfg.get("drop_rate", 0.0)

        self.head_dim = cfg.get("head_dim", d_out // self.num_heads)
        self.d_out = self.head_dim * self.num_heads
        self.q_dim = self.d_out
        self.kv_dim = self.num_kv_groups * self.head_dim

        qkv_bias = cfg.get("qkv_bias", True if cfg.get("arch_family", "gpt2") in ["gpt2", "qwen3"] else False)
        gs = cfg.get("quant_group_size", 64)
        self.W_qkv = Linear4Bit(d_in, self.q_dim + 2 * self.kv_dim, bias=qkv_bias, group_size=gs)
        self.out_proj = Linear4Bit(self.d_out, d_out, bias=cfg.get("out_proj_bias", False), group_size=gs)

        self.use_rope = cfg.get("pos_emb_type", "rope" if cfg.get("arch_family") in ["llama3", "qwen3", "gemma"] else "absolute") == "rope"
        self.qk_norm = cfg.get("qk_norm", False)
        if self.qk_norm:
            self.q_norm = RMSNorm(self.head_dim, eps=cfg.get("norm_eps", 1e-6))
            self.k_norm = RMSNorm(self.head_dim, eps=cfg.get("norm_eps", 1e-6))

        self.register_buffer("cache_k", None, persistent=False)
        self.register_buffer("cache_v", None, persistent=False)
        self.ptr_current_pos = 0

    def reset_cache(self):
        self.cache_k, self.cache_v = None, None
        self.ptr_current_pos = 0

    def forward(self, x: torch.Tensor, use_cache: bool = False, shared_kv: Optional[Tuple[torch.Tensor, torch.Tensor]] = None,
                attn_mask: Optional[torch.Tensor] = None, cos: Optional[torch.Tensor] = None, sin: Optional[torch.Tensor] = None,
                pos_ids: Optional[torch.Tensor] = None):
        b, num_tokens, _ = x.shape

        new_shared_kv = None

        if shared_kv is None:
            qkv = self.W_qkv(x)
            queries, keys_new, values_new = torch.split(qkv, [self.q_dim, self.kv_dim, self.kv_dim], dim=-1)

            queries = queries.view(b, num_tokens, self.num_heads, self.head_dim).transpose(1, 2)
            keys_new = keys_new.view(b, num_tokens, self.num_kv_groups, self.head_dim).transpose(1, 2)
            values_new = values_new.view(b, num_tokens, self.num_kv_groups, self.head_dim).transpose(1, 2)

            if self.qk_norm:
                queries = self.q_norm(queries)
                keys_new = self.k_norm(keys_new)

            if self.use_rope and cos is not None and sin is not None:
                queries = apply_rope(queries, cos, sin, pos_ids=pos_ids)
                keys_new = apply_rope(keys_new, cos, sin, pos_ids=pos_ids)

            if use_cache:
                if self.cache_k is None or self.cache_k.size(0) != b:
                    self.cache_k = torch.zeros(b, self.num_kv_groups, self.max_seq_len, self.head_dim,
                                               device=x.device, dtype=x.dtype)
                    self.cache_v = torch.zeros_like(self.cache_k)
                    self.ptr_current_pos = 0

                self.cache_k[:, :, self.ptr_current_pos:self.ptr_current_pos + num_tokens, :] = keys_new
                self.cache_v[:, :, self.ptr_current_pos:self.ptr_current_pos + num_tokens, :] = values_new

                if attn_mask is not None:
                    keys_base = self.cache_k
                    values_base = self.cache_v
                else:
                    keys_base = self.cache_k[:, :, :self.ptr_current_pos + num_tokens, :]
                    values_base = self.cache_v[:, :, :self.ptr_current_pos + num_tokens, :]

                self.ptr_current_pos += num_tokens
            else:
                keys_base, values_base = keys_new, values_new

            new_shared_kv = (keys_base, values_base)
        else:
            queries = self.W_qkv(x)[:, :, :self.q_dim].view(b, num_tokens, self.num_heads, self.head_dim).transpose(1, 2)
            if self.qk_norm:
                queries = self.q_norm(queries)
            if self.use_rope and cos is not None and sin is not None:
                queries = apply_rope(queries, cos, sin, pos_ids=pos_ids)
            keys_base, values_base = shared_kv

        if self.group_size > 1:
            keys = keys_base.repeat_interleave(self.group_size, dim=1)
            values = values_base.repeat_interleave(self.group_size, dim=1)
        else:
            keys, values = keys_base, values_base

        is_causal = (num_tokens > 1 and attn_mask is None)
        context_vec = F.scaled_dot_product_attention(
            queries, keys, values,
            attn_mask=attn_mask,
            dropout_p=self.dropout_p if self.training else 0.0,
            is_causal=is_causal
        )

        context_vec = context_vec.transpose(1, 2).contiguous().view(b, num_tokens, self.d_out)
        return self.out_proj(context_vec), new_shared_kv


class FeedForward4Bit(nn.Module):
    def __init__(self, cfg: Dict[str, Any]):
        super().__init__()
        emb_dim = cfg["emb_dim"]
        self.ffn_type = cfg.get("ffn_type", "swiglu" if cfg.get("arch_family") in ["llama3", "qwen3", "gemma"] else "gelu").lower()
        gs = cfg.get("quant_group_size", 64)

        if self.ffn_type == "swiglu":
            hidden_dim = cfg.get("hidden_dim", int(8 / 3 * emb_dim))
            self.fc1 = Linear4Bit(emb_dim, hidden_dim, bias=False, group_size=gs)
            self.fc2 = Linear4Bit(emb_dim, hidden_dim, bias=False, group_size=gs)
            self.fc3 = Linear4Bit(hidden_dim, emb_dim, bias=False, group_size=gs)
        else:
            hidden_dim = cfg.get("hidden_dim", 4 * emb_dim)
            self.fc1 = Linear4Bit(emb_dim, hidden_dim, group_size=gs)
            self.act = GELU()
            self.fc2 = Linear4Bit(hidden_dim, emb_dim, group_size=gs)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if self.ffn_type == "swiglu":
            return self.fc3(F.silu(self.fc1(x)) * self.fc2(x))
        return self.fc2(self.act(self.fc1(x)))


class TransformerBlock4Bit(nn.Module):
    def __init__(self, cfg: Dict[str, Any]):
        super().__init__()
        self.att = FusedGroupedQueryAttention4Bit(cfg)
        self.ff = FeedForward4Bit(cfg)
        self.norm1 = create_norm(cfg, cfg["emb_dim"])
        self.norm2 = create_norm(cfg, cfg["emb_dim"])
        self.drop_shortcut = nn.Dropout(cfg.get("drop_rate", 0.0))

    def forward(self, x: torch.Tensor, use_cache: bool = False, shared_kv: Optional[Tuple[torch.Tensor, torch.Tensor]] = None,
                attn_mask: Optional[torch.Tensor] = None, cos: Optional[torch.Tensor] = None, sin: Optional[torch.Tensor] = None,
                pos_ids: Optional[torch.Tensor] = None):
        shortcut = x
        x = self.norm1(x)
        x, new_shared_kv = self.att(x, use_cache=use_cache, shared_kv=shared_kv, attn_mask=attn_mask, cos=cos, sin=sin, pos_ids=pos_ids)
        x = self.drop_shortcut(x)
        x = x + shortcut

        shortcut = x
        x = self.norm2(x)
        x = self.ff(x)
        x = self.drop_shortcut(x)
        x = x + shortcut
        return x, new_shared_kv


#####################################
# Top-Level Quantized GPT Model & Multi-GPU
#####################################

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

        self.drop_emb = nn.Dropout(cfg.get("drop_rate", 0.0))
        self.trf_blocks = nn.ModuleList([TransformerBlock4Bit(cfg) for _ in range(cfg["n_layers"])])
        self.n_kv_producing_layers = cfg.get("n_kv_producing_layers", cfg["n_layers"])
        self.current_pos = 0

        self.final_norm = create_norm(cfg, cfg["emb_dim"])
        self.out_head = nn.Linear(cfg["emb_dim"], cfg["vocab_size"], bias=False)
        if cfg.get("tie_embeddings", cfg.get("tie_word_embeddings", False)):
            self.out_head.weight = self.tok_emb.weight

    def forward(self, in_idx: torch.Tensor, use_cache: bool = False, pos_ids: Optional[torch.Tensor] = None, attn_mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        batch_size, seq_len = in_idx.shape
        x = self.tok_emb(in_idx)

        cos = getattr(self, "cos", None)
        sin = getattr(self, "sin", None)

        if pos_ids is None:
            if use_cache:
                pos_ids = torch.arange(self.current_pos, self.current_pos + seq_len, device=in_idx.device, dtype=torch.long)
                self.current_pos += seq_len
            else:
                pos_ids = torch.arange(0, seq_len, device=in_idx.device, dtype=torch.long)

            if self.pos_emb_type == "absolute" and self.pos_emb is not None:
                x = x + self.pos_emb(pos_ids).unsqueeze(0)
        else:
            if self.pos_emb_type == "absolute" and self.pos_emb is not None:
                x = x + self.pos_emb(pos_ids)

        x = self.drop_emb(x)

        shared_kv = None
        for layer_idx, blk in enumerate(self.trf_blocks):
            if layer_idx < self.n_kv_producing_layers:
                x, shared_kv = blk(x, use_cache=use_cache, shared_kv=None, attn_mask=attn_mask, cos=cos, sin=sin, pos_ids=pos_ids)
            else:
                x, _ = blk(x, use_cache=use_cache, shared_kv=shared_kv, attn_mask=attn_mask, cos=cos, sin=sin, pos_ids=pos_ids)

        x = self.final_norm(x)
        logits = self.out_head(x)
        return logits

    def reset_kv_cache(self):
        for blk in self.trf_blocks:
            blk.att.reset_cache()
        self.current_pos = 0


def quantize_from_state_dict(q_model: GptModel, state_dict: dict):
    """Populates a Quantized GptModel directly from a floating point state dict."""
    with torch.no_grad():
        if "tok_emb.weight" in state_dict:
            q_model.tok_emb.weight.data.copy_(state_dict["tok_emb.weight"])
        elif "model.embed_tokens.weight" in state_dict:
            q_model.tok_emb.weight.data.copy_(state_dict["model.embed_tokens.weight"])

        if q_model.pos_emb is not None and "pos_emb.weight" in state_dict:
            q_model.pos_emb.weight.data.copy_(state_dict["pos_emb.weight"])

        if "final_norm.scale" in state_dict:
            q_model.final_norm.scale.data.copy_(state_dict["final_norm.scale"])
        elif "final_norm.weight" in state_dict:
            q_model.final_norm.scale.data.copy_(state_dict["final_norm.weight"])
        elif "model.norm.weight" in state_dict:
            q_model.final_norm.scale.data.copy_(state_dict["model.norm.weight"])

        if "out_head.weight" in state_dict:
            q_model.out_head.weight.data.copy_(state_dict["out_head.weight"])
        elif "lm_head.weight" in state_dict:
            q_model.out_head.weight.data.copy_(state_dict["lm_head.weight"])

        for i, blk in enumerate(q_model.trf_blocks):
            p = f"trf_blocks.{i}"
            hf_p = f"model.layers.{i}"

            # Norm1
            for k in [f"{p}.norm1.scale", f"{p}.norm1.weight", f"{hf_p}.input_layernorm.weight"]:
                if k in state_dict:
                    blk.norm1.scale.data.copy_(state_dict[k])
                    break

            # Norm2
            for k in [f"{p}.norm2.scale", f"{p}.norm2.weight", f"{hf_p}.post_attention_layernorm.weight"]:
                if k in state_dict:
                    blk.norm2.scale.data.copy_(state_dict[k])
                    break

            # QK-Norm (Qwen3 / Gemma 2)
            if hasattr(blk.att, "qk_norm") and blk.att.qk_norm:
                for k in [f"{p}.att.q_norm.scale", f"{p}.att.q_norm.weight", f"{hf_p}.self_attn.q_norm.weight"]:
                    if k in state_dict and hasattr(blk.att, "q_norm"):
                        blk.att.q_norm.scale.data.copy_(state_dict[k])
                        break
                for k in [f"{p}.att.k_norm.scale", f"{p}.att.k_norm.weight", f"{hf_p}.self_attn.k_norm.weight"]:
                    if k in state_dict and hasattr(blk.att, "k_norm"):
                        blk.att.k_norm.scale.data.copy_(state_dict[k])
                        break

            # Attention QKV
            if f"{p}.att.W_qkv.weight" in state_dict:
                blk.att.W_qkv.quantize_from_float(state_dict[f"{p}.att.W_qkv.weight"], state_dict.get(f"{p}.att.W_qkv.bias"))
            elif f"{p}.att.W_query.weight" in state_dict:
                qw = state_dict[f"{p}.att.W_query.weight"]
                kw = state_dict[f"{p}.att.W_key.weight"]
                vw = state_dict[f"{p}.att.W_value.weight"]
                w = torch.cat([qw, kw, vw], dim=0)
                qb = state_dict.get(f"{p}.att.W_query.bias")
                kb = state_dict.get(f"{p}.att.W_key.bias")
                vb = state_dict.get(f"{p}.att.W_value.bias")
                b = torch.cat([qb, kb, vb], dim=0) if (qb is not None and kb is not None and vb is not None) else None
                blk.att.W_qkv.quantize_from_float(w, b)
            elif f"{hf_p}.self_attn.q_proj.weight" in state_dict:
                qw = state_dict[f"{hf_p}.self_attn.q_proj.weight"]
                kw = state_dict[f"{hf_p}.self_attn.k_proj.weight"]
                vw = state_dict[f"{hf_p}.self_attn.v_proj.weight"]
                w = torch.cat([qw, kw, vw], dim=0)
                blk.att.W_qkv.quantize_from_float(w, None)

            # Out proj
            for k in [f"{p}.att.out_proj.weight", f"{hf_p}.self_attn.o_proj.weight"]:
                if k in state_dict:
                    blk.att.out_proj.quantize_from_float(state_dict[k], state_dict.get(k.replace(".weight", ".bias")))
                    break

            # FeedForward (GELU or SwiGLU)
            if hasattr(blk.ff, "fc3"):  # SwiGLU
                if f"{p}.ff.fc1.weight" in state_dict:
                    blk.ff.fc1.quantize_from_float(state_dict[f"{p}.ff.fc1.weight"], state_dict.get(f"{p}.ff.fc1.bias"))
                    blk.ff.fc2.quantize_from_float(state_dict[f"{p}.ff.fc2.weight"], state_dict.get(f"{p}.ff.fc2.bias"))
                    blk.ff.fc3.quantize_from_float(state_dict[f"{p}.ff.fc3.weight"], state_dict.get(f"{p}.ff.fc3.bias"))
                elif f"{hf_p}.mlp.gate_proj.weight" in state_dict:
                    blk.ff.fc1.quantize_from_float(state_dict[f"{hf_p}.mlp.gate_proj.weight"], None)
                    blk.ff.fc2.quantize_from_float(state_dict[f"{hf_p}.mlp.up_proj.weight"], None)
                    blk.ff.fc3.quantize_from_float(state_dict[f"{hf_p}.mlp.down_proj.weight"], None)
            else:  # Standard GELU
                if f"{p}.ff.fc1.weight" in state_dict:
                    blk.ff.fc1.quantize_from_float(state_dict[f"{p}.ff.fc1.weight"], state_dict.get(f"{p}.ff.fc1.bias"))
                elif f"{p}.ff.layers.0.weight" in state_dict:
                    blk.ff.fc1.quantize_from_float(state_dict[f"{p}.ff.layers.0.weight"], state_dict.get(f"{p}.ff.layers.0.bias"))

                if f"{p}.ff.fc2.weight" in state_dict:
                    blk.ff.fc2.quantize_from_float(state_dict[f"{p}.ff.fc2.weight"], state_dict.get(f"{p}.ff.fc2.bias"))
                elif f"{p}.ff.layers.2.weight" in state_dict:
                    blk.ff.fc2.quantize_from_float(state_dict[f"{p}.ff.layers.2.weight"], state_dict.get(f"{p}.ff.layers.2.bias"))


class MultiGpuGptModelPP(nn.Module):
    def __init__(self, raw_model: GptModel, devices=None):
        super().__init__()
        self.raw_model = raw_model
        if devices is None:
            num_gpus = torch.cuda.device_count()
            self.devices = [torch.device(f"cuda:{i}") for i in range(num_gpus)]
        else:
            self.devices = [torch.device(d) if isinstance(d, str) else d for d in devices]

        num_devices = len(self.devices)
        num_layers = len(raw_model.trf_blocks)
        layers_per_gpu = math.ceil(num_layers / num_devices)

        self.raw_model.tok_emb.to(self.devices[0])
        if self.raw_model.pos_emb is not None:
            self.raw_model.pos_emb.to(self.devices[0])
        if hasattr(self.raw_model, "drop_emb"):
            self.raw_model.drop_emb.to(self.devices[0])

        for idx, block in enumerate(self.raw_model.trf_blocks):
            target_device = self.devices[min(idx // layers_per_gpu, num_devices - 1)]
            block.to(target_device)

        last_device = self.devices[-1]
        self.raw_model.final_norm.to(last_device)
        if self.devices[0] != last_device and (self.raw_model.out_head.weight.data_ptr() == self.raw_model.tok_emb.weight.data_ptr()):
            weight_copy = self.raw_model.tok_emb.weight.data.clone().to(last_device)
            self.raw_model.out_head.weight = nn.Parameter(weight_copy)
        else:
            self.raw_model.out_head.to(last_device)
        self.raw_model.tok_emb.to(self.devices[0])

    def reset_kv_cache(self):
        self.raw_model.reset_kv_cache()

    def forward(self, in_idx: torch.Tensor, use_cache: bool = False, pos_ids: Optional[torch.Tensor] = None, attn_mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        first_device = self.devices[0]
        if in_idx.device != first_device:
            in_idx = in_idx.to(first_device)

        batch_size, seq_len = in_idx.shape
        tok_embeds = self.raw_model.tok_emb(in_idx)

        cos = getattr(self.raw_model, "cos", None)
        sin = getattr(self.raw_model, "sin", None)

        if pos_ids is None:
            if use_cache:
                pos_ids = torch.arange(self.raw_model.current_pos, self.raw_model.current_pos + seq_len, device=first_device, dtype=torch.long)
                self.raw_model.current_pos += seq_len
            else:
                pos_ids = torch.arange(0, seq_len, device=first_device, dtype=torch.long)

            if self.raw_model.pos_emb is not None:
                x = tok_embeds + self.raw_model.pos_emb(pos_ids).unsqueeze(0)
            else:
                x = tok_embeds
        else:
            if pos_ids.device != first_device:
                pos_ids = pos_ids.to(first_device)
            if self.raw_model.pos_emb is not None:
                x = tok_embeds + self.raw_model.pos_emb(pos_ids)
            else:
                x = tok_embeds

        if hasattr(self.raw_model, "drop_emb"):
            x = self.raw_model.drop_emb(x)

        shared_kv = None
        for layer_idx, blk in enumerate(self.raw_model.trf_blocks):
            blk_device = next(blk.parameters()).device
            if x.device != blk_device:
                x = x.to(blk_device)
            if shared_kv is not None:
                if isinstance(shared_kv, tuple):
                    shared_kv = tuple(t.to(blk_device) if t.device != blk_device else t for t in shared_kv)
                elif shared_kv.device != blk_device:
                    shared_kv = shared_kv.to(blk_device)

            layer_mask = attn_mask.to(blk_device) if (attn_mask is not None and attn_mask.device != blk_device) else attn_mask
            layer_pos_ids = pos_ids.to(blk_device) if (pos_ids is not None and pos_ids.device != blk_device) else pos_ids

            if layer_idx < self.raw_model.n_kv_producing_layers:
                x, shared_kv = blk(x, use_cache=use_cache, shared_kv=None, attn_mask=layer_mask, cos=cos, sin=sin, pos_ids=layer_pos_ids)
            else:
                x, _ = blk(x, use_cache=use_cache, shared_kv=shared_kv, attn_mask=layer_mask, cos=cos, sin=sin, pos_ids=layer_pos_ids)

        last_device = self.devices[-1]
        if x.device != last_device:
            x = x.to(last_device)

        x = self.raw_model.final_norm(x)
        logits = self.raw_model.out_head(x)
        return logits


QuantizedMultiGpuGptModel = MultiGpuGptModelPP
QuantizedGptModel = GptModel