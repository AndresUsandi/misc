import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
import requests


PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from gptutils.consoleutils import print, create_progress_bar
from gptio.pathutil import (
    resolve_path,
    TARGET_ROOT,
    TARGET_MODEL,
    TARGET_PARAMS,
)
from repos.registry import MODEL_REGISTRY, MODEL_ALIASES


def lookup_model_spec(spec: str) -> Optional[Dict[str, Any]]:
    spec_clean = spec.lower().strip()
    if spec_clean in MODEL_REGISTRY:
        return MODEL_REGISTRY[spec_clean]
    if spec_clean in MODEL_ALIASES:
        return MODEL_REGISTRY[MODEL_ALIASES[spec_clean]]

    # Check hyphen/colon direct variants (e.g. gpt2-124m <-> gpt2:124m)
    alt_colon = spec_clean.replace("-", ":")
    if alt_colon in MODEL_REGISTRY:
        return MODEL_REGISTRY[alt_colon]
    if alt_colon in MODEL_ALIASES:
        return MODEL_REGISTRY[MODEL_ALIASES[alt_colon]]

    alt_dash = spec_clean.replace(":", "-")
    if alt_dash in MODEL_REGISTRY:
        return MODEL_REGISTRY[alt_dash]
    if alt_dash in MODEL_ALIASES:
        return MODEL_REGISTRY[MODEL_ALIASES[alt_dash]]

    return None


def download_file(url: str, destination: Path) -> Path:
    """Downloads a file from url to destination with visual progress tracking."""
    destination.parent.mkdir(parents=True, exist_ok=True)

    response = requests.get(url, stream=True, timeout=60)
    response.raise_for_status()

    file_size = int(response.headers.get("Content-Length", 0))

    if destination.exists() and file_size > 0 and destination.stat().st_size == file_size:
        print(f"[gptdownload] File already exists and is complete: {destination}")
        return destination

    block_size = 1024 * 1024  # 1 MB
    print(f"[gptdownload] Downloading {destination.name} ({file_size / (1024 * 1024):.1f} MB total)...")

    with create_progress_bar(total=file_size, desc=destination.name, unit="iB", unit_scale=True) as pbar:
        with open(destination, "wb") as f:
            for chunk in response.iter_content(chunk_size=block_size):
                if chunk:
                    f.write(chunk)
                    pbar.update(len(chunk))

    print(f"[gptdownload] Download complete: {destination}")
    return destination


def download_model(model_spec: str, models_dir: str) -> Tuple[Path, Path]:
    """
    Downloads pretrained model weights and writes configuration into:
      [models_dir]/[model]-[size]/model.pth
      [models_dir]/[model]-[size]/config.json
    """
    info = lookup_model_spec(model_spec)
    if info is None:
        supported = sorted(list(MODEL_REGISTRY.keys()))
        raise ValueError(f"Unknown model specification '{model_spec}'.\nSupported model specifiers:\n" + "\n".join(f"  - {k}" for k in supported))

    canonical_name = info["canonical_name"]
    canonical_size = info["canonical_size"]
    full_name = f"{canonical_name}-{canonical_size}"
    url = info["repo_url"]
    config = dict(info["config"])

    # Target directory: [models_dir]/[full_name]
    dest_dir = resolve_path(full_name, TARGET_ROOT, models_dir=models_dir or "bin")
    dest_dir.mkdir(parents=True, exist_ok=True)

    dest_pth = resolve_path(full_name, TARGET_MODEL, models_dir=models_dir or "bin")

    # Download .pth weights
    download_file(url, dest_pth)

    # Download companion tokenizer if available
    tok_url = info.get("tokenizer_url")
    tok_filename = None
    if tok_url:
        tok_filename = tok_url.split("/")[-1]
        tok_pth = dest_dir / tok_filename
        download_file(tok_url, tok_pth)

    # Build model-params dict with required parameters
    model_params = dict(config)
    # Pad vocab_size to 50304 for GPT-2 models (Tensor Core GEMM alignment)
    if model_params.get("vocab_size") == 50257 or info.get("family") == "gpt2":
        model_params["vocab_size"] = 50304

    if "tie_embeddings" not in model_params:
        is_gpt2 = info.get("family") == "gpt2"
        model_params["tie_embeddings"] = config.get("tie_embeddings", config.get("tie_word_embeddings", True if is_gpt2 else False))
    if tok_filename:
        model_params["tokenizer"] = tok_filename  # get_tokenizer() loads it from the model folder

    # Write .model-params.json
    params_path = resolve_path(full_name, TARGET_PARAMS, models_dir=models_dir or "bin")
    with open(params_path, "w", encoding="utf-8") as f:
        json.dump(model_params, f, indent=2)

    print(f"[gptdownload] Successfully prepared model in: {dest_dir}")
    print(f"[gptdownload]   Checkpoint  : {dest_pth}")
    print(f"[gptdownload]   Model Params: {params_path}")
    if tok_filename:
        print(f"[gptdownload]   Tokenizer   : {dest_dir / tok_filename}")

    return dest_pth, params_path


def list_models():
    """Prints a formatted table of all models available in MODEL_REGISTRY."""
    headers = ["Model Name", "Canonical Size", "Context Length", "Emb Dim", "N Heads", "N Layers"]
    rows = []
    for model_key, info in MODEL_REGISTRY.items():
        name = model_key
        size = info.get("canonical_size", "-")
        cfg = info.get("config", {})
        ctx = str(cfg.get("context_length", "-"))
        emb = str(cfg.get("emb_dim", "-"))
        heads = str(cfg.get("n_heads", "-"))
        layers = str(cfg.get("n_layers", "-"))
        rows.append([name, size, ctx, emb, heads, layers])

    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, val in enumerate(row):
            col_widths[i] = max(col_widths[i], len(val))

    header_line = " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
    separator = "-+-".join("-" * col_widths[i] for i in range(len(headers)))

    print("\n" + "=" * len(separator))
    title = "AVAILABLE PRETRAINED MODELS IN REGISTRY"
    padding = max(0, (len(separator) - len(title)) // 2)
    print(" " * padding + title)
    print("=" * len(separator))
    print(header_line)
    print(separator)
    for row in rows:
        print(" | ".join(row[i].ljust(col_widths[i]) for i in range(len(headers))))
    print("=" * len(separator) + "\n")
