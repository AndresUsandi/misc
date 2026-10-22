# Copyright (c) Sebastian Raschka under Apache License 2.0 (see LICENSE.txt).
# Unified Path Resolution Utility for GPT Models, Datasets, Checkpoints, and Options.

import os
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

if TYPE_CHECKING:  # argsutil imports this module, so only the type checker sees the import
    from argsutil import ModelArgs

CHECKPOINT_EXT: str = ".chk"
CHECKPOINT_TRN_EXT: str = ".chk.trn"
CHECKPOINT_SFT_EXT: str = ".chk.sft"
CHECKPOINT_DPO_EXT: str = ".chk.dpo"
CHECKPOINT_TMP_SUFFIX: str = ".tmp"
CHECKPOINT_SWAP_SUFFIX: str = ".tmp2"
CHECKPOINT_BAK_SUFFIX: str = ".bak"
MODEL_EXT: str = ".pth"
MODEL_ALT_EXT: str = ".pt"
GGUF_EXT: str = ".gguf"

TARGET_ROOT: str = "root"
TARGET_DATA: str = "data"
TARGET_CHECKPOINT: str = "checkpoint"
TARGET_MODEL: str = "model"
TARGET_PARAMS: str = "params"
TARGET_OPTIONS: str = "options"
TARGET_STEPS_CACHE: str = "steps_cache"
TARGET_PLOT: str = "plot"
TARGET_TOKENIZER: str = "tokenizer"
TOKENIZER_FILE: str = "tokenizer.json"

STAGE_TRAIN: str = "train"
STAGE_TUNE: str = "tune"
STAGE_OPTIMIZE: str = "optimize"
STAGE_INFER: str = "infer"


MULTI_GPU_PP: str = "parallel-pipeline"
MULTI_GPU_DP: str = "data-parallelism"
MULTI_GPU_DP_ZERO1: str = "data-parallelism-zero1"


def clean_model_name(model_name: str) -> str:
    """Strips file extensions and stage tags to produce the clean, canonical model name."""
    clean = str(model_name).strip()
    for suffix in [
        "-loss-plot-train.pdf", "-loss-plot-tune.pdf", "-loss-plot-optimize.pdf", "-loss-plot.pdf",
        ".model-params.json", ".model-param.json",
        ".options-train.json", ".options-tune.json", ".options-optimize.json", ".options-infer.json", ".options.json",
        f"{CHECKPOINT_TRN_EXT}{CHECKPOINT_SWAP_SUFFIX}", f"{CHECKPOINT_TRN_EXT}{CHECKPOINT_TMP_SUFFIX}", CHECKPOINT_TRN_EXT,
        f"{CHECKPOINT_SFT_EXT}{CHECKPOINT_SWAP_SUFFIX}", f"{CHECKPOINT_SFT_EXT}{CHECKPOINT_TMP_SUFFIX}", CHECKPOINT_SFT_EXT,
        f"{CHECKPOINT_DPO_EXT}{CHECKPOINT_SWAP_SUFFIX}", f"{CHECKPOINT_DPO_EXT}{CHECKPOINT_TMP_SUFFIX}", CHECKPOINT_DPO_EXT,
        f"{MODEL_EXT}{CHECKPOINT_SWAP_SUFFIX}", f"{MODEL_EXT}{CHECKPOINT_TMP_SUFFIX}", CHECKPOINT_EXT, MODEL_EXT, MODEL_ALT_EXT, ".json",
        ".trn", "-trn", "_trn",
        ".sft", "-sft", "_sft",
        ".dpo", "-dpo", "_dpo",
    ]:
        if clean.lower().endswith(suffix):
            clean = clean[:-len(suffix)]
            break
    return Path(clean).name


def resolve_model_dir(
    model_name: str,
    models_dir: Union[str, Path] = "bin",
) -> Path:
    """
    Resolves the root directory path for a model.
    Checks for exact folder match, with case-insensitive search fallback across models_dir.
    """
    clean_name = clean_model_name(model_name)
    models_dir_path = Path(models_dir)
    target_dir = models_dir_path / clean_name

    if not target_dir.exists() and models_dir_path.exists() and models_dir_path.is_dir():
        for sub in models_dir_path.iterdir():
            if sub.is_dir() and sub.name.lower() == clean_name.lower():
                return sub

    return target_dir


def resolve_path_with_override(
    args: "ModelArgs",
    stage: str = STAGE_TRAIN,
    override_folder: Optional[Union[str, Path]] = None,
) -> Path:
    """Resolves data directory or file path for training, fine-tuning, or DPO optimization."""
    if override_folder:
        return Path(override_folder)
    return resolve_path(args.model_name, target=TARGET_DATA, stage=stage, models_dir=args.models_base_dir)

def resolve_path(
    model_name: str,
    target: str = TARGET_ROOT,
    stage: Optional[str] = None,
    models_dir: Union[str, Path] = "bin",
    suffix: Optional[str] = None,
) -> Path:
    """
    Centralized path resolver for all model-related files, folders, checkpoints, and configurations.

    Targets supported (via TARGET_* constants):
      - TARGET_ROOT: Model root folder ([models_dir]/[model_name])
      - TARGET_DATA: Model data folder ([models_dir]/[model_name]/data, or data/[Training|Tuning|Optimizing] when stage provided)
      - TARGET_CHECKPOINT: Stage-specific checkpoint path (.chk.trn, .chk.sft, or .chk.dpo)
      - TARGET_MODEL: Final model weights file (.pth)
      - TARGET_PARAMS: Model parameters configuration JSON (.model-params.json)
      - TARGET_OPTIONS: Stage-specific options JSON (.options-[stage].json)
      - TARGET_STEPS_CACHE: Steps cache JSON (steps_cache.json)
      - TARGET_PLOT: Model loss plot PDF ([model_name]-loss-plot-[stage].pdf)
      - TARGET_TOKENIZER: The model's tokenizer file (tokenizer.json)
      - <custom_relative_path>: Any relative subfolder or file within the model directory (an absolute path is returned as is)
    """
    if not model_name:
        raise ValueError("resolve_path requires 'model_name' to be specified.")

    m_dir = resolve_model_dir(model_name, models_dir=models_dir)
    m_name = m_dir.name
    t = str(target).strip().lower() if target else TARGET_ROOT
    s = str(stage).strip().lower() if stage else None

    if t == TARGET_ROOT:
        return m_dir

    if t == TARGET_DATA:
        if s == STAGE_TRAIN:
            return m_dir / "data" / "Training"
        elif s == STAGE_TUNE:
            return m_dir / "data" / "Tuning"
        elif s == STAGE_OPTIMIZE:
            return m_dir / "data" / "Optimizing"
        return m_dir / "data"

    if t == TARGET_CHECKPOINT:
        chk_stage = s or STAGE_TRAIN
        if chk_stage == STAGE_TUNE:
            chk_ext = CHECKPOINT_SFT_EXT
        elif chk_stage == STAGE_OPTIMIZE:
            chk_ext = CHECKPOINT_DPO_EXT
        else:
            chk_ext = CHECKPOINT_TRN_EXT
        file_name = f"{m_name}{chk_ext}{suffix or ''}"
        return m_dir / file_name

    if t == TARGET_MODEL:
        file_name = f"{m_name}{MODEL_EXT}{suffix or ''}"
        return m_dir / file_name

    if t == TARGET_PARAMS:
        return m_dir / f"{m_name}.model-params.json"

    if t == TARGET_OPTIONS:
        stage_val = s or STAGE_TRAIN
        return m_dir / f"{m_name}.options-{stage_val}.json"

    if t == TARGET_STEPS_CACHE:
        return m_dir / "steps_cache.json"

    if t == TARGET_TOKENIZER:
        return m_dir / TOKENIZER_FILE

    if t == TARGET_PLOT:
        stage_val = s or STAGE_TRAIN
        if stage_val in (STAGE_TUNE, "tuning", "sft", "fine-tuning"):
            plot_stage = STAGE_TUNE
        elif stage_val in (STAGE_OPTIMIZE, "optimizing", "dpo"):
            plot_stage = STAGE_OPTIMIZE
        else:
            plot_stage = STAGE_TRAIN
        return m_dir / f"{m_name}-loss-plot-{plot_stage}.pdf"

    # Default: arbitrary subfolder or file path within model directory
    return m_dir / target


def resolve_checkpoint_candidates(
    model_name: str,
    stage: str = STAGE_TRAIN,
    models_dir: Union[str, Path] = "bin",
) -> List[Path]:
    """
    Returns an ordered list of existing checkpoint files to try loading for a model and stage,
    prioritizing stage-specific checkpoints followed by backup files (.tmp, .tmp2, .bak).
    """
    m_dir = resolve_model_dir(model_name, models_dir=models_dir)
    m_name = m_dir.name
    stage_val = str(stage).strip().lower() if stage else STAGE_TRAIN

    if stage_val == STAGE_OPTIMIZE:
        chk_order = [CHECKPOINT_DPO_EXT, CHECKPOINT_SFT_EXT, CHECKPOINT_TRN_EXT, CHECKPOINT_EXT]
    elif stage_val == STAGE_TUNE:
        chk_order = [CHECKPOINT_SFT_EXT, CHECKPOINT_TRN_EXT, CHECKPOINT_EXT]
    else:
        chk_order = [CHECKPOINT_TRN_EXT, CHECKPOINT_EXT]  # pretraining never continues from SFT/DPO weights

    paths_to_try: List[Path] = []
    for ext in chk_order:
        cand = m_dir / f"{m_name}{ext}"
        if cand.exists() and cand.is_file() and cand not in paths_to_try:
            paths_to_try.append(cand)

    # Backups (.tmp / .tmp2 / .bak) honor the same per-stage order as the primary checkpoints
    for b_path in [m_dir / f"{m_name}{ext}{suf}" for ext in chk_order for suf in (CHECKPOINT_TMP_SUFFIX, CHECKPOINT_SWAP_SUFFIX)] + [m_dir / f"{m_name}{CHECKPOINT_BAK_SUFFIX}"]:
        if b_path.exists() and b_path not in paths_to_try:
            paths_to_try.append(b_path)

    return paths_to_try


# TODO: QUESTION THE EXISTANCE OF THIS FUNCTION
def resolve_data_files(
    data_path_or_model: Union[str, Path],
    stage: str = STAGE_TRAIN,
    models_dir: Union[str, Path] = "bin",
) -> List[Path]:
    """
    Centralized dataset file resolver. Resolves a model name, directory path,
    or file path into an ordered list of Path objects for the requested stage.
    """
    raw_str = str(data_path_or_model).strip()
    raw_path = Path(raw_str)

    # If raw_str looks like a model name or does not exist as given, resolve it as a model's stage data folder
    if ("/" not in raw_str and "\\" not in raw_str and not raw_str.endswith((".txt", ".json", ".jsonl"))) or not raw_path.exists():
        target_path = resolve_path(raw_str, target=TARGET_DATA, stage=stage, models_dir=models_dir)
        if target_path.exists():
            raw_path = target_path

    if raw_path.is_file():
        return [raw_path]

    if not raw_path.is_dir():
        raise FileNotFoundError(f"Data directory does not exist: '{data_path_or_model}' (resolved to '{raw_path}')")

    found_files: List[Path] = []
    if stage == STAGE_OPTIMIZE:
        for ext in ["*.json", "*.jsonl"]:
            for f in sorted(raw_path.rglob(ext)):
                if f.is_file() and "raw" not in f.parts and f not in found_files:
                    if not any(f.name.endswith(s) for s in [".chk", ".pth", ".pt", "steps_cache.json", "options.json", "model-params.json"]):
                        found_files.append(f)
    else:
        for ext in ["combined_*.txt", "*.txt"]:
            for f in sorted(raw_path.rglob(ext)):
                if f.is_file() and "raw" not in f.parts and f not in found_files:
                    found_files.append(f)

    if not found_files:
        raise FileNotFoundError(f"No valid dataset files found for stage '{stage}' in: '{raw_path}'")

    return sorted(found_files)

