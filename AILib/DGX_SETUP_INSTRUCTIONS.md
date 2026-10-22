# AILib on NVIDIA DGX Spark — Setup Guide

**Tested baseline:** NVIDIA DGX Spark (GB10, ARM64), Ubuntu 24.04.5 LTS, October 2026.  
**Purpose:** Prepare a Spark for AILib development, GPU training, and the repository's end-to-end tests.  
**Approach:** Use NVIDIA's existing Spark driver/CUDA installation, one shared Python virtual environment, and the specific PyTorch / TorchAO / cuBLAS combination that worked on the reference Spark.

> **Validation status:** On the reference DGX Spark, the packages installed, imported, CUDA detected the GB10, and a GPU matrix multiplication completed successfully. A complete AILib end-to-end training run and GB10 FP8 training were **not yet confirmed** when this guide was written. Treat those tests as required validation on your own machine, not as known passes.

## 0. Before you begin

This guide assumes:

- An NVIDIA DGX Spark running NVIDIA's supported Ubuntu software image (the reference machine used **Ubuntu 24.04.5 LTS, `aarch64`**).
- Internet access; terminal access (local or SSH); a user with `sudo` privileges.
- Access to the **AILib** Git repository, including any private-repository permissions.
- Enough free disk space for Python packages, datasets, models, and checkpoints.

**Do not replace the NVIDIA driver, reinstall CUDA, install an x86-64 CUDA build, or modify system CUDA symlinks to follow this guide.** The reference Spark already had a working driver and CUDA toolkit. PyTorch wheels bring their own runtime libraries; the system toolkit and driver remain separate.

Check the starting environment:

```bash
uname -m
lsb_release -ds
nvidia-smi
nvcc --version
python3 --version
```

Reference output/versions:

| Item | Reference DGX Spark |
| --- | --- |
| CPU architecture | `aarch64` (ARM64) |
| OS | Ubuntu 24.04.5 LTS |
| GPU | NVIDIA GB10, compute capability 12.1 (`sm_121`) |
| NVIDIA driver | `580.178.04` |
| CUDA toolkit (`nvcc`) | `13.0.88` |
| CUDA reported by `nvidia-smi` | 13.0 |
| Python | 3.12.3 |

The numbers above document **one working baseline**, not minimum requirements for every future AILib release. If `nvidia-smi` fails, fix the base DGX Spark software installation first. Do not attempt to solve a driver failure by changing Python packages.

## 1. Install Ubuntu development tools

```bash
sudo apt update
sudo apt upgrade -y

sudo apt install -y \
  build-essential git gh curl wget ca-certificates pkg-config \
  cmake ninja-build python3 python3-pip python3-venv python3-dev \
  htop tmux openssh-server ethtool unzip zip
```

If a system update changes the kernel or NVIDIA components, **reboot before continuing**, then recheck `nvidia-smi` and `nvcc --version`.

Optional: enable SSH so you can develop remotely (for example, from VS Code/Cursor):

```bash
sudo systemctl enable --now ssh
systemctl is-active ssh
hostname -I
```

On another computer, connect using `ssh <linux-username>@<spark-ip-address>` (substitute your own user and address). Ensure the Spark is reachable on your trusted network before exposing SSH beyond it.

## 2. Clone AILib

If you have **already cloned AILib**, simply `cd` into the repository and skip the clone instructions. Otherwise, obtain the actual HTTPS or SSH clone URL from the repository owner. The repository may be private.

Example layout (a directory convention, not a requirement):

```bash
mkdir -p ~/GitHub/MachineLarning
cd ~/GitHub/MachineLarning

# Paste the clone command supplied by the repository owner here.
# For example: git clone <the-actual-AILib-URL> AILib

cd AILib
pwd
```

All remaining commands that mention repository files assume **you are in the AILib repository root**.

> Note: the `MachineLarning` spelling is deliberate in the reference machine's path. Your checkout may live elsewhere. **Do not hardcode another person's Linux username or home directory.**

## 3. Create one shared Python environment

The reference setup uses a single venv at `~/ai-env` for all AILib AI work, rather than a separate venv per project.

```bash
python3 -m venv ~/ai-env
source ~/ai-env/bin/activate
python -m pip install --upgrade pip setuptools wheel
```

Verify:

```bash
which python
python --version
echo "$VIRTUAL_ENV"
```

Expected: `which python` points to **your own** `/home/<user>/ai-env/bin/python` and `VIRTUAL_ENV` points to your home directory's `ai-env`.

### Activate the environment automatically in new shells

Append this block to `~/.bashrc` **once**:

```bash
cat >> ~/.bashrc <<'EOF'

# Automatically activate the shared AI Python environment
if [[ -f "$HOME/ai-env/bin/activate" ]]; then
    source "$HOME/ai-env/bin/activate"
fi
EOF
```

Apply it to your current Bash session:

```bash
source ~/.bashrc
which python
```

New interactive Bash/SSH sessions should automatically show `(ai-env)` in the prompt. Avoid adding the block repeatedly.

## 4. Install PyTorch with CUDA 13.0 for ARM64

**Install PyTorch before AILib's general dependencies.** This step successfully installed PyTorch **2.14.1+cu130** on the reference Spark:

```bash
python -m pip install torch --index-url https://download.pytorch.org/whl/cu130
```

Verify the actual version and GPU detection; wheel availability and default versions can change over time:

```bash
python - <<'PY'
import platform
import torch

print("Architecture:", platform.machine())
print("PyTorch:", torch.__version__)
print("PyTorch CUDA runtime:", torch.version.cuda)
print("CUDA available:", torch.cuda.is_available())
if torch.cuda.is_available():
    print("GPU:", torch.cuda.get_device_name(0))
    print("Compute capability:", torch.cuda.get_device_capability(0))
PY
```

**Reference values:** PyTorch `2.14.1+cu130`, CUDA runtime `13.0`, `CUDA available: True`, GPU `NVIDIA GB10`, compute capability `(12, 1)`.

If the installed PyTorch version differs, **do not assume all later compatibility steps were validated with that version**. In particular, the TorchAO and cuBLAS versions below describe the known-tested combination.

## 5. Install AILib's Python dependencies

The repository should contain `requirements-spark.txt`, which intentionally **does not list `torch`, `torchao`, or a cuBLAS override**. Those are installed separately to avoid unintended CUDA dependency replacement.

From the repository root:

```bash
python -m pip install -r requirements-spark.txt
```

For reference, the dependency file used on the original Spark contained:

```text
--extra-index-url https://download.pytorch.org/whl/cu130
tiktoken>=0.7.0
datasets>=2.18.0
huggingface_hub>=0.20.0
tokenizers>=0.19.0
gguf>=0.19.0
pyarrow>=15.0.0
symspellpy>=6.7.0
pandas>=2.0.0
duckdb>=1.0.0
fastparquet>=2024.0.0
matplotlib>=3.7.0
tqdm>=4.66.0
requests>=2.31.0
transformers>=4.57.0
sentencepiece>=0.2.0
protobuf>=4.0
diskcache>=5.6.1
```

If the file is missing from your checkout, ask the repository maintainer to commit it. For a temporary fallback, copy the above lines into a local `requirements-spark.txt` **without overwriting an existing repo-managed file**, then rerun the install command. These ranges allow newer releases; for strict reproducibility, capture and share a tested lock file separately.

## 6. Install TorchAO without modifying the PyTorch stack

The reference Spark successfully imported **TorchAO 0.18.0** with PyTorch 2.14.1+cu130:

```bash
python -m pip install --no-deps "torchao==0.18.0"
```

`--no-deps` is intentional: it avoids pip replacing the working PyTorch/CUDA packages while resolving TorchAO's dependencies. The combination must still be tested in actual training code.

## 7. Apply the cuBLAS 13.2.2.2 override

**Do not omit this step when reproducing the reference setup.** The AILib development machines previously encountered an FP8 cuBLAS failure in a **multi-GPU RTX 5070 Ti** configuration with `nvidia-cublas==13.1.1.3`. The separate override to **13.2.2.2** resolved that issue there.

The reference Spark initially reported:

- `cuda-toolkit`: `13.0.3.0`
- `nvidia-cublas`: `13.1.1.3`

Then it successfully installed and ran basic CUDA matrix multiplication with:

```bash
python -m pip install --no-deps "nvidia-cublas==13.2.2.2"
```

**Why separate?** The CUDA package dependency pins may still describe the older cuBLAS package. Installing the override separately with `--no-deps` avoids forcing pip to re-resolve or replace the PyTorch stack. A package being installable and passing a matrix-multiplication smoke test **does not prove** every FP8 kernel works on GB10. The original bug involved multiple GPUs; Spark has a single GB10 and might not require this workaround independently. We retain the override here to reproduce the actual reference environment.

**Do not install any x86-64 wheel manually** if pip reports the requested package unavailable for ARM64. Record the error and compare your Spark's Python/CUDA build with the reference.

## 8. Verify the complete installation

Run this smoke test from inside `(ai-env)`:

```bash
python - <<'PY'
import importlib.metadata as m
import platform
import torch
import torchao

print("Architecture:", platform.machine())
for package in ["torch", "torchao", "cuda-toolkit", "nvidia-cublas"]:
    try:
        print(f"{package}: {m.version(package)}")
    except m.PackageNotFoundError:
        print(f"{package}: NOT INSTALLED")

print("CUDA runtime:", torch.version.cuda)
print("CUDA available:", torch.cuda.is_available())
assert torch.cuda.is_available(), "CUDA is not available to PyTorch"
print("GPU:", torch.cuda.get_device_name(0))
print("Capability:", torch.cuda.get_device_capability(0))

x = torch.randn(1024, 1024, device="cuda")
y = x @ x
torch.cuda.synchronize()
print("CUDA matrix multiplication: SUCCESS")
PY
```

Expected package versions **on the reference Spark**:

```text
torch: 2.14.1+cu130
torchao: 0.18.0
cuda-toolkit: 13.0.3.0
nvidia-cublas: 13.2.2.2
CUDA runtime: 13.0
CUDA available: True
GPU: NVIDIA GB10
Capability: (12, 1)
CUDA matrix multiplication: SUCCESS
```

The `torch.utils._pytree` warning mentioning `KernelPreference` / `register_constant()` was observed during TorchAO import. It is a **deprecation warning**, not a failed test.

Then verify other imports:

```bash
python - <<'PY'
import torch, torchao, numpy, datasets, transformers, tiktoken, gguf, pandas, duckdb
print("Core AILib dependencies: IMPORT SUCCESS")
print("NumPy:", numpy.__version__)
print("Transformers:", transformers.__version__)
PY
```

The reference machine had NumPy `2.5.4` and Transformers `5.20.2` at the time of installation. Import success alone is not a guarantee of API compatibility with the application.

### About `pip check` on Spark

```bash
python -m pip check
```

The reference Spark printed:

```text
nvidia-cusparselt-cu13 0.8.1 is not supported on this platform
```

Inspection showed PyTorch requires `nvidia-cusparselt-cu13==0.8.1` for Linux, but `pip check` flagged the installed package on this ARM64 platform. **The reason for the platform warning was not fully resolved.** Ordinary CUDA matrix multiplication passed despite it. Do **not** uninstall cuSPARSELt merely to silence the warning; it is listed as required by PyTorch. Investigate further if an AILib training run fails with a related error.

## 9. Validate AILib itself

From the repository root:

```bash
python train.py --help
```

On the reference Spark, this displayed the full Unified GPT Training/Fine-Tuning/Optimization command-line interface successfully, demonstrating that the training entry point and its imports could initialize.

Next, inspect the available end-to-end tests:

```bash
ls -lh gpttests/e2e/
```

The first recommended test is `test-basic.py`. It exercises pretraining, fine-tuning, DPO optimization, inference, checkpoint transitions, and log assertions:

```bash
python gpttests/e2e/test-basic.py
```

**Before running:** the E2E helper calls `t.clean()` at the start and end. Verify its cleanup scope if you have existing model/checkpoint data you need to preserve:

```bash
sed -n '1,220p' gpttests/e2e/_e2e.py
```

Also ensure the test model's required `bin/...` configuration and dataset files are actually present. The reference development setup has model and dataset assets under `bin/<model-name>/`; a fresh Git clone may **not** include ignored or separately copied assets.

After the basic test passes, candidates for more specific testing include:

```bash
python gpttests/e2e/test-muon-bf16.py
python gpttests/e2e/test-precision-fp8.py
```

Inspect each test's prerequisites and assertions before running it. **FP8 is not yet confirmed working on the reference GB10;** its test is specifically intended to establish that. Muon BF16 tests may include hardware-specific memory assertions. Do not run the full `run_all_tests.py` suite blindly: several tests target **multiple discrete GPUs**, whereas DGX Spark exposes **one** GB10.

### Monitor GPU activity during a test

In a second terminal or SSH session:

```bash
watch -n 1 nvidia-smi
```

To stop `watch`, press **Ctrl+C**. DGX Spark uses unified system/GPU memory, so memory behavior may differ from discrete RTX cards.

## 10. Common issues and checks

| Symptom | What to check |
| --- | --- |
| `nvidia-smi` fails | Stop: confirm the NVIDIA DGX Spark driver/image before touching Python packages. |
| `torch.cuda.is_available()` returns `False` | Confirm you activated `~/ai-env`, installed the correct ARM64 CUDA PyTorch wheel, and can run `nvidia-smi`. |
| `nvcc` not found | Check whether the NVIDIA CUDA toolkit is installed and on `PATH`; do not guess an installation command or alter the driver without checking the Spark software image. |
| `torchao` fails to import | Confirm `torch==2.14.1+cu130` and `torchao==0.18.0` (reference versions); capture the exact traceback. |
| `pip check` reports cuSPARSELt unsupported | See §8. This was observed on the reference ARM64 machine even while basic CUDA computation worked. |
| Test fails due to missing model/data paths | Check `bin/<test-model>/` contents; Git-ignored assets may need to be obtained separately. |
| FP8 / Triton / compile fails | Capture the full error, confirm GPU capability `(12, 1)`, and verify torch/TorchAO/cuBLAS versions. A basic CUDA pass does not validate compiled FP8 kernels. |
| Out of memory | Stop any concurrent inference server such as vLLM; reduce the test batch size only if doing so does not invalidate its assertions. |
| Unexpected package upgrades | Avoid installing unreviewed PyTorch/TorchAO dependencies into the shared venv; capture installed versions before changing it. |

## 11. Capture the working environment

After all desired E2E tests pass, save an environment snapshot for repeatability:

```bash
python -m pip freeze > requirements-spark-locked.txt
python -m pip list --format=columns
nvidia-smi
```

The resulting `requirements-spark-locked.txt` is a **record of the reference environment**, not necessarily a safe one-command installer: it can include platform-specific CUDA packages and the intentional cuBLAS pin override. Prefer this guide's ordered installation steps for a new Spark, then compare snapshots. Commit the lock file only if your project wants to maintain it.

---

## Quick command checklist

Run these only after checking the prerequisites and being in the appropriate directory:

```bash
# Ubuntu development tools
sudo apt update
sudo apt install -y build-essential git gh curl wget ca-certificates pkg-config cmake ninja-build python3 python3-pip python3-venv python3-dev htop tmux openssh-server ethtool unzip zip

# Shared Python environment
python3 -m venv ~/ai-env
source ~/ai-env/bin/activate
python -m pip install --upgrade pip setuptools wheel

# In AILib repository root: CUDA-enabled PyTorch, AILib deps, TorchAO, cuBLAS override
python -m pip install torch --index-url https://download.pytorch.org/whl/cu130
python -m pip install -r requirements-spark.txt
python -m pip install --no-deps "torchao==0.18.0"
python -m pip install --no-deps "nvidia-cublas==13.2.2.2"

# Validation
python train.py --help
python gpttests/e2e/test-basic.py
```

**Maintainer checklist before sharing AILib:** commit this guide and `requirements-spark.txt`; confirm required test assets are included or explain how to obtain them; give collaborators repository access; update the tested-version table when a newer combination passes the E2E suite.
