import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from argsutil import ModelArgs, TrainingArgs
from gptio.pathutil import (
    resolve_path,
    TARGET_STEPS_CACHE,
    TARGET_DATA,
    STAGE_TRAIN,
    STAGE_TUNE,
    STAGE_OPTIMIZE,
)
from gptio.fileutil import read_text_file
from gptio.tokencache import load_token_cache
from gptinfer.inference import get_tokenizer
from gptutils.consoleutils import print


def normalize_file_key(file_path: Union[str, Path], base_dir: Optional[Union[str, Path]] = None) -> str:
    """Returns a normalized relative posix path key for a dataset file."""
    p = Path(file_path)
    if base_dir is not None:
        try:
            return p.relative_to(base_dir).as_posix()
        except ValueError:
            pass
    parts = p.parts
    for marker in ("Training", "Tuning", "Optimizing"):
        if marker in parts:
            idx = parts.index(marker)
            if idx + 1 < len(parts):
                return Path(*parts[idx + 1:]).as_posix()
    return p.as_posix()


def calculate_file_steps(
    file_tokens: int,
    batch_size: int,
    context_length: int,
    train_ratio: float = 0.90,
) -> int:
    """Dynamically calculates exact dataloader batch count from token count."""
    train_tokens = int(file_tokens * train_ratio)
    num_sequences = max(0, train_tokens - 1) // context_length
    return max(1, num_sequences // batch_size)


def load_all_steps_cache(args: ModelArgs) -> Dict[str, Dict[str, Any]]:
    """Loads the root steps cache JSON dictionary mapping stage -> stage_cache_data."""
    if not args.model_name:
        return {}
    cache_path = resolve_path(args.model_name, target=TARGET_STEPS_CACHE, models_dir=args.models_base_dir)
    if not cache_path.exists():
        return {}
    try:
        with open(cache_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return {}
        if (
            STAGE_TRAIN not in data
            and STAGE_TUNE not in data
            and STAGE_OPTIMIZE not in data
            and any(k in data for k in ("cached_steps", "files", "batch_size", "file_names"))
        ):
            return {STAGE_TRAIN: data}
        return data
    except Exception as e:
        print(f"[Steps Cache Warning] Failed to read steps cache from '{cache_path}': {e}")
        return {}


def save_all_steps_cache(
    args: ModelArgs,
    data: Dict[str, Dict[str, Any]],
) -> None:
    """Saves the entire multi-stage steps cache dictionary to disk."""
    if not args.model_name:
        return
    cache_path = resolve_path(args.model_name, target=TARGET_STEPS_CACHE, models_dir=args.models_base_dir)
    try:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"[Steps Cache Warning] Failed to save steps cache to '{cache_path}': {e}")


def load_steps_cache(
    args: ModelArgs,
    stage: str = STAGE_TRAIN,
) -> Dict[str, int]:
    """
    Loads cached token counts mapped by normalized file key from data[stage]['files'].
    Automatically migrates legacy step-based caches if encountered.
    Returns Dict[file_key, token_count].
    """
    data = load_all_steps_cache(args)
    stage_data = data.get(stage)
    if not stage_data or not isinstance(stage_data, dict):
        return {}

    files_dict = stage_data.get("files")
    if isinstance(files_dict, dict) and files_dict:
        result = {}
        for k, v in files_dict.items():
            if isinstance(v, int):
                result[normalize_file_key(k)] = v
            elif isinstance(v, dict) and "tokens" in v:
                result[normalize_file_key(k)] = int(v["tokens"])
        return result

    # Legacy migration: if stage_data has "cached_steps" and "file_names"
    cached_steps = stage_data.get("cached_steps")
    file_names = stage_data.get("file_names")
    if isinstance(cached_steps, list) and isinstance(file_names, list) and len(cached_steps) == len(file_names):
        leg_bs = stage_data.get("batch_size", 32)
        leg_ctx = stage_data.get("context_length", 1024)
        leg_ratio = stage_data.get("train_ratio", 0.90)
        # If batch_size was modified to 16 but cached_steps sum reflects 32:
        if leg_bs == 16 and sum(cached_steps) < 250000 and len(cached_steps) > 50:
            leg_bs = 32

        # Match with disk files to get unique relative subpaths instead of colliding base filenames
        data_dir = resolve_path(args.model_name, target=TARGET_DATA, stage=stage, models_dir=args.models_base_dir)
        disk_files = sorted([p for p in data_dir.rglob("*.txt") if p.is_file()]) if data_dir.exists() else []
        if len(disk_files) == len(cached_steps):
            keys = [p.relative_to(data_dir).as_posix() for p in disk_files]
        else:
            keys = [normalize_file_key(fname) for fname in file_names]

        migrated: Dict[str, int] = {}
        for key, steps in zip(keys, cached_steps):
            approx_tokens = int((steps * leg_bs * leg_ctx) / leg_ratio)
            migrated[key] = approx_tokens

        save_steps_cache(args, migrated, stage=stage)
        return migrated

    return {}


def steps_plan_key(args: TrainingArgs, context_length: Optional[int]) -> str:
    """Names a token-budget batching configuration: an exact step count streamed under one is only reusable by sessions with the same one (the token count is reusable by all)."""
    return f"bs{args.batch_size}_len{context_length or 1024}_tr{args.train_ratio}_pad{getattr(args, 'pad_to_multiple_of', None)}"


def load_exact_steps(args: ModelArgs, stage: str, plan_key: str) -> Dict[str, int]:
    """Exact per-file step counts recorded by a full pass with the same batching configuration (data[stage]['files'][file]['steps'][plan_key])."""
    files = (load_all_steps_cache(args).get(stage) or {}).get("files") or {}
    return {normalize_file_key(k): int(v["steps"][plan_key]) for k, v in files.items() if isinstance(v, dict) and plan_key in v.get("steps", {})}


def save_steps_cache(
    args: ModelArgs,
    file_tokens: Dict[str, int],
    stage: str = STAGE_TRAIN,
    file_steps: Optional[Dict[str, int]] = None,
    plan_key: Optional[str] = None,
) -> None:
    """Saves or updates file token counts under data[stage]['files']; with file_steps + plan_key also the exact step counts of that batching configuration."""
    if not args.model_name or not file_tokens:
        return
    data = load_all_steps_cache(args)
    stage_data = data.get(stage, {})
    if not isinstance(stage_data, dict):
        stage_data = {}

    existing_files = stage_data.get("files", {})
    if not isinstance(existing_files, dict):
        existing_files = {}

    for k, v in file_tokens.items():
        key = normalize_file_key(k)
        prev = existing_files.get(key) if isinstance(existing_files.get(key), dict) else {}
        if file_steps is not None and plan_key is not None:
            existing_files[key] = {"tokens": int(v), "steps": {**prev.get("steps", {}), plan_key: int(file_steps[k])}}
        else:
            existing_files[key] = {**prev, "tokens": int(v)} if prev else int(v)

    stage_data["stage"] = stage
    stage_data["files"] = existing_files
    if existing_files:
        stage_data["total_tokens"] = sum(v["tokens"] if isinstance(v, dict) else v for v in existing_files.values())
    data[stage] = stage_data
    save_all_steps_cache(args, data)


def estimate_file_tokens_and_steps(
    file_path: Union[str, Path],
    batch_size: int,
    context_length: int,
    train_ratio: float = 1.0,
    stage: str = STAGE_TRAIN,
) -> Tuple[int, int]:
    """Estimates token count and step count from file size."""
    p = Path(file_path)
    try:
        fsize = p.stat().st_size
        if stage == STAGE_OPTIMIZE:
            est_tokens = max(1, int(fsize * 0.40 / 4))
        else:
            est_tokens = max(1, int(fsize * 0.85 / 4))
        est_steps = max(1, int(est_tokens * train_ratio) // (context_length * batch_size))
        return est_tokens, est_steps
    except Exception:
        return 1000, 10


def init_streaming_dataset_cache(
    files: List[Any],
    args: TrainingArgs,
    context_length: int,
    stage: str,
) -> Tuple[List[Optional[int]], List[Optional[int]], List[int], List[int], List[bool]]:
    """
    Initializes (known_steps, known_tokens, cached_steps, cached_tokens, exact_steps) for a streaming dataset.
    Loads previously cached token counts from disk if available, calculating steps per file from them (exact_steps[i] is True when the
    cache holds the step count a full pass streamed under the same batching configuration, which the token formula only approximates).
    Falls back to running average or estimations for unvisited files.
    """
    total_files = len(files)
    known_steps: List[Optional[int]] = [None] * total_files
    known_tokens: List[Optional[int]] = [None] * total_files
    exact_steps: List[bool] = [False] * total_files
    cached_steps: List[int] = []
    cached_tokens: List[int] = []

    cached_map: Dict[str, int] = {}
    exact_map: Dict[str, int] = {}
    if args.model_name:
        cached_map = load_steps_cache(args, stage=stage)
        exact_map = load_exact_steps(args, stage, steps_plan_key(args, context_length))

    for i, fp in enumerate(files):
        key = normalize_file_key(fp)
        if key in cached_map:
            t = cached_map[key]
            s = exact_map.get(key) or calculate_file_steps(t, batch_size=args.batch_size, context_length=context_length, train_ratio=args.train_ratio)
            known_tokens[i] = t
            known_steps[i] = s
            exact_steps[i] = key in exact_map

    known_t_vals = [t for t in known_tokens if t is not None]
    avg_tokens = (sum(known_t_vals) // len(known_t_vals)) if known_t_vals else None

    for i, fp in enumerate(files):
        if known_tokens[i] is not None:
            cached_tokens.append(known_tokens[i])
            cached_steps.append(known_steps[i])
        elif avg_tokens is not None:
            cached_tokens.append(avg_tokens)
            cached_steps.append(calculate_file_steps(avg_tokens, batch_size=args.batch_size, context_length=context_length, train_ratio=args.train_ratio))
        else:
            est_t, est_s = estimate_file_tokens_and_steps(
                file_path=fp,
                batch_size=args.batch_size,
                context_length=context_length,
                train_ratio=args.train_ratio,
                stage=stage,
            )
            cached_tokens.append(est_t)
            cached_steps.append(est_s)

    return known_steps, known_tokens, cached_steps, cached_tokens, exact_steps


def update_streaming_dataset_cache(
    file_idx: int,
    file_steps: int,
    file_tokens: int,
    files: List[Any],
    known_steps: List[Optional[int]],
    known_tokens: List[Optional[int]],
    args: TrainingArgs,
    context_length: int,
    stage: str,
) -> Tuple[List[int], List[int]]:
    """
    Updates known steps/tokens for the completed file, re-averages remaining unvisited files,
    persists the updated file tokens to disk, and returns the new (cached_steps, cached_tokens).
    """
    known_steps[file_idx] = max(1, file_steps)
    known_tokens[file_idx] = max(1, file_tokens)

    if args.model_name:
        curr_key = normalize_file_key(files[file_idx])
        save_steps_cache(
            args,
            file_tokens={curr_key: file_tokens},
            stage=stage,
        )

    known_t = [t for t in known_tokens if t is not None]
    avg_t = int(round(sum(known_t) / len(known_t)))
    avg_s = calculate_file_steps(avg_t, batch_size=args.batch_size, context_length=context_length, train_ratio=args.train_ratio)

    cached_steps = [known_steps[i] if known_steps[i] is not None else avg_s for i in range(len(files))]
    cached_tokens = [known_tokens[i] if known_tokens[i] is not None else avg_t for i in range(len(files))]

    return cached_steps, cached_tokens


def save_stage_steps_cache(
    args: ModelArgs,
    stage: str,
    total_tokens: int,
    train_tokens: int,
    val_tokens: int,
    file_names: Optional[List[str]] = None,
    extra_metadata: Optional[Dict[str, Any]] = None,
) -> None:
    """Saves dataset-invariant stage tokens and sample counts under data[stage]."""
    if not args.model_name:
        return
    data = load_all_steps_cache(args)
    stage_data: Dict[str, Any] = {
        "stage": stage,
        "total_tokens": total_tokens,
        "train_tokens": train_tokens,
        "val_tokens": val_tokens,
    }
    if file_names:
        stage_data["file_names"] = file_names
    if extra_metadata:
        stage_data.update(extra_metadata)
    data[stage] = stage_data
    save_all_steps_cache(args, data)


def load_stage_steps_cache(
    args: ModelArgs,
    stage: str,
    file_names: Optional[List[str]] = None,
) -> Optional[Dict[str, Any]]:
    """Loads stage-specific steps and token cache from data[stage] if matching settings."""
    data = load_all_steps_cache(args)
    stage_data = data.get(stage)
    if not stage_data or not isinstance(stage_data, dict):
        return None
    if file_names is None or stage_data.get("file_names") == file_names:
        return stage_data
    return None


def precompute_dataset_steps(
    all_files: List[Any],
    args: ModelArgs,
    stage: str = STAGE_TRAIN,
    tokenizer: Optional[Any] = None,
) -> Dict[str, int]:
    """Proactively counts and caches exact tokens across all dataset files before training begins."""
    if tokenizer is None:
        tokenizer = get_tokenizer()

    cached_tokens = load_steps_cache(args, stage=stage) if args.model_name else {}
    total_files = len(all_files)
    print(f"[Precompute] Verifying/calculating exact tokens across {total_files} dataset file(s)...")

    updated = False
    for i, fp in enumerate(all_files, 1):
        key = normalize_file_key(fp)
        if key in cached_tokens:
            continue
        tokens = len(load_token_cache(fp, tokenizer, label=key)) if stage == STAGE_TRAIN else len(tokenizer.encode(read_text_file(fp) + " <|endoftext|> ", allowed_special="all"))
        cached_tokens[key] = tokens
        updated = True
        print(f"  [Precompute] File {i}/{total_files} ({key}): {tokens:,} tokens")

    if updated and args.model_name:
        save_steps_cache(args, cached_tokens, stage=stage)

    return cached_tokens
