# Copyright (c) Sebastian Raschka under Apache License 2.0 (see LICENSE.txt).
# Script to download official pretrained LLM weights (GPT-2, LLaMA-3, Qwen-3/2.5, Gemma) in Pure PyTorch.

import argparse
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
from repos.modelrepo import download_model, list_models
from gptutils.consoleutils import print


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Download pretrained LLM weights (GPT-2, LLaMA-3, Qwen-3/2.5, Gemma) in Pure PyTorch format."
    )
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        default=False,
        help="Display a table of all available pretrained models in the registry."
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gpt2:124M",
        help="Model specifier (e.g. 'gpt2:124M', 'gpt2:1.5B', 'llama3.2:1B', 'qwen3:0.6B', 'gemma2:2B')."
    )
    parser.add_argument(
        "--models_dir",
        type=str,
        default="bin",
        help="Base folder to store downloaded models (e.g. models/gpt2-124M)."
    )

    args = parser.parse_args()

    if args.list:
        list_models()
        return

    try:
        download_model(args.model, models_dir=args.models_dir)
    except Exception as e:
        print(f"\n[gptdownload] Error: {e}")
        exit(1)


if __name__ == "__main__":
    main()
