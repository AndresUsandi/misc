# Copyright (c) Sebastian Raschka under Apache License 2.0 (see LICENSE.txt).
# Utility to transform model files from one kind to another (currently: training checkpoint -> final model file -> GGUF file).

import argparse
import re
from pathlib import Path
from typing import Optional

import torch

from gptio.checkpoint import atomic_replace_with_retry
from gptio.pathutil import CHECKPOINT_DPO_EXT, CHECKPOINT_SFT_EXT, CHECKPOINT_TMP_SUFFIX, CHECKPOINT_TRN_EXT, GGUF_EXT, MODEL_EXT
from gptutils.consoleutils import print


def next_free_path(path: Path) -> Path:
    """path itself when it does not exist yet, else the first free one of path + 1, path + 2, ... (blah.pth, blah.pth1, blah.pth2, ...)."""
    candidate, n = path, 0
    while candidate.exists():
        n += 1
        candidate = path.with_name(f"{path.name}{n}")
    return candidate


def checkpoint_to_model(source_file: Path, target_file: Optional[Path]) -> Path:
    """Writes the weights + config of a checkpoint (.chk.trn / .chk.sft / .chk.dpo) as a final model file (.pth), same layout save_model writes."""
    ext = next((e for e in (CHECKPOINT_TRN_EXT, CHECKPOINT_SFT_EXT, CHECKPOINT_DPO_EXT) if source_file.name.lower().endswith(e)), None)
    if ext is None:
        raise ValueError(f"'{source_file}' is not a checkpoint file (expected {CHECKPOINT_TRN_EXT}, {CHECKPOINT_SFT_EXT} or {CHECKPOINT_DPO_EXT}).")
    if target_file is None:
        target_file = next_free_path(source_file.with_name(source_file.name[:-len(ext)] + MODEL_EXT))

    ckpt = torch.load(source_file, map_location="cpu", weights_only=False)
    if not isinstance(ckpt, dict) or "model_state_dict" not in ckpt or "config" not in ckpt:
        raise ValueError(f"'{source_file}' has no 'model_state_dict' and 'config' entries; it is not a checkpoint saved by this project.")

    target_file.parent.mkdir(parents=True, exist_ok=True)
    tmp_file = target_file.with_name(target_file.name + CHECKPOINT_TMP_SUFFIX)
    torch.save({"model_state_dict": ckpt["model_state_dict"], "config": ckpt["config"]}, tmp_file)
    atomic_replace_with_retry(tmp_file, target_file)
    print(f"[model_file_util] Converted checkpoint '{source_file}' to model file '{target_file}'.")
    return target_file


def model_to_gguf(source_file: Path, target_file: Optional[Path]) -> Path:
    """Writes a model file (.pth) as a GGUF file (.gguf) that llama.cpp and Ollama load; gptio.ggufio does the work and lists what it can export."""
    from gptio.ggufio import write_gguf  # imported here so that only this conversion needs the gguf package
    ext = re.search(r"\.pth\d*$", source_file.name, re.IGNORECASE)  # .pth, or the numbered .pth1, .pth2, ... that checkpoint_to_model picks when blah.pth exists
    if ext is None:
        raise ValueError(f"'{source_file}' is not a model file (expected {MODEL_EXT}).")
    if target_file is None:
        target_file = next_free_path(source_file.with_name(source_file.name[:ext.start()] + GGUF_EXT))

    target_file.parent.mkdir(parents=True, exist_ok=True)
    tmp_file = target_file.with_name(target_file.name + CHECKPOINT_TMP_SUFFIX)
    write_gguf(source_file, tmp_file)
    atomic_replace_with_retry(tmp_file, target_file)
    print(f"[model_file_util] Converted model file '{source_file}' to GGUF file '{target_file}'.")
    return target_file


CONVERSIONS = {"checkpoint_to_model": checkpoint_to_model, "model_to_gguf": model_to_gguf}


def main():
    parser = argparse.ArgumentParser(description="Transform model files from one kind to another.")
    parser.add_argument("--conversion_type", required=True, choices=list(CONVERSIONS), help="checkpoint_to_model: a checkpoint (.chk.trn, .chk.sft or .chk.dpo) to a model file (.pth). model_to_gguf: a model file (.pth) to a GGUF file (.gguf) for llama.cpp / Ollama.")
    parser.add_argument("--source_file", required=True, type=Path, help="Path to the source file.")
    parser.add_argument("--target_file", type=Path, default=None, help="Path to the target file. Default: the source file with its extension swapped for the target kind's (e.g. blah.chk.sft -> blah.pth, blah.pth -> blah.gguf); if that exists, a sequential number is appended (blah.pth1, blah.pth2, ...) until a free name is found.")
    args = parser.parse_args()

    try:
        CONVERSIONS[args.conversion_type](args.source_file, args.target_file)
    except Exception as e:
        print(f"\n[model_file_util] Error: {e}")
        exit(1)


if __name__ == "__main__":
    main()
