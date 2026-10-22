# Copyright (c) Sebastian Raschka under Apache License 2.0 (see LICENSE.txt).
# Script to download and prepare pretraining datasets from Hugging Face for LLM training.

import argparse
import re
from typing import Any, Dict, List, Optional, Tuple
from dataset.registry import (
    DATASET_REGISTRY,
    VALID_CATEGORIES,
    get_all_dataset_keys,
    get_dataset_category,
)
from dataset.download import download_and_prepare_dataset, check_dataset_exists
from gptio.pathutil import STAGE_TRAIN, STAGE_TUNE, STAGE_OPTIMIZE


ORDER_BY_KEY = "key"
ORDER_BY_SOURCE = "source"
ORDER_BY_DOWNLOAD = "download"
ORDER_BY_ON_DISK = "on_disk"
ORDER_BY_TOKENS = "tokens"
ORDER_BY_DESCRIPTION = "description"

ORDER_BY_CHOICES = [
    ORDER_BY_KEY,
    ORDER_BY_SOURCE,
    ORDER_BY_DOWNLOAD,
    ORDER_BY_ON_DISK,
    ORDER_BY_TOKENS,
    ORDER_BY_DESCRIPTION,
]


def _parse_size_to_bytes(size_str: str) -> float:
    if not size_str or size_str == "N/A":
        return -1.0
    s = size_str.replace("~", "").strip()
    m = re.search(r"([\d,.]+)\s*([A-Za-z]+)", s)
    if not m:
        return -1.0
    try:
        val = float(m.group(1).replace(",", ""))
    except ValueError:
        return -1.0
    unit = m.group(2).upper()
    if "KB" in unit:
        return val * 1024
    elif "MB" in unit:
        return val * (1024 ** 2)
    elif "GB" in unit:
        return val * (1024 ** 3)
    elif "TB" in unit:
        return val * (1024 ** 4)
    return val


def _parse_count_to_num(count_str: str) -> float:
    if not count_str or count_str == "N/A":
        return -1.0
    s = count_str.replace("~", "").strip()
    m = re.search(r"([\d,.]+)\s*([BMKbmk])?\b", s)
    if not m:
        return -1.0
    try:
        val = float(m.group(1).replace(",", ""))
    except ValueError:
        return -1.0
    unit = (m.group(2) or "").upper()
    if unit == "B":
        return val * 1_000_000_000
    elif unit == "M":
        return val * 1_000_000
    elif unit == "K":
        return val * 1_000
    return val


def _get_sort_key(entry: Tuple[str, Dict[str, Any]], order_by: str) -> Any:
    k, v = entry
    if order_by == ORDER_BY_KEY:
        return (k.lower(),)
    elif order_by == ORDER_BY_SOURCE:
        hf_disp = v.get("hf_path") or ""
        if v.get("hf_name"):
            hf_disp += f" ({v['hf_name']})"
        elif not hf_disp and (v.get("external_url") or v.get("url")):
            hf_disp = "[External: GitHub]"
        return (hf_disp.lower(), k.lower())
    elif order_by == ORDER_BY_DOWNLOAD:
        return (_parse_size_to_bytes(v.get("download_size", "N/A")), k.lower())
    elif order_by == ORDER_BY_ON_DISK:
        return (_parse_size_to_bytes(v.get("extracted_size", "N/A")), k.lower())
    elif order_by == ORDER_BY_TOKENS:
        return (_parse_count_to_num(v.get("item_count", "N/A")), k.lower())
    elif order_by == ORDER_BY_DESCRIPTION:
        return (v.get("description", "").lower(), k.lower())
    return (k.lower(),)


# ==============================================================================
# CLI Entrypoint
# ==============================================================================

def parse_token_list(raw_input: Any) -> List[str]:
    """
    Parses a single identifier or multiple identifiers provided in formats such as:
    - 'smoltalk'
    - '[smoltalk, ultrachat]'
    - 'smoltalk, ultrachat'
    - ['smoltalk', 'ultrachat']
    - ['[smoltalk,', 'ultrachat]']
    Returns a clean list of unique tokens preserving order.
    """
    if not raw_input:
        return []
    if isinstance(raw_input, (list, tuple)):
        text = " ".join(str(x) for x in raw_input)
    else:
        text = str(raw_input)

    # Replace commas, brackets, braces, parentheses with spaces
    text = re.sub(r"[\[\]\(\)\{\},]", " ", text)
    tokens: List[str] = []
    for token in text.split():
        cleaned = token.strip("'\" \t\r\n")
        if cleaned and cleaned not in tokens:
            tokens.append(cleaned)
    return tokens


def main():
    all_builtin_keys = get_all_dataset_keys()

    parser = argparse.ArgumentParser(
        description="Download and prepare datasets from Hugging Face for GPT training (Pure PyTorch)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--list", action="store_true", help="List all built-in supported datasets and exit")
    parser.add_argument(
        "--dataset",
        nargs="+",
        default=None,
        help=f"Dataset identifier(s). Single (e.g. --dataset smoltalk) or multiple (e.g. --dataset [smoltalk, ultrachat] or --dataset smoltalk ultrachat). Built-ins: {all_builtin_keys} or custom HF repo path",
    )
    parser.add_argument("--purpose", "--dataset_purpose", type=str, choices=[STAGE_TRAIN, STAGE_TUNE, STAGE_OPTIMIZE], default=None, help="Target stage bucket under data/ (train, tune, or optimize). Automatically inferred for built-in datasets.")
    parser.add_argument("--model_name", type=str, help="Target model name to store data under [models_root_dir]/[model_name]/data/[purpose]/[dataset]")
    parser.add_argument("--models_base_dir", type=str, default="bin", help="Root directory for models and datasets")
    parser.add_argument("--max_size_mb", type=int, default=500, help="Maximum size in MB for each combined training text file chunk")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of documents/books to download (useful for quick testing)")
    parser.add_argument("--save_raw", action="store_true", help="Also save individual raw text files under raw/")
    parser.add_argument("--no_streaming", action="store_true", help="Disable streaming mode (downloads whole dataset into HF cache first)")
    parser.add_argument(
        "--order_by",
        type=str,
        choices=ORDER_BY_CHOICES,
        default=None,
        help=f"Sort column for --list subsections ({', '.join(ORDER_BY_CHOICES)})",
    )
    parser.add_argument(
        "--cat_filter",
        nargs="+",
        default=None,
        help=f"Filter --list output by one or more categories ({', '.join(VALID_CATEGORIES)}). Single (e.g. --cat_filter core) or multiple (e.g. --cat_filter [core, math]).",
    )

    args = parser.parse_args()

    if args.order_by and not args.list:
        parser.error("--order_by can only be used in conjunction with --list")

    if args.cat_filter and not args.list:
        parser.error("--cat_filter can only be used in conjunction with --list")

    if args.list:
        filter_cats: Optional[List[str]] = None
        if args.cat_filter:
            parsed_cats = parse_token_list(args.cat_filter)
            if not parsed_cats:
                parser.error("--cat_filter must specify at least one valid category")
            filter_cats = []
            for c in parsed_cats:
                cat_lower = c.lower()
                if cat_lower not in VALID_CATEGORIES:
                    parser.error(f"Invalid category '{c}'. Valid categories are: {', '.join(VALID_CATEGORIES)}")
                if cat_lower not in filter_cats:
                    filter_cats.append(cat_lower)

        print("\n" + "=" * 125)
        header_title = "BUILT-IN DATASET REGISTRY"
        if filter_cats:
            header_title += f" (Category Filter: {', '.join(filter_cats)})"
        print(f"{header_title:^125}")
        print("=" * 125)

        total_shown = 0
        for bucket_name, bucket_datasets in DATASET_REGISTRY.items():
            filtered_datasets: Dict[str, Dict[str, Any]] = {}
            for k, v in bucket_datasets.items():
                if filter_cats:
                    entry_cat = get_dataset_category(k)
                    if entry_cat not in filter_cats:
                        continue
                filtered_datasets[k] = v

            if not filtered_datasets:
                continue

            total_shown += len(filtered_datasets)
            print("\n" + "#" * 125)
            bucket_folder = "Training" if bucket_name == STAGE_TRAIN else ("Tuning" if bucket_name == STAGE_TUNE else "Optimizing")
            print(f"  PURPOSE BUCKET: [{bucket_name.upper()}] (Destination: bin/<model_name>/data/{bucket_folder}/<dataset_name>)")
            print("#" * 125)

            # Group datasets by category inside this purpose bucket
            categories: Dict[str, List[Tuple[str, Dict[str, Any]]]] = {}
            for k, v in filtered_datasets.items():
                cat = v.get("category", "General")
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append((k, v))

            for cat_name, entries in categories.items():
                if args.order_by:
                    entries = sorted(entries, key=lambda entry: _get_sort_key(entry, args.order_by))

                print(f"\n  [{cat_name}]")
                print(f"    {'KEY':<26} {'SOURCE / HF PATH':<50} {'DOWNLOAD':<11} {'ON-DISK':<11} {'TOKENS / ITEMS':<28} {'SUB-CATEGORY'}")
                print(f"    {'-'*26} {'-'*50} {'-'*11} {'-'*11} {'-'*28} {'-'*20}")
                for k, v in entries:
                    hf_disp = v.get("hf_path") or ""
                    if v.get("hf_name"):
                        hf_disp += f" ({v['hf_name']})"
                    elif not hf_disp and (v.get("external_url") or v.get("url")):
                        hf_disp = "[External: GitHub]"

                    scat = v.get("sub_category", "N/A")
                    dl = v.get("download_size", "N/A")
                    raw = v.get("extracted_size", "N/A")
                    cnt = v.get("item_count", "N/A")

                    print(f"    {k:<26} {hf_disp:<50} {dl:<11} {raw:<11} {cnt:<28} {scat}")

        if total_shown == 0 and filter_cats:
            print(f"\n  No datasets found matching category filter: {', '.join(filter_cats)}")

        print("\n" + "=" * 125)
        print("Usage Examples:")
        print("  python download_dataset.py --model_name andres1-s --dataset gutenberg")
        print("  python download_dataset.py --model_name andres1-s --dataset [smoltalk, ultrachat]")
        print("  python download_dataset.py --model_name andres1-s --dataset orca_dpo")
        print("  python download_dataset.py --list --cat_filter core")
        print("  python download_dataset.py --list --cat_filter [core, math]")
        print("=" * 125 + "\n")
        return

    if not args.list:
        if args.model_name is None:
            parser.error("--model_name is required unless --list is specified")

        if not args.dataset:
            parser.error("--dataset is required unless --list is specified")

    dataset_keys = parse_token_list(args.dataset)
    if not dataset_keys:
        parser.error("--dataset must specify at least one valid dataset identifier")

    total_datasets = len(dataset_keys)
    for idx, d_key in enumerate(dataset_keys, 1):
        existing_dir = check_dataset_exists(
            dataset_key=d_key,
            model_name=args.model_name,
            models_base_dir=args.models_base_dir,
            dataset_purpose=args.purpose,
        )
        if existing_dir is not None:
            print(f"[Warning] Dataset '{d_key}' already exists at '{existing_dir}'. Skipping download.")
            continue

        if total_datasets > 1:
            print(f"\n{'='*80}")
            print(f"[{idx}/{total_datasets}] DOWNLOADING DATASET: {d_key}")
            print(f"{'='*80}")

        download_and_prepare_dataset(
            dataset_key=d_key,
            model_name=args.model_name,
            models_base_dir=args.models_base_dir,
            dataset_purpose=args.purpose,
            max_size_mb=args.max_size_mb,
            limit=args.limit,
            separator="<|endoftext|>",
            save_raw=args.save_raw,
            streaming=not args.no_streaming,
        )


if __name__ == "__main__":
    main()
