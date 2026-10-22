import gc
import json
import os
import sys
import tempfile
import time
import warnings
import duckdb
import requests
from pathlib import Path
from typing import Any, Callable, Dict, Iterator, List, Optional
from huggingface_hub.utils import logging as hf_logging


PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from gptutils.consoleutils import print, create_progress_bar
from gptio.pathutil import (
    resolve_path,
    TARGET_DATA,
    STAGE_TRAIN,
    STAGE_TUNE,
    STAGE_OPTIMIZE,
)
from dataset.registry import DATASET_REGISTRY, find_dataset_entry
from dataset.cleanup import clean_standard_entry


# Suppress Hugging Face Windows symlink & unauthenticated warnings
hf_logging.set_verbosity_error()
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["HF_HUB_DISABLE_IMPLICIT_TOKEN"] = "1"
warnings.filterwarnings("ignore", category=UserWarning, module="huggingface_hub")
warnings.filterwarnings("ignore", message=".*symlink.*")
warnings.filterwarnings("ignore", message=".*unauthenticated.*")


# ==============================================================================
# Robust Streamer (HF datasets or Direct HTTP/Parquet fallback)
# ==============================================================================

def get_hf_parquet_file_urls(
    hf_repo_id: str,
    hf_name: Optional[str] = None,
    split: str = "train",
) -> List[str]:
    """Queries the Hugging Face API to find all data parquet files in the repository."""
    # 1. Check direct repository siblings first (finds author's complete parquet shards in main branch)
    try:
        api_url = f"https://huggingface.co/api/datasets/{hf_repo_id}"
        resp = requests.get(api_url, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            files = []
            for sibling in data.get("siblings", []):
                rfilename = sibling.get("rfilename", "")
                if rfilename.endswith(".parquet"):
                    if hf_name and hf_name not in rfilename:
                        continue
                    parts = rfilename.replace("\\", "/").split("/")
                    base_name = parts[-1].lower()
                    if split and any(s in base_name for s in ("train", "validation", "test", "val")) and split not in base_name:
                        continue
                    if len(parts) > 2 and parts[-2] != split and parts[-2] in ("train", "validation", "test", "val"):
                        continue
                    download_url = f"https://huggingface.co/datasets/{hf_repo_id}/resolve/main/{rfilename}"
                    files.append(download_url)
            if files:
                return files
    except Exception:
        pass

    # 2. Check datasets-server API fallback (finds converted parquet files like refs/convert/parquet)
    try:
        api_url = f"https://datasets-server.huggingface.co/parquet?dataset={hf_repo_id}"
        resp = requests.get(api_url, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            train_files = [f["url"] for f in data.get("parquet_files", []) if f.get("split") == split]
            if train_files:
                if hf_name:
                    filtered = [u for u in train_files if hf_name in u]
                    if filtered:
                        return filtered
                return train_files
            all_files = [f["url"] for f in data.get("parquet_files", [])]
            if all_files:
                return all_files
    except Exception:
        pass

    return []


def iterate_dataset_items(
    hf_path: Optional[str] = None,
    split: str = "train",
    hf_name: Optional[str] = None,
    data_dir: Optional[str] = None,
    data_files: Optional[Any] = None,
    streaming: bool = True,
    external_url: Optional[str] = None,
    on_total: Optional[Callable[[int], None]] = None,
) -> Iterator[Dict[str, Any]]:
    """
    Yields items from the dataset.
    If `external_url` is provided (or `hf_path` is a direct HTTP/file URL), fetches directly via HTTP/JSON.
    Otherwise streams from Hugging Face via datasets library or direct Parquet downloads.
    """
    # 0. Handle external URL or local JSON file path
    data_url = external_url or (hf_path if hf_path and (hf_path.startswith("http://") or hf_path.startswith("https://")) else None)
    if data_url:
        resp = requests.get(data_url, timeout=45)
        resp.raise_for_status()
        if data_url.endswith(".jsonl"):
            for line in resp.iter_lines():
                if line:
                    yield json.loads(line.decode("utf-8"))
        else:
            data = resp.json()
            if on_total:
                if isinstance(data, list):
                    on_total(len(data))
                elif isinstance(data, dict) and "data" in data and isinstance(data["data"], list):
                    on_total(len(data["data"]))
            if isinstance(data, list):
                for item in data:
                    yield item
            elif isinstance(data, dict):
                if "data" in data and isinstance(data["data"], list):
                    for item in data["data"]:
                        yield item
                else:
                    yield data
        return

    if hf_path and os.path.exists(hf_path) and (hf_path.endswith(".json") or hf_path.endswith(".jsonl")):
        with open(hf_path, "r", encoding="utf-8") as f:
            if hf_path.endswith(".jsonl"):
                for line in f:
                    if line.strip():
                        yield json.loads(line)
            else:
                data = json.load(f)
                if on_total:
                    if isinstance(data, list):
                        on_total(len(data))
                    elif isinstance(data, dict) and "data" in data and isinstance(data["data"], list):
                        on_total(len(data["data"]))
                if isinstance(data, list):
                    for item in data:
                        yield item
                elif isinstance(data, dict):
                    if "data" in data and isinstance(data["data"], list):
                        for item in data["data"]:
                            yield item
                    else:
                        yield data
        return

    if not hf_path:
        raise ValueError("Neither Hugging Face repository ('hf_path') nor external URL ('external_url') was provided.")

    # 1. Attempt Hugging Face datasets library
    try:
        from datasets import load_dataset
        use_streaming = streaming
        if data_files and isinstance(data_files, str) and data_files.endswith(".json"):
            use_streaming = False
        kwargs = {"split": split, "streaming": use_streaming, "trust_remote_code": True}
        if hf_name:
            kwargs["name"] = hf_name
        if data_dir:
            kwargs["data_dir"] = data_dir
        if data_files:
            kwargs["data_files"] = data_files
        try:
            ds = load_dataset(hf_path, **kwargs)
        except TypeError:
            kwargs.pop("trust_remote_code", None)
            ds = load_dataset(hf_path, **kwargs)
        except Exception:
            if kwargs.get("streaming"):
                kwargs["streaming"] = False
                kwargs.pop("trust_remote_code", None)
                ds = load_dataset(hf_path, **kwargs)
            else:
                raise
        if on_total:
            if hasattr(ds, "__len__"):
                try:
                    on_total(len(ds))
                except Exception:
                    pass
            elif hasattr(ds, "info") and ds.info and hasattr(ds.info, "splits") and ds.info.splits:
                if split in ds.info.splits and ds.info.splits[split].num_examples:
                    on_total(ds.info.splits[split].num_examples)
        for item in ds:
            yield item
        return
    except Exception as e:
        print(f"[Notice] Hugging Face datasets module notice ({e}). Using direct HTTP/Parquet fallback...")

    # 2. Fallback: Direct Parquet streaming via pandas
    try:
        import pandas as pd
    except ImportError:
        print("[ERROR] Neither 'datasets' nor 'pandas' is available.")
        sys.exit(1)

    parquet_urls = get_hf_parquet_file_urls(hf_path, hf_name=hf_name, split=split)
    if not parquet_urls:
        if data_files and isinstance(data_files, str) and (data_files.endswith(".json") or data_files.endswith(".jsonl")):
            file_url = f"https://huggingface.co/datasets/{hf_path}/resolve/main/{data_files}"
            for item in iterate_dataset_items(external_url=file_url, on_total=on_total):
                yield item
            return
        raise ValueError(f"No parquet files found on Hugging Face for repo: {hf_path}")

    print(f"Found {len(parquet_urls)} data shard(s) on Hugging Face. Streaming shards...")
    for shard_idx, url in enumerate(parquet_urls, 1):
        print(f"  [Shard {shard_idx}/{len(parquet_urls)}] Downloading & reading shard...")
        try:
            df = None
            try:
                df = pd.read_parquet(url)
            except Exception:
                df = None

            nested_cols = [c for c in ("messages", "conversations", "conversation", "data") if c in df.columns] if df is not None else []
            if df is None or (len(df) > 0 and nested_cols and any(df[c].dropna().empty for c in nested_cols)):
                resp = requests.get(url, stream=True)
                with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as tf:
                    for chunk in resp.iter_content(chunk_size=1024 * 1024):
                        tf.write(chunk)
                    tmp_p = tf.name
                try:
                    clean_path = tmp_p.replace(os.sep, "/")
                    df = duckdb.query(f"SELECT * FROM read_parquet('{clean_path}')").df()
                finally:
                    if os.path.exists(tmp_p):
                        os.remove(tmp_p)

            for _, row in df.iterrows():
                d = row.to_dict()
                for c in ("messages", "conversations", "conversation", "data"):
                    if c in d and hasattr(d[c], "__iter__") and not isinstance(d[c], (str, dict)):
                        d[c] = list(d[c])
                yield d
        except Exception as err:
            print(f"  [Warning] Failed to read shard {shard_idx}: {err}")


# ==============================================================================
# Core Dataset Downloader & Preparer
# ==============================================================================

def check_dataset_exists(
    dataset_key: str = "",
    model_name: str = "",
    models_base_dir: str = "",
    dataset_purpose: Optional[str] = None,
) -> Optional[Path]:
    """
    Checks if a dataset subfolder already exists under the model's data directory.
    If dataset_purpose is specified (train, tune, optimize), checks that specific stage folder.
    Otherwise, checks across all stages (Tuning, Training, Optimizing).
    Returns the Path to the existing dataset directory if found, otherwise None.
    """
    if not model_name or not dataset_key:
        return None

    dataset_key = dataset_key.lower().strip()
    found_purpose, found_info = find_dataset_entry(dataset_key, purpose=dataset_purpose)
    if found_info is not None:
        dataset_name = dataset_key
        effective_purpose = dataset_purpose or found_purpose or STAGE_TRAIN
    else:
        if dataset_key.startswith("http://") or dataset_key.startswith("https://"):
            dataset_name = "custom_url_dataset"
        else:
            dataset_name = dataset_key.replace("/", "_")
        effective_purpose = dataset_purpose or STAGE_TRAIN

    stages_to_check = [effective_purpose] if dataset_purpose else [effective_purpose, STAGE_TUNE, STAGE_TRAIN, STAGE_OPTIMIZE]
    for stage_cand in stages_to_check:
        if not stage_cand:
            continue
        cand_dir = resolve_path(model_name, TARGET_DATA, stage=stage_cand, models_dir=models_base_dir or "bin") / dataset_name
        if cand_dir.exists():
            return cand_dir
    return None


def download_and_prepare_dataset(
    dataset_key: str = "",
    model_name: str = "",
    models_base_dir: str = "",
    dataset_purpose: Optional[str] = None,
    max_size_mb: int = 0,
    limit: Optional[int] = None,
    separator: str = "",
    save_raw: bool = False,
    streaming: bool = True,
) -> List[str]:
    """
    Downloads dataset from Hugging Face or External URL, cleans and combines into ready-to-train
    files in the target directory: [models_base_dir]/[model_name]/data/[dataset_purpose]/[dataset_name]
    """
    dataset_key = dataset_key.lower().strip()
    found_purpose, found_info = find_dataset_entry(dataset_key, purpose=dataset_purpose)

    if found_info is not None:
        info = found_info
        dataset_name = dataset_key
        effective_purpose = dataset_purpose or found_purpose or STAGE_TRAIN
    else:
        if dataset_key.startswith("http://") or dataset_key.startswith("https://"):
            info = {
                "hf_path": "",
                "external_url": dataset_key,
                "split": "train",
                "description": f"Custom External URL dataset: {dataset_key}",
                "cleaner": clean_standard_entry,
            }
            dataset_name = "custom_url_dataset"
        else:
            info = {
                "hf_path": dataset_key,
                "split": "train",
                "description": f"Custom Hugging Face dataset: {dataset_key}",
                "cleaner": clean_standard_entry,
            }
            dataset_name = dataset_key.replace("/", "_")

        if dataset_purpose:
            effective_purpose = dataset_purpose
        elif info.get("format") == "json" or "Direct Preference Optimization (DPO)" in info.get("category", ""):
            effective_purpose = STAGE_OPTIMIZE
        elif "Instruction" in info.get("category", "") or "SFT" in info.get("category", ""):
            effective_purpose = STAGE_TUNE
        else:
            effective_purpose = STAGE_TRAIN

    existing_dir = check_dataset_exists(
        dataset_key=dataset_key,
        model_name=model_name,
        models_base_dir=models_base_dir,
        dataset_purpose=dataset_purpose,
    )
    if existing_dir is not None:
        print(f"[Warning] Dataset '{dataset_name}' already exists at '{existing_dir}'. Skipping download.")
        return [str(p) for p in existing_dir.glob("*") if p.is_file()]

    target_dir = resolve_path(model_name, TARGET_DATA, stage=effective_purpose, models_dir=models_base_dir or "bin") / dataset_name
    target_dir.mkdir(parents=True, exist_ok=True)

    raw_dir = target_dir / "raw"
    if save_raw:
        raw_dir.mkdir(parents=True, exist_ok=True)

    source_label = info.get("hf_path") or info.get("external_url") or "External URL"
    print("=" * 70)
    print(f"GPT Dataset Downloader & Preparer")
    print(f"  Purpose:     {effective_purpose}")
    print(f"  Dataset:     {dataset_name} ({source_label})")
    print(f"  Target Dir:  {target_dir.resolve()}")
    print(f"  Chunk Size:  {max_size_mb} MB per combined file")
    if limit:
        print(f"  Limit:       {limit} items")
    print("=" * 70)

    cleaner_fn: Callable[[Dict[str, Any]], Optional[Any]] = info.get("cleaner")
    is_json = info.get("format") == "json" or "Direct Preference Optimization (DPO)" in info.get("category", "")

    print("\n[1/2] Streaming, cleaning, and packing dataset into combined training chunks...")
    current_content: List[Any] = []
    current_size_bytes = 0
    file_counter = 1
    processed_count = 0
    valid_count = 0
    target_bytes = max_size_mb * 1024 * 1024
    saved_files: List[str] = []

    progress_bar = create_progress_bar(total=limit, desc="Processing items", unit="it")
    start_time = time.time()

    def flush_chunk():
        nonlocal current_content, current_size_bytes, file_counter, saved_files
        if not current_content:
            return
        if is_json:
            chunk_path = target_dir / f"preference_combined_{file_counter}.json"
            with open(chunk_path, "w", encoding="utf-8") as f:
                json.dump(current_content, f, indent=2)
            size_mb = os.path.getsize(chunk_path) / (1024 * 1024)
            saved_msg = f" -> Saved {chunk_path.name} ({size_mb:.2f} MB with {len(current_content):,} preference pairs)"
        else:
            chunk_path = target_dir / f"combined_{file_counter}.txt"
            joined_text = f"\n{separator}\n".join(current_content)
            with open(chunk_path, "w", encoding="utf-8") as f:
                f.write(joined_text)
            size_mb = os.path.getsize(chunk_path) / (1024 * 1024)
            saved_msg = f" -> Saved {chunk_path.name} ({size_mb:.2f} MB with {len(current_content):,} documents)"
        getattr(progress_bar, "clear", lambda: None)()  # wipe the bar line, print above it, then redraw the bar below
        print(saved_msg)
        getattr(progress_bar, "refresh", lambda: None)()
        saved_files.append(str(chunk_path))
        file_counter += 1
        current_content = []
        current_size_bytes = 0

    def set_total_items(total_count: int) -> None:
        if progress_bar is not None and not limit and total_count > 0:
            progress_bar.total = total_count
            if hasattr(progress_bar, "refresh"):
                progress_bar.refresh()

    def add_item(clean_item: Any) -> bool:
        """Files one cleaned item into the current chunk; returns False once the item limit is reached."""
        nonlocal valid_count, current_size_bytes
        valid_count += 1

        if save_raw:
            raw_ext = "json" if is_json else "txt"
            raw_file = raw_dir / f"doc_{valid_count}.{raw_ext}"
            with open(raw_file, "w", encoding="utf-8") as rf:
                if is_json:
                    json.dump(clean_item, rf, indent=2)
                else:
                    rf.write(clean_item)

        if is_json:
            item_bytes = len(json.dumps(clean_item, ensure_ascii=False).encode("utf-8"))
        else:
            item_bytes = len(clean_item.encode("utf-8"))

        if current_size_bytes + item_bytes > target_bytes and current_content:
            flush_chunk()

        current_content.append(clean_item)
        current_size_bytes += item_bytes
        return not (limit and valid_count >= limit)

    try:
        item_iterator = iterate_dataset_items(
            hf_path=info.get("hf_path"),
            split=info.get("split", "train"),
            hf_name=info.get("hf_name"),
            data_dir=info.get("data_dir"),
            data_files=info.get("data_files"),
            streaming=streaming,
            external_url=info.get("external_url"),
            on_total=set_total_items,
        )

        for item in item_iterator:
            processed_count += 1
            if progress_bar is not None:
                progress_bar.update(1)
            elif processed_count % 100 == 0:
                print(f"  Processed {processed_count} items ({valid_count} valid)...", end="\r")

            clean_item = cleaner_fn(item)
            if clean_item and not add_item(clean_item):
                break
        else:
            # Cleaners that assemble items from several rows (e.g. OpenAssistant conversation trees) hand them over once the stream ends
            for clean_item in (cleaner_fn.flush() if hasattr(cleaner_fn, "flush") else []):
                if clean_item and not add_item(clean_item):
                    break
        # Stopping early leaves pyarrow still reading in the background, which crashes interpreter shutdown: close the stream and let it settle
        item_iterator.close()
        gc.collect()
        time.sleep(1)

    except KeyboardInterrupt:
        print("\n[INFO] Download interrupted by user. Finalizing accumulated chunks...")
    finally:
        if progress_bar is not None:
            progress_bar.close()
        flush_chunk()

    elapsed = time.time() - start_time
    if valid_count == 0:
        if target_dir.exists() and not any(target_dir.iterdir()):
            try:
                target_dir.rmdir()
            except Exception:
                pass
        cleaner_name = cleaner_fn.__name__ if cleaner_fn is not None else "None"
        print("\n" + "=" * 70)
        print(f"[ERROR] Dataset Preparation Failed!")
        print(f"  Total items inspected: {processed_count}")
        print(f"  Valid items saved:     0")
        print(f"  Source:                {source_label}")
        print(f"  Cleaner:               {cleaner_name}")
        print(f"  Reason:                None of the {processed_count:,} items matched the required format for cleaner '{cleaner_name}'.")
        print(f"  Empty directory was cleaned up: {target_dir}")
        print("=" * 70)
        raise ValueError(
            f"Dataset '{dataset_name}' produced 0 valid items out of {processed_count:,} inspected. "
            f"The repository '{source_label}' does not have the expected fields for '{cleaner_name}'."
        )

    print("\n" + "=" * 70)
    print(f"[2/2] Dataset Preparation Complete!")
    print(f"  Total items inspected: {processed_count}")
    print(f"  Valid items saved:     {valid_count}")
    print(f"  Combined files created: {len(saved_files)}")
    print(f"  Directory:             {target_dir.resolve()}")
    print(f"  Time taken:            {elapsed:.1f}s")
    print("=" * 70)
    print(f"\nYou can now start pretraining, instruction tuning, or preference optimization with:")
    print(f"  python train.py    --model_name {model_name}")
    print(f"  python tune.py     --model_name {model_name}")
    print(f"  python optimize.py --model_name {model_name}")

    return saved_files

