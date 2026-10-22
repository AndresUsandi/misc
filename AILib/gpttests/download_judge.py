# Copyright (c) Sebastian Raschka under Apache License 2.0 (see LICENSE.txt).
# One-time setup for the content validators in gpttests/data: installs the GPU-matched prebuilt llama-cpp-python CUDA 13 wheel,
# downloads the Gemma 4 E4B judge GGUF into bin/judge, and pre-caches the DeBERTa NLI model.

import argparse
import importlib.util
from pathlib import Path
import subprocess
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import torch
from huggingface_hub import hf_hub_download, snapshot_download

from gpttests.data.modelrefs import JUDGE_DIR, JUDGE_FILENAME, JUDGE_REPO_ID, NLI_MODEL_ID
from gptutils.consoleutils import print

# Prebuilt Windows wheels: official abetlen release with CUDA 13.0 support and AVX2 CPU compatibility.
_CUDA13_WHEEL = "https://github.com/abetlen/llama-cpp-python/releases/download/v0.3.36-cu130/llama_cpp_python-0.3.36-py3-none-win_amd64.whl"
_WHEELS = {
    7: _CUDA13_WHEEL,
    8: _CUDA13_WHEEL,
    9: _CUDA13_WHEEL,
    10: _CUDA13_WHEEL,
    12: _CUDA13_WHEEL,
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Install llama-cpp-python and download the judge / NLI models used by gpttests/data.")
    parser.add_argument("--gpu_index", type=int, default=0, help="CUDA device whose architecture selects the llama-cpp-python wheel.")
    parser.add_argument("--force_wheel", action="store_true", default=False, help="Reinstall the llama-cpp-python wheel even if already importable.")
    args = parser.parse_args()

    if args.force_wheel or importlib.util.find_spec("llama_cpp") is None:
        major, minor = torch.cuda.get_device_capability(args.gpu_index)
        if major == 8 and minor >= 9:
            major = 9
        url = _WHEELS.get(major)
        if url is None:
            raise SystemExit(f"[judge] No prebuilt llama-cpp-python wheel for compute capability {major}.{minor}; build from source (see llama-cpp-python docs).")
        print(f"[judge] Installing llama-cpp-python wheel for sm_{major}{minor}: {url}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--force-reinstall", "--no-deps", url])
    else:
        print("[judge] llama-cpp-python already installed.")

    print(f"[judge] Downloading {JUDGE_REPO_ID}/{JUDGE_FILENAME} -> {JUDGE_DIR}")
    hf_hub_download(JUDGE_REPO_ID, JUDGE_FILENAME, local_dir=str(JUDGE_DIR))
    print(f"[judge] Caching NLI model {NLI_MODEL_ID}")
    snapshot_download(NLI_MODEL_ID, allow_patterns=["*.json", "*.model", "model.safetensors"])
    print("[judge] Done.")


if __name__ == "__main__":
    main()
