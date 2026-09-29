# Copyright (c) Sebastian Raschka under Apache License 2.0 (see LICENSE.txt).
# Core metrics, perplexity calculations, scaling law formulas, and stage completion summaries.

import math
from typing import Any, Dict, Optional, Tuple, Union

import torch
import torch.nn as nn

from gptio.pathutil import STAGE_TRAIN, STAGE_TUNE, STAGE_OPTIMIZE
from gptutils.consoleutils import print, format_elapsed_time


def calculate_perplexity(loss: Optional[float]) -> float:
    """
    Calculates language model perplexity from cross-entropy loss: PPL = exp(loss).
    Safely clamps input to [0.0, 20.0] to prevent floating-point overflow during early random initialization.
    """
    if loss is None or math.isnan(loss):
        return float("nan")
    clamped = max(0.0, min(float(loss), 20.0))
    return math.exp(clamped)


def format_token_count(tokens: Union[int, float]) -> str:
    """Formats token counts into clean, human-readable units (e.g. 15.0B, 300M, 50K)."""
    t = float(tokens)
    if t >= 1e12:
        val = f"{t / 1e12:.1f}".rstrip("0").rstrip(".")
        return f"{val}T"
    elif t >= 1e9:
        val = f"{t / 1e9:.1f}".rstrip("0").rstrip(".")
        return f"{val}B"
    elif t >= 1e6:
        val = f"{t / 1e6:.1f}".rstrip("0").rstrip(".")
        return f"{val}M"
    elif t >= 1e3:
        val = f"{t / 1e3:.1f}".rstrip("0").rstrip(".")
        return f"{val}K"
    return str(int(t))


def format_model_param_count(param_count: int) -> str:
    """Formats exact parameter count into compact notation (e.g. ~150.8M params)."""
    if param_count >= 1e9:
        return f"~{param_count / 1e9:.2f}B params"
    elif param_count >= 1e6:
        return f"~{param_count / 1e6:.1f}M params"
    elif param_count >= 1e3:
        return f"~{param_count / 1e3:.1f}K params"
    return f"{param_count} params"


def count_model_parameters(
    model: Optional[nn.Module] = None,
    config: Optional[Dict[str, Any]] = None
) -> int:
    """
    Extracts total unique parameter count from a model instance (correctly handling tied weights),
    or calculates it analytically from architecture configuration dictionary.
    """
    if model is not None:
        try:
            unique_params = set(model.parameters())
            return sum(p.numel() for p in unique_params)
        except Exception:
            pass

    if config is not None:
        emb_dim = int(config.get("emb_dim", 768))
        n_layers = int(config.get("n_layers", 12))
        vocab_size = int(config.get("vocab_size", 50257))
        context_length = int(config.get("context_length", 1024))
        qkv_bias = bool(config.get("qkv_bias", False))
        tie_embeddings = bool(config.get("tie_embeddings", config.get("tie_word_embeddings", True)))

        tok_emb_params = vocab_size * emb_dim
        pos_emb_params = context_length * emb_dim

        # Per transformer block:
        # Attention: W_qkv (3 * emb_dim * emb_dim) + (3 * emb_dim if bias else 0)
        #            Out proj (emb_dim * emb_dim) + (emb_dim if bias else 0)
        # MLP: Linear 1 (emb_dim * 4 * emb_dim) + 4 * emb_dim (bias)
        #      Linear 2 (4 * emb_dim * emb_dim) + emb_dim (bias)
        # LayerNorms: 2 norms * 2 * emb_dim (weight + bias)
        attn_params = 4 * (emb_dim ** 2) + (4 * emb_dim if qkv_bias else 0)
        mlp_params = 8 * (emb_dim ** 2) + 5 * emb_dim
        norm_params = 4 * emb_dim
        block_params = attn_params + mlp_params + norm_params
        total_blocks = n_layers * block_params

        final_norm_params = 2 * emb_dim
        head_params = 0 if tie_embeddings else (vocab_size * emb_dim)

        return tok_emb_params + pos_emb_params + total_blocks + final_norm_params + head_params

    return 0


def estimate_ideal_metrics(param_count: int, stage: str = STAGE_TRAIN) -> Dict[str, Any]:
    """
    Computes theoretical scaling-law ideal targets for arbitrary model sizes:
    - Pretraining: Chinchilla/Kaplan power-law formulation for 32k-50k vocab.
    - Fine-Tuning: Empirical instruction-following SFT target ranges with prompt masking.
    - Optimization: Preference binary loss and margin targets.
    """
    p = max(10_000_000, float(param_count))
    p_b = p / 1e9  # parameters in billions

    if stage == STAGE_TRAIN:
        val_mid = 1.05 + 1.50 * (p_b ** -0.23)
        train_mid = val_mid - 0.05
        val_range = (max(0.1, val_mid - 0.075), val_mid + 0.075)
        train_range = (max(0.1, train_mid - 0.075), train_mid + 0.075)
        ppl_range = (math.exp(val_range[0]), math.exp(val_range[1]))
        tok_min = max(1e9, 20.0 * p)
        tok_max = max(2e9, 130.0 * p)
    elif stage == STAGE_TUNE:
        val_mid = 0.55 + 1.05 * (p_b ** -0.19)
        train_mid = val_mid - 0.30
        val_range = (max(0.1, val_mid - 0.15), val_mid + 0.15)
        train_range = (max(0.1, train_mid - 0.15), train_mid + 0.15)
        ppl_range = (math.exp(val_range[0]), math.exp(val_range[1]))
        tok_min = max(200e6, 2.0 * p)
        tok_max = max(1e9, 15.0 * p)
    else:  # STAGE_OPTIMIZE
        train_range = (0.40, 0.60)
        val_range = (0.45, 0.65)
        ppl_range = (0.0, 0.0)
        tok_min = max(10e6, 0.5 * p)
        tok_max = max(100e6, 5.0 * p)

    return {
        "train_loss_range": train_range,
        "val_loss_range": val_range,
        "ppl_range": ppl_range,
        "tokens_range": (tok_min, tok_max),
        "tokens_str": f"{format_token_count(tok_min)}-{format_token_count(tok_max)}",
        "train_loss_str": f"{train_range[0]:.2f}-{train_range[1]:.2f}",
        "val_loss_str": f"{val_range[0]:.2f}-{val_range[1]:.2f}",
        "ppl_str": f"{ppl_range[0]:.1f}-{ppl_range[1]:.1f}" if ppl_range[0] > 0 else "N/A",
    }


def assess_loss_gap(
    train_loss: Optional[float],
    val_loss: Optional[float],
    stage: str = STAGE_TRAIN,
    val_seq_loss: Optional[float] = None
) -> Tuple[Optional[float], str]:
    """
    Computes Val - Train loss difference and assesses convergence quality:
    Returns (gap, assessment_string), e.g. (0.043, "+0.043 (OK!)") or (0.420, "+0.420 (OVERFITTING!)").
    """
    if train_loss is None or val_loss is None:
        return None, ""

    gap = val_loss - train_loss

    if stage == STAGE_TRAIN:
        if val_loss > 4.0:
            status = f"{gap:+.3f} (UNDERFITTING!)"
        elif gap > 0.30:
            status = f"{gap:+.3f} (OVERFITTING!)"
        elif gap < -0.10:
            status = f"{gap:+.3f} (ANOMALY / Val < Train)"
        else:
            status = f"{gap:+.3f} (OK!)"
    elif stage == STAGE_TUNE:
        eval_loss = val_seq_loss if val_seq_loss is not None else val_loss
        underfit_threshold = 2.00 if val_seq_loss is not None else 2.80
        if eval_loss > underfit_threshold:
            status = f"{gap:+.3f} (UNDERFITTING!)"
        elif gap > 0.45:
            status = f"{gap:+.3f} (OVERFITTING!)"
        elif gap < -0.10:
            status = f"{gap:+.3f} (ANOMALY / Val < Train)"
        else:
            status = f"{gap:+.3f} (OK!)"
    else:  # STAGE_OPTIMIZE
        if gap > 0.25:
            status = f"{gap:+.3f} (OVERFITTING!)"
        else:
            status = f"{gap:+.3f} (OK!)"

    return gap, status


def print_stage_completion_summary(
    stage: str,
    total_elapsed_time: float,
    total_tokens: int,
    train_loss: Optional[float],
    val_loss: Optional[float],
    model_name: str,
    param_count: Optional[int] = None,
    train_margin: Optional[float] = None,
    val_margin: Optional[float] = None,
    val_seq_loss: Optional[float] = None,
) -> None:
    """
    Standardized, beautifully formatted completion banner displaying:
    - Elapsed duration
    - Tokens seen alongside scaling-law ideal target
    - Final losses alongside ideal target intervals
    - Val - Train loss gap with automatic diagnosis (OK / OVERFITTING / UNDERFITTING)
    - Perplexity score alongside ideal target interval
    - Model metadata and parameter count
    """
    time_str = format_elapsed_time(total_elapsed_time)

    banner_titles = {
        STAGE_TRAIN: "TRAINING COMPLETED",
        STAGE_TUNE: "FINE-TUNING COMPLETED",
        STAGE_OPTIMIZE: "DPO OPTIMIZATION COMPLETED",
    }
    title = banner_titles.get(stage, "TRAINING COMPLETED")

    ideals = estimate_ideal_metrics(param_count, stage) if (param_count and param_count > 0) else None
    _, gap_status = assess_loss_gap(train_loss, val_loss, stage, val_seq_loss=val_seq_loss)

    print(f"\n{'='*60}")
    print(f"               {title}")
    print(f"{'='*60}")
    print(f"  Total Elapsed Time : {time_str}")

    if ideals is not None:
        print(f"  Total Tokens Seen  : {total_tokens:,} (ideal: {ideals['tokens_str']})")
    else:
        print(f"  Total Tokens Seen  : {total_tokens:,}")

    if train_loss is not None and val_loss is not None:
        if val_seq_loss is not None:
            if ideals is not None and stage != STAGE_OPTIMIZE:
                print(f"  Final Losses       : Train {train_loss:.3f} | Val {val_loss:.3f} (Seq: {val_seq_loss:.3f}, ideal: {ideals['val_loss_str']})")
            else:
                print(f"  Final Losses       : Train {train_loss:.3f} | Val {val_loss:.3f} (Seq: {val_seq_loss:.3f})")
        else:
            if ideals is not None and stage != STAGE_OPTIMIZE:
                print(f"  Final Losses       : Train {train_loss:.3f} (ideal: {ideals['train_loss_str']}) | Val {val_loss:.3f} (ideal: {ideals['val_loss_str']})")
            else:
                print(f"  Final Losses       : Train {train_loss:.3f} | Val {val_loss:.3f}")

        if gap_status:
            print(f"  Val - Train Gap    : {gap_status}")

    if stage != STAGE_OPTIMIZE and val_loss is not None:
        ppl = calculate_perplexity(val_loss)
        if val_seq_loss is not None:
            seq_ppl = calculate_perplexity(val_seq_loss)
            if ideals is not None:
                print(f"  Perplexity         : Resp {ppl:.2f} | Seq {seq_ppl:.2f} (ideal: {ideals['ppl_str']})")
            else:
                print(f"  Perplexity         : Resp {ppl:.2f} | Seq {seq_ppl:.2f}")
        else:
            if ideals is not None:
                print(f"  Perplexity         : {ppl:.2f} (ideal: {ideals['ppl_str']})")
            else:
                print(f"  Perplexity         : {ppl:.2f}")

    if stage == STAGE_OPTIMIZE and train_margin is not None and val_margin is not None:
        print(f"  Final Margins      : Train {train_margin:+.3f} | Val {val_margin:+.3f}")

    if param_count and param_count > 0:
        param_str = format_model_param_count(param_count)
        print(f"  Model              : {model_name} ({param_str})")
    else:
        print(f"  Model              : {model_name}")

    print(f"{'='*60}\n")
