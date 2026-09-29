import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import torch
from gptmodel.GptModel import GptModel


def calculate_parameters_from_config(config: Dict[str, Any]) -> Tuple[int, Dict[str, int]]:
    """
    Instantiates GptModel on PyTorch's meta device to calculate exact parameter count
    with zero memory allocation, correctly accounting for layer sharing and tied weights.
    Returns: (total_parameters, module_breakdown_dict)
    """
    cfg = dict(config)

    # Use meta device for zero-allocation instantiation, fallback to CPU if unsupported
    try:
        with torch.device("meta"):
            model = GptModel(cfg)
    except Exception:
        model = GptModel(cfg)

    # Unique parameters (accounts for tied weights, e.g. out_head tied to tok_emb)
    unique_params = set(model.parameters())
    total_params = sum(p.numel() for p in unique_params)

    # Detailed component breakdown
    breakdown = {}
    if hasattr(model, "tok_emb") and model.tok_emb is not None:
        breakdown["token_embeddings"] = sum(p.numel() for p in model.tok_emb.parameters())
    if hasattr(model, "pos_emb") and model.pos_emb is not None:
        breakdown["position_embeddings"] = sum(p.numel() for p in model.pos_emb.parameters())
    if hasattr(model, "trf_blocks") and model.trf_blocks is not None:
        breakdown["transformer_blocks"] = sum(p.numel() for p in model.trf_blocks.parameters())
    if hasattr(model, "final_norm") and model.final_norm is not None:
        breakdown["final_norm"] = sum(p.numel() for p in model.final_norm.parameters())
    if hasattr(model, "out_head") and model.out_head is not None:
        is_tied = cfg.get("tie_embeddings", cfg.get("tie_word_embeddings", False))
        head_params = sum(p.numel() for p in model.out_head.parameters())
        breakdown["output_head"] = 0 if is_tied else head_params

    return total_params, breakdown


def calculate_params(file_path: str) -> int:
    """Reads model-params.json and returns the total parameter count."""
    p = Path(file_path).resolve()
    if not p.exists():
        raise FileNotFoundError(f"Model parameters file not found: {p}")

    if p.is_dir():
        candidates = list(p.glob("*.model-params.json")) + list(p.glob(".model-params.json"))
        if candidates:
            p = candidates[0]
        else:
            raise FileNotFoundError(f"Could not find any .model-params.json file in directory: {p}")

    with open(p, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    if not isinstance(cfg, dict):
        raise ValueError(f"Expected JSON dictionary in {p}, got {type(cfg).__name__}")

    total_params, breakdown = calculate_parameters_from_config(cfg)

    # Format human-readable sizes
    if total_params >= 1_000_000_000:
        size_str = f"{total_params / 1_000_000_000:.2f}B"
    elif total_params >= 1_000_000:
        size_str = f"{total_params / 1_000_000:.2f}M"
    elif total_params >= 1_000:
        size_str = f"{total_params / 1_000:.2f}K"
    else:
        size_str = f"{total_params}"

    arch = cfg.get("arch_family", "gpt2")
    layers = cfg.get("n_layers", "N/A")
    emb = cfg.get("emb_dim", "N/A")
    heads = cfg.get("n_heads", "N/A")
    vocab = cfg.get("vocab_size", "N/A")
    tied = cfg.get("tie_embeddings", cfg.get("tie_word_embeddings", False))

    print(f"File Path        : {p}")
    print(f"Architecture     : {arch} (Layers: {layers}, Dim: {emb}, Heads: {heads}, Vocab: {vocab}, Tied: {tied})")
    print(f"Total Parameters : {total_params:,} (~{size_str})")

    return total_params


def main():
    parser = argparse.ArgumentParser(
        description="Calculate the total parameter count of a model from its model-params.json specification."
    )
    parser.add_argument(
        "--file_path", "-f",
        type=str,
        required=True,
        help="Path to the model-params.json file."
    )

    args = parser.parse_args()

    try:
        calculate_params(args.file_path)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
