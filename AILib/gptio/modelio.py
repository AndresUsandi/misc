# Copyright (c) Sebastian Raschka under Apache License 2.0 (see LICENSE.txt).
# Model I/O Module for Pure Model Weights and Configurations
# Dedicated strictly to final model persistence (.pth) and loading for inference.

import json
import os
from pathlib import Path
import re
import shutil
import sys
import time
from typing import Any, Dict, List, Optional, Tuple, Union

import torch
import torch.nn as nn

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from argsutil import ModelArgs
from gptutils.consoleutils import print
from gptio.pathutil import (
    resolve_path,
    clean_model_name,
    TARGET_ROOT,
    TARGET_MODEL,
    TARGET_PARAMS,
    TARGET_CHECKPOINT,
)


def _unwrap_model(model: nn.Module) -> nn.Module:
    """Unwraps a model from wrappers (DataParallel, DDP, torch.compile _orig_mod, MultiGpuGptModelPP)."""
    while True:
        if hasattr(model, "module"):
            model = model.module
        elif hasattr(model, "_orig_mod"):
            model = model._orig_mod
        elif hasattr(model, "raw_model"):
            model = model.raw_model
        else:
            break
    return model


def _clean_state_dict_keys(state_dict: Dict[str, Any], target_model: nn.Module) -> Dict[str, Any]:
    """Ensures state_dict keys align with target model, adjusting prefixes, QKV projections, and HF keys."""
    target_state = target_model.state_dict()
    target_keys = set(target_state.keys())
    sd_keys = set(state_dict.keys())

    if target_keys == sd_keys:
        shapes_match = True
        for k in target_keys:
            if isinstance(state_dict[k], torch.Tensor) and isinstance(target_state[k], torch.Tensor):
                if state_dict[k].shape != target_state[k].shape:
                    shapes_match = False
                    break
        if shapes_match:
            return state_dict

    sample_target = next(iter(target_keys)) if target_keys else ""
    sample_sd = next(iter(sd_keys)) if sd_keys else ""

    # Translate HuggingFace / standard OpenLLM keys if present
    translated_sd = {}
    for k, v in state_dict.items():
        new_k = k
        if new_k == "model.embed_tokens.weight":
            new_k = "tok_emb.weight"
        elif new_k in ["model.norm.weight", "model.norm.scale"]:
            new_k = "final_norm.scale" if "final_norm.scale" in target_keys else "final_norm.weight"
        elif new_k == "lm_head.weight":
            new_k = "out_head.weight"
        else:
            # Map layer components
            m = re.match(r"^model\.layers\.(\d+)\.(.*)$", new_k)
            if m:
                layer_idx, rest = m.group(1), m.group(2)
                if rest in ["input_layernorm.weight", "input_layernorm.scale"]:
                    new_k = f"trf_blocks.{layer_idx}.norm1.scale" if f"trf_blocks.{layer_idx}.norm1.scale" in target_keys else f"trf_blocks.{layer_idx}.norm1.weight"
                elif rest in ["post_attention_layernorm.weight", "post_attention_layernorm.scale"]:
                    new_k = f"trf_blocks.{layer_idx}.norm2.scale" if f"trf_blocks.{layer_idx}.norm2.scale" in target_keys else f"trf_blocks.{layer_idx}.norm2.weight"
                elif rest == "self_attn.q_proj.weight":
                    new_k = f"trf_blocks.{layer_idx}.att.W_query.weight"
                elif rest == "self_attn.k_proj.weight":
                    new_k = f"trf_blocks.{layer_idx}.att.W_key.weight"
                elif rest == "self_attn.v_proj.weight":
                    new_k = f"trf_blocks.{layer_idx}.att.W_value.weight"
                elif rest == "self_attn.o_proj.weight":
                    new_k = f"trf_blocks.{layer_idx}.att.out_proj.weight"
                elif rest == "mlp.gate_proj.weight":
                    new_k = f"trf_blocks.{layer_idx}.ff.fc1.weight"
                elif rest == "mlp.up_proj.weight":
                    new_k = f"trf_blocks.{layer_idx}.ff.fc2.weight"
                elif rest == "mlp.down_proj.weight":
                    new_k = f"trf_blocks.{layer_idx}.ff.fc3.weight"
        translated_sd[new_k] = v

    # Strip prefixes if target doesn't have them
    cleaned_sd = {}
    for k, v in translated_sd.items():
        new_k = k
        for prefix in ["_orig_mod.", "module.", "raw_model."]:
            if new_k.startswith(prefix) and not sample_target.startswith(prefix):
                new_k = new_k[len(prefix):]
        cleaned_sd[new_k] = v

    # Add prefix if target has it
    if sample_target.startswith("_orig_mod.") and not sample_sd.startswith("_orig_mod."):
        cleaned_sd = {f"_orig_mod.{k}": v for k, v in cleaned_sd.items()}
    elif sample_target.startswith("module.") and not sample_sd.startswith("module."):
        cleaned_sd = {f"module.{k}": v for k, v in cleaned_sd.items()}

    # Handle fused QKV <-> split Q, K, V projections
    for k in list(target_keys):
        if k.endswith(".att.W_qkv.weight") and k not in cleaned_sd:
            prefix = k[:-len(".att.W_qkv.weight")]
            q_w = cleaned_sd.get(f"{prefix}.att.W_query.weight")
            k_w = cleaned_sd.get(f"{prefix}.att.W_key.weight")
            v_w = cleaned_sd.get(f"{prefix}.att.W_value.weight")
            if q_w is not None and k_w is not None and v_w is not None:
                cleaned_sd[k] = torch.cat([q_w, k_w, v_w], dim=0)

        if k.endswith(".att.W_qkv.bias") and k not in cleaned_sd:
            prefix = k[:-len(".att.W_qkv.bias")]
            q_b = cleaned_sd.get(f"{prefix}.att.W_query.bias")
            k_b = cleaned_sd.get(f"{prefix}.att.W_key.bias")
            v_b = cleaned_sd.get(f"{prefix}.att.W_value.bias")
            if q_b is not None and k_b is not None and v_b is not None:
                cleaned_sd[k] = torch.cat([q_b, k_b, v_b], dim=0)

        if k.endswith(".att.W_query.weight") and k not in cleaned_sd:
            prefix = k[:-len(".att.W_query.weight")]
            qkv_w = cleaned_sd.get(f"{prefix}.att.W_qkv.weight")
            if qkv_w is not None:
                splits = torch.chunk(qkv_w, 3, dim=0)
                cleaned_sd[f"{prefix}.att.W_query.weight"] = splits[0]
                cleaned_sd[f"{prefix}.att.W_key.weight"] = splits[1]
                cleaned_sd[f"{prefix}.att.W_value.weight"] = splits[2]

        if k.endswith(".att.W_query.bias") and k not in cleaned_sd:
            prefix = k[:-len(".att.W_query.bias")]
            qkv_b = cleaned_sd.get(f"{prefix}.att.W_qkv.bias")
            if qkv_b is not None:
                splits = torch.chunk(qkv_b, 3, dim=0)
                cleaned_sd[f"{prefix}.att.W_query.bias"] = splits[0]
                cleaned_sd[f"{prefix}.att.W_key.bias"] = splits[1]
                cleaned_sd[f"{prefix}.att.W_value.bias"] = splits[2]

    # Handle final_norm scale <-> weight alias
    if "final_norm.scale" in target_keys and "final_norm.scale" not in cleaned_sd and "final_norm.weight" in cleaned_sd:
        cleaned_sd["final_norm.scale"] = cleaned_sd["final_norm.weight"]
    if "final_norm.weight" in target_keys and "final_norm.weight" not in cleaned_sd and "final_norm.scale" in cleaned_sd:
        cleaned_sd["final_norm.weight"] = cleaned_sd["final_norm.scale"]

    for k in list(target_keys):
        if k.endswith(".norm1.scale") and k not in cleaned_sd and k.replace(".scale", ".weight") in cleaned_sd:
            cleaned_sd[k] = cleaned_sd[k.replace(".scale", ".weight")]
        elif k.endswith(".norm1.weight") and k not in cleaned_sd and k.replace(".weight", ".scale") in cleaned_sd:
            cleaned_sd[k] = cleaned_sd[k.replace(".weight", ".scale")]
        if k.endswith(".norm2.scale") and k not in cleaned_sd and k.replace(".scale", ".weight") in cleaned_sd:
            cleaned_sd[k] = cleaned_sd[k.replace(".scale", ".weight")]
        elif k.endswith(".norm2.weight") and k not in cleaned_sd and k.replace(".weight", ".scale") in cleaned_sd:
            cleaned_sd[k] = cleaned_sd[k.replace(".weight", ".scale")]

        # Handle FeedForward aliases: ff.fc1 <-> ff.layers.0 and ff.fc2 <-> ff.layers.2
        if ".ff.fc1." in k and k not in cleaned_sd:
            legacy_k = k.replace(".ff.fc1.", ".ff.layers.0.")
            if legacy_k in cleaned_sd:
                cleaned_sd[k] = cleaned_sd[legacy_k]
        elif ".ff.layers.0." in k and k not in cleaned_sd:
            new_k = k.replace(".ff.layers.0.", ".ff.fc1.")
            if new_k in cleaned_sd:
                cleaned_sd[k] = cleaned_sd[new_k]

        if ".ff.fc2." in k and k not in cleaned_sd:
            legacy_k = k.replace(".ff.fc2.", ".ff.layers.2.")
            if legacy_k in cleaned_sd:
                cleaned_sd[k] = cleaned_sd[legacy_k]
        elif ".ff.layers.2." in k and k not in cleaned_sd:
            new_k = k.replace(".ff.layers.2.", ".ff.fc2.")
            if new_k in cleaned_sd:
                cleaned_sd[k] = cleaned_sd[new_k]

    # Handle vocab_size padding or truncation (e.g. 50257 <-> 50304 for Tensor Cores)
    target_dict = target_model.state_dict() if hasattr(target_model, "state_dict") else {}
    for emb_key in ["tok_emb.weight", "out_head.weight", "lm_head.weight"]:
        if emb_key in target_keys and emb_key in cleaned_sd and emb_key in target_dict:
            t_shape = target_dict[emb_key].shape
            c_shape = cleaned_sd[emb_key].shape
            if t_shape != c_shape and len(t_shape) == 2 and len(c_shape) == 2:
                t_rows, t_cols = t_shape
                c_rows, c_cols = c_shape
                if t_cols == c_cols:
                    if c_rows < t_rows:
                        # Pad extra rows with zeros
                        padded = target_dict[emb_key].clone().to(device=cleaned_sd[emb_key].device, dtype=cleaned_sd[emb_key].dtype)
                        padded[:c_rows, :] = cleaned_sd[emb_key]
                        cleaned_sd[emb_key] = padded
                    else:
                        # Truncate extra padding rows
                        cleaned_sd[emb_key] = cleaned_sd[emb_key][:t_rows, :]

    # Filter out keys that don't belong to target model (e.g. legacy 'mask' buffers)
    final_sd = {}
    for k, v in cleaned_sd.items():
        if k in target_keys:
            final_sd[k] = v

    return final_sd


def load_model_config(args: ModelArgs) -> Optional[Dict[str, Any]]:
    """Extracts the selected model's configuration dictionary from companion json, saved model file, or registry."""
    return _load_model_config(args.model_name, models_dir=args.models_base_dir)


def _load_model_config(
    model_name: Union[str, Path],
    models_dir: Union[str, Path] = "bin",
) -> Optional[Dict[str, Any]]:
    """Path-level variant of load_model_config: accepts a model name or a weights/checkpoint file path."""
    if not model_name:
        return None
    # 1. Check model-params / config JSON via resolve_path
    params_path = resolve_path(model_name, target=TARGET_PARAMS, models_dir=models_dir)
    if params_path.exists() and params_path.is_file():
        try:
            with open(params_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass

    # 2. Check embedded config in model weights or checkpoint
    for target_t in (TARGET_MODEL, TARGET_CHECKPOINT):
        p = resolve_path(model_name, target=target_t, models_dir=models_dir)
        if p.exists() and p.is_file():
            try:
                data = torch.load(str(p), map_location="cpu", weights_only=False)
                if isinstance(data, dict):
                    for k in ["config", "model_config", "gpt_config"]:
                        if k in data and isinstance(data[k], dict):
                            return data[k]
            except Exception:
                pass

    # 3. Registry lookup for standard pretrained architectures (e.g. gpt2:124M)
    raw = clean_model_name(model_name)
    try:
        from repos.modelrepo import lookup_model_spec
        info = lookup_model_spec(raw)
        if info is not None and "config" in info:
            cfg = dict(info["config"])
            if cfg.get("vocab_size") == 50257 or info.get("family") == "gpt2":
                cfg["vocab_size"] = 50304
            return cfg
    except Exception:
        pass

    return None


def save_model(
    model: nn.Module,
    args: ModelArgs,
    config: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Saves a clean final model (.pth) and companion configuration JSON without optimizer states
    or training telemetry fluff. Designed specifically for clean inference and deployment.
    Path and filename resolution is strictly internal: [models_dir]/[model_name]/[model_name].pth
    """
    if not args.model_name:
        raise ValueError("save_model requires 'model_name' to be specified.")

    unwrapped = _unwrap_model(model)

    # Determine configuration
    model_config = config
    if model_config is None and hasattr(unwrapped, "config") and isinstance(unwrapped.config, dict):
        model_config = unwrapped.config
    elif model_config is None:
        model_config = {
            "vocab_size": getattr(unwrapped, "tok_emb", nn.Embedding(50257, 768)).num_embeddings if hasattr(unwrapped, "tok_emb") else 50257,
            "emb_dim": getattr(unwrapped, "tok_emb", nn.Embedding(50257, 768)).embedding_dim if hasattr(unwrapped, "tok_emb") else 768,
            "n_layers": len(unwrapped.trf_blocks) if hasattr(unwrapped, "trf_blocks") else 12,
        }

    target_dir = resolve_path(args.model_name, target=TARGET_ROOT, models_dir=args.models_base_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    target_file = resolve_path(args.model_name, target=TARGET_MODEL, models_dir=args.models_base_dir)
    tmp_file = resolve_path(args.model_name, target=TARGET_MODEL, suffix=".tmp", models_dir=args.models_base_dir)
    tmp2_file = resolve_path(args.model_name, target=TARGET_MODEL, suffix=".tmp2", models_dir=args.models_base_dir)

    raw_state_dict = unwrapped.state_dict()
    cpu_state_dict = {k: v.cpu() if isinstance(v, torch.Tensor) else v for k, v in raw_state_dict.items()}

    model_payload: Dict[str, Any] = {
        "model_state_dict": cpu_state_dict,
        "config": model_config,
    }

    # Step 1: Write clean model payload with 3 retries
    max_write_attempts = 3
    write_success = False
    last_write_err = None
    for attempt in range(1, max_write_attempts + 1):
        try:
            torch.save(model_payload, str(tmp_file))
            write_success = True
            break
        except Exception as e:
            last_write_err = e
            print(f"[ModelIO Warning] Attempt {attempt}/{max_write_attempts} failed to write '{tmp_file.name}': {e}")
            time.sleep(1.0)

    if not write_success:
        raise RuntimeError(f"Failed to write model to '{tmp_file.name}' after {max_write_attempts} attempts: {last_write_err}")

    # Step 2: Create second copy (.tmp2)
    shutil.copyfile(str(tmp_file), str(tmp2_file))

    # Step 3: Delete original weights file (.pth)
    if target_file.exists():
        for _ in range(3):
            try:
                target_file.unlink()
                break
            except Exception:
                time.sleep(1.0)

    # Step 4: Rename .tmp2 to .pth
    renamed = False
    for _ in range(3):
        try:
            if target_file.exists():
                target_file.unlink()
            tmp2_file.rename(target_file)
            renamed = True
            break
        except Exception:
            try:
                tmp2_file.replace(target_file)
                renamed = True
                break
            except Exception:
                time.sleep(1.0)

    if not renamed:
        shutil.copyfile(str(tmp_file), str(target_file))

    # Clean up temporary swap file
    if tmp_file.exists():
        try:
            tmp_file.unlink()
        except Exception:
            pass

    # Step 5: Save companion model-params.json only when the model folder has none (never overwrite the user's spec,
    # e.g. with the runtime-padded vocab_size)
    params_file = resolve_path(args.model_name, target=TARGET_PARAMS, models_dir=args.models_base_dir)
    cfg_to_write = dict(model_config)

    if not params_file.exists():
        try:
            with open(params_file, "w", encoding="utf-8") as f:
                json.dump(cfg_to_write, f, indent=2)
        except Exception as e:
            print(f"[ModelIO Warning] Could not save '{params_file.name}': {e}")

    print(f"[modelio] Successfully saved clean final model to: {target_file}")
    return str(target_file)


def load_model_weights(
    model: nn.Module,
    args: ModelArgs,
    device: Optional[Union[str, torch.device]] = None,
    strict: bool = True,
) -> nn.Module:
    """Loads weights into an existing model instance from a final model .pth file or model folder."""
    if not args.model_name:
        raise ValueError("load_model_weights requires 'model_name' to be specified.")

    actual_path = resolve_path(args.model_name, target=TARGET_MODEL, models_dir=args.models_base_dir)
    if not actual_path.exists():
        actual_path_str, _ = resolve_model_path_and_config(args.model_name, models_dir=args.models_base_dir)
        actual_path = Path(actual_path_str)

    map_loc = "cpu"  # transient host copy: load_state_dict copies into the (GPU) model params, so the fp32 .pth never sits on the GPU next to the model

    try:
        payload = torch.load(actual_path, map_location=map_loc, weights_only=True)
    except Exception:
        payload = torch.load(actual_path, map_location=map_loc, weights_only=False)

    if isinstance(payload, dict) and ("model_state_dict" in payload or "state_dict" in payload):
        state_dict = payload.get("model_state_dict", payload.get("state_dict"))
    else:
        state_dict = payload

    unwrapped = _unwrap_model(model)
    cleaned_sd = _clean_state_dict_keys(state_dict, unwrapped)

    target_dtype = None
    try:
        target_dtype = next(unwrapped.parameters()).dtype
    except StopIteration:
        pass

    unwrapped.load_state_dict(cleaned_sd, strict=strict)
    if target_dtype is not None:
        unwrapped.to(dtype=target_dtype)
    if device is not None and not hasattr(model, "layer_devices"):
        model.to(device=device)

    print(f"[modelio] Successfully loaded model weights from: {actual_path}")
    return model


def load_model(
    model_class: Any,
    args: ModelArgs,
    fallback_config: Optional[Dict[str, Any]] = None,
    device: Optional[Union[str, torch.device]] = None,
    strict: bool = True,
    **kwargs: Any
) -> Tuple[nn.Module, Dict[str, Any]]:
    """Instantiates a model class using its saved configuration and loads final weights (.pth)."""
    if not args.model_name:
        raise ValueError("load_model requires 'model_name' to be specified.")

    config = load_model_config(args)
    if config is None:
        if fallback_config is None:
            raise ValueError(f"No config found for '{args.model_name}' and no fallback_config provided.")
        config = fallback_config

    model = model_class(config, **kwargs)
    load_model_weights(model, args, device=device, strict=strict)
    return model, config


def resolve_model_path_and_config(
    model_name_or_path: Union[str, Path],
    models_base_dir: Union[str, Path] = "bin",
    **kwargs: Any
) -> Tuple[str, Optional[Dict[str, Any]]]:
    """
    Resolves a model name, folder, or file path into
    the concrete checkpoint .pth path and loaded configuration dictionary.
    """
    models_dir = kwargs.get("models_dir", kwargs.get("models_root_dir", models_base_dir))
    p = Path(model_name_or_path)

    # 1. Direct file path
    if p.exists() and p.is_file():
        cfg = _load_model_config(p)
        return str(p), cfg

    # 2. Canonical model weights (.pth) or checkpoint (.chk) resolution via pathutil
    pth_file = resolve_path(str(model_name_or_path), target=TARGET_MODEL, models_dir=models_dir)
    if pth_file.exists() and pth_file.is_file():
        cfg = _load_model_config(pth_file)
        return str(pth_file), cfg

    chk_file = resolve_path(str(model_name_or_path), target=TARGET_CHECKPOINT, models_dir=models_dir)
    if chk_file.exists() and chk_file.is_file():
        cfg = _load_model_config(chk_file)
        return str(chk_file), cfg

    # 3. Registry lookup and auto-download for external pretrained models (e.g. gpt2:124M)
    models_dir_path = Path(models_dir)
    raw = str(model_name_or_path).strip()
    try:
        from repos.modelrepo import lookup_model_spec, download_model
        info = lookup_model_spec(raw)
        if info is not None:
            dest_pth, _ = download_model(raw, models_dir=str(models_dir_path))
            cfg = _load_model_config(dest_pth)
            return str(dest_pth), cfg
    except Exception:
        pass

    raise FileNotFoundError(
        f"Could not locate model '{model_name_or_path}'. "
        f"Expected model weights file at: '{pth_file.resolve()}'."
    )

