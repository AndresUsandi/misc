# Unified GPT Training, Fine-Tuning & Optimization Arguments Guide

This document provides a comprehensive technical reference for every command-line argument and configuration option in the unified orchestrator (`train.py`). All arguments can be specified on the command line or persisted in stage-specific JSON configuration files (`<model_name>.options-train.json`, `<model_name>.options-tune.json`, `<model_name>.options-optimize.json`).

---

## Table of Contents

1. [Primary Process Selector](#1-primary-process-selector)
   - [`--training_process`](#training_process)
2. [Model & Path Identification](#2-model--path-identification)
   - [`--model_name`](#model_name)
   - [`--models_base_dir`](#models_base_dir)
   - [`--resume`](#resume)
3. [Hyperparameters & Scheduling](#3-hyperparameters--scheduling)
   - [`--batch_size`](#batch_size)
   - [`--accum_steps`](#accum_steps)
   - [`--num_epochs`](#num_epochs)
   - [`--learning_rate`](#learning_rate)
   - [`--min_lr`](#min_lr)
   - [`--warmup_steps`](#warmup_steps)
   - [`--warmup_ratio`](#warmup_ratio)
   - [`--weight_decay`](#weight_decay)
   - [`--eval_freq`](#eval_freq)
   - [`--eval_iter`](#eval_iter)
   - [`--save_interval`](#save_interval)
   - [`--step_limit`](#step_limit)
4. [Hardware, Multi-GPU & Precision](#4-hardware-multi-gpu--precision)
   - [`--device`](#device)
   - [`--pol_device`](#pol_device)
   - [`--ref_device`](#ref_device)
   - [`--single_gpu`](#single_gpu)
   - [`--gpu_index`](#gpu_index)
   - [`--precision`](#precision)
   - [`--compile`](#compile)
   - [`--coordinate_descent_tuning`](#coordinate_descent_tuning)
   - [`--activation_checkpointing`](#activation_checkpointing)
   - [`--freeze_embeddings`](#freeze_embeddings)
   - [`--multi_gpu_strategy`](#multi_gpu_strategy)
   - [`--multi_stage_micro_batching`](#multi_stage_micro_batching)
   - [`--even_layers`](#even_layers)
   - [`--1f1b`](#1f1b)
   - [`--async_pcie`](#async_pcie)
5. [Optimizers](#5-optimizers)
   - [`--use_muon`](#use_muon)
   - [`--muon_lr`](#muon_lr)
6. [Dataset, Sequence & Loss Computation](#6-dataset-sequence--loss-computation)
   - [`--override_data_folder`](#override_data_folder)
   - [`--train_ratio`](#train_ratio)
   - [`--test_ratio`](#test_ratio)
   - [`--max_length`](#max_length)
   - [`--pad_to_multiple_of`](#pad_to_multiple_of)
   - [`--chunk_size`](#chunk_size)
   - [`--recompute_lmhead`](#recompute_lmhead)
   - [`--vocab_padded`](#vocab_padded)
   - [`--mask_prompt`](#mask_prompt)
   - [`--precompute_total_steps`](#precompute_total_steps)
7. [Inference, Evaluation & Debugging](#7-inference-evaluation--debugging)
   - [`--temperature`](#temperature)
   - [`--top_k`](#top_k)
   - [`--chat`](#chat)
   - [`--save_timeout`](#save_timeout)
   - [`--verbose`](#verbose)
   - [`--test_mode`](#test_mode)
   - [`--beta`](#beta)

---

<a id="1-primary-process-selector"></a>
## 1. Primary Process Selector

<a id="training_process"></a>
<a id="--training_process"></a>
### `--training_process`
- **CLI Flag**: `--training_process`
- **JSON Key**: `training_process`
- **Type**: `str`
- **Choices**: `Training`, `Fine-Tuning`, `Optimizing`
- **Required**: Yes
- **Default**: None

#### In-Depth Explanation
Selects which stage of the LLM lifecycle pipeline to execute:
1. **`Training`** (Pretraining): Next-token prediction across unannotated textual corpora (Gutenberg, Cosmopedia, Wikipedia, etc.). Initializes embeddings, transformer blocks, and heads from random normal initialization, running the fully optimized Muon/AdamW pretraining loop.
2. **`Fine-Tuning`** (Supervised Fine-Tuning / SFT): Instruction-following adaptation using prompt/response pairs (Alpaca, Dolly, No Robots, OpenHermes). Automatically applies prompt masking (`-100` cross-entropy targets) so loss is strictly evaluated and backpropagated on assistant answers. Resumes from the pretraining checkpoint (`.trn.chk` or base weights).
3. **`Optimizing`** (Direct Preference Optimization / DPO): Post-training alignment using pairwise preferences (chosen vs. rejected responses). Jointly coordinates a trainable policy model and a frozen reference model to optimize implicit reward margins without separate reward model training. Resumes from the SFT checkpoint (`.sft.chk`).

#### Tradeoffs & Best Practices
Always follow the natural order of LLM training: `Training` -> `Fine-Tuning` -> `Optimizing`. Each process stage resolves its own options file (`.options-train.json`, `.options-tune.json`, `.options-optimize.json`) and writes to dedicated checkpoint types (`.trn.chk`, `.sft.chk`, `.dpo.chk`).

---

<a id="2-model--path-identification"></a>
## 2. Model & Path Identification

<a id="model_name"></a>
<a id="--model_name"></a>
### `--model_name`
- **CLI Flag**: `--model_name`
- **JSON Key**: `model_name`
- **Type**: `str`
- **Required**: Yes
- **Default**: None

#### In-Depth Explanation
The canonical identifier for the model architecture and storage directory (e.g. `andres1xs-150M`, `andres1-1B`). Resolves the model folder at `<models_base_dir>/<model_name>/`, loading the architecture parameters from `<model_name>.model-params.json` and stage options from `<model_name>.options-<stage>.json`.

#### Tokenizer (`"tokenizer"` key in `model-params.json`)
A model may declare its own tokenizer in `<model_name>.model-params.json`; it is part of the model's identity (the weights are meaningless with a different vocabulary), so it lives next to `vocab_size` rather than in the per-stage options files, and `train.py` and `infer.py` always agree on it. Accepted values:
- **absent or `"gpt2"`**: the built-in GPT-2 encoding (50,257 tokens) extended with the ChatML / Phi / LLaMA control tokens in the padded slots 50,256-50,269. All models to date use this.
- **a file name**, e.g. `"tokenizer.json"` or `"tokenizer.model"`: loaded from the model folder (Hugging Face `tokenizers` JSON, tiktoken BPE, or SentencePiece). `download_model.py` writes this key automatically for registry models that ship a tokenizer.
- **a Hugging Face repo id**, e.g. `"Qwen/Qwen2.5-0.5B"` or `"HuggingFaceTB/SmolLM2-135M"`: its `tokenizer.json` is downloaded into the model folder on first use and reused afterwards.

Requirements: the tokenizer must define `<|endoftext|>` (the pretraining document separator and the SFT/DPO pad token) and, for chat data, `<|im_start|>` / `<|im_end|>`; `vocab_size` must be at least the tokenizer's token count (a multiple of 64 or 128 for Tensor Cores; e.g. 151,936 for Qwen2.5's 151,665 tokens, 49,152 for SmolLM2). A missing file or a vocabulary that does not fit stops execution instead of falling back to GPT-2. The end-of-text / pad ids are read from the tokenizer everywhere (they are `151643` for Qwen2.5 and `0` for SmolLM2, not GPT-2's `50256`).

---

<a id="models_base_dir"></a>
<a id="--models_base_dir"></a>
### `--models_base_dir`
- **CLI Flag**: `--models_base_dir`
- **JSON Key**: `models_base_dir`
- **Type**: `str`
- **Default**: `"bin"`

#### In-Depth Explanation
The root folder under which all model subdirectories, datasets, checkpoints, and telemetry logs reside. Defaults to `bin`, meaning paths resolve to `bin/<model_name>/...`.

---

<a id="resume"></a>
<a id="--resume"></a>
<a id="no_resume"></a>
<a id="--no_resume"></a>
### `--resume`
- **CLI Flag**: `--resume`
- **JSON Key**: `resume`
- **Type**: `bool`
- **Default**: `True`

#### In-Depth Explanation
Controls whether the engine looks up existing checkpoints before training begins. Can be supplied on the command line as `--resume`, with an explicit boolean value (`--resume true` / `--resume false`), or defined in stage-specific JSON configuration files (`"resume": true` / `"resume": false`).
- **When `True` (default)**: Detects stage-specific checkpoints (`.trn.chk` for pretraining, `.sft.chk` for tuning, `.dpo.chk` for optimizing). Automatically restores model weights, optimizer states (first and second momentum buffers for AdamW and Muon), global step, epoch index, completed file indices, step within file, loss telemetry history, and accumulated training time.
- **When `False` (`--resume false` or `"resume": false`)**: Ignores existing stage checkpoints and begins fresh from step 0. In SFT and DPO, it loads the base weights from the preceding stage (`.trn.chk` or base `.pth`) while initializing optimizer states from scratch. Redundant `--no_resume` arguments have been removed in favor of setting `--resume false`.

---

<a id="3-hyperparameters--scheduling"></a>
## 3. Hyperparameters & Scheduling

<a id="batch_size"></a>
<a id="--batch_size"></a>
### `--batch_size`
- **CLI Flag**: `--batch_size`
- **JSON Key**: `batch_size`
- **Type**: `int`
- **Default**: `4`

#### In-Depth Explanation
The physical mini-batch size loaded into GPU memory per forward/backward step.
- **In Single-GPU**: The model processes `batch_size` sequences simultaneously.
- **In Multi-GPU Data Parallelism (`data-parallelism`)**: The `batch_size` is evenly divided across GPUs (e.g. `batch_size=16` across 2 GPUs assigns 8 sequences per GPU).
- **Effective Batch Size**: `Effective Batch Size = batch_size * accum_steps`.

#### Tradeoffs
Larger batch sizes maximize GPU Tensor Core saturation and throughput (tokens/sec) but consume substantially more VRAM for activations. If you hit CUDA Out of Memory (OOM), reduce `batch_size` and proportionally increase `accum_steps`.

---

<a id="accum_steps"></a>
<a id="--accum_steps"></a>
### `--accum_steps`
- **CLI Flag**: `--accum_steps`
- **JSON Key**: `accum_steps`
- **Type**: `int`
- **Default**: `1`

#### In-Depth Explanation
The number of micro-steps over which gradients are accumulated before executing an optimizer step (`optimizer.step()`) and zeroing gradients. Mathematically reproduces large batch training without incurring the VRAM cost of materializing large activation tensors simultaneously.

#### Tradeoffs
Higher accumulation steps reduce the frequency of optimizer updates and inter-GPU gradient reductions, which can slightly increase tokens/second throughput when communication bound. However, setting `accum_steps` excessively high can slow down convergence if the effective batch size becomes larger than optimal for the learning rate.

---

<a id="num_epochs"></a>
<a id="--num_epochs"></a>
### `--num_epochs`
- **CLI Flag**: `--num_epochs`
- **JSON Key**: `num_epochs`
- **Type**: `int`
- **Default**: `1`

#### In-Depth Explanation
Total number of full passes through the training dataset. For pretraining multi-file corpora, an epoch processes every combined text chunk in sequence. In SFT and DPO, an epoch iterates through all shuffled instruction/preference pairs.

---

<a id="learning_rate"></a>
<a id="--learning_rate"></a>
### `--learning_rate`
- **CLI Flag**: `--learning_rate`
- **JSON Key**: `learning_rate`
- **Type**: `float`
- **Default**: `5e-4` (`0.0005`)

#### In-Depth Explanation
Peak learning rate reached at the end of the warmup schedule. Governs parameter update magnitude in AdamW (and base optimizer steps).
- Pretraining typically uses higher learning rates (e.g. `3e-4` to `6e-4` for ~150M-1B models).
- Supervised Fine-Tuning (SFT) uses lower rates (`2e-5` to `5e-5`) to avoid catastrophic forgetting.
- Direct Preference Optimization (DPO) uses very conservative rates (`5e-7` to `5e-6`).

---

<a id="min_lr"></a>
<a id="--min_lr"></a>
### `--min_lr`
- **CLI Flag**: `--min_lr`
- **JSON Key**: `min_lr`
- **Type**: `float`
- **Default**: `1e-6` (`0.000001`)

#### In-Depth Explanation
The floor minimum learning rate reached at the conclusion of the cosine decay schedule. Prevents the learning rate from declining to exact zero, allowing continuous parameter adaptation in long training runs. Typically set to 10% of `--learning_rate`.

---

<a id="warmup_steps"></a>
<a id="--warmup_steps"></a>
### `--warmup_steps`
- **CLI Flag**: `--warmup_steps`
- **JSON Key**: `warmup_steps`
- **Type**: `int`
- **Default**: `100`

#### In-Depth Explanation
The number of initial training steps over which the learning rate ramps up linearly from `0.0` to `learning_rate`. Primarily utilized during pretraining (`STAGE_TRAIN`). Warmup prevents large, erratic gradients from destabilizing randomly initialized attention and feed-forward projections during early iterations.

---

<a id="warmup_ratio"></a>
<a id="--warmup_ratio"></a>
### `--warmup_ratio`
- **CLI Flag**: `--warmup_ratio`
- **JSON Key**: `warmup_ratio`
- **Type**: `float`
- **Default**: `0.03` (3%)

#### In-Depth Explanation
The fraction of total planned training steps dedicated to linear warmup during SFT and DPO. Calculated dynamically as `warmup_steps = int(total_steps * warmup_ratio)`. Standard setting is 3% to 5% (`0.03` to `0.05`).

---

<a id="weight_decay"></a>
<a id="--weight_decay"></a>
### `--weight_decay`
- **CLI Flag**: `--weight_decay`
- **JSON Key**: `weight_decay`
- **Type**: `float`
- **Default**: `0.01`

#### In-Depth Explanation
L2 weight regularization penalty applied by AdamW to 2D weight matrices (linear layers, projections, embeddings). Normalization weights (RMSNorm/LayerNorm gains) and 1D biases are explicitly excluded from weight decay. Pretraining typically uses `0.05` to `0.10`; fine-tuning typically uses `0.01`.

---

<a id="eval_freq"></a>
<a id="--eval_freq"></a>
### `--eval_freq`
- **CLI Flag**: `--eval_freq`
- **JSON Key**: `eval_freq`
- **Type**: `int`
- **Default**: `5`

#### In-Depth Explanation
Interval in training steps between validation evaluations. At each evaluation interval, the engine disables gradients (`torch.no_grad()`), switches the model to evaluation mode (`model.eval()`), evaluates validation loss over `--eval_iter` batches, samples a sample text generation from the prompt context, and logs metrics. Set higher (e.g. `50` to `100`) during production runs to minimize evaluation overhead.

---

<a id="eval_iter"></a>
<a id="--eval_iter"></a>
### `--eval_iter`
- **CLI Flag**: `--eval_iter`
- **JSON Key**: `eval_iter`
- **Type**: `int`
- **Default**: `1`

#### In-Depth Explanation
Number of mini-batches sampled from the validation set during each evaluation pass. Increasing `eval_iter` provides a lower-variance validation loss estimate at the expense of evaluation runtime.

---

<a id="save_interval"></a>
<a id="--save_interval"></a>
### `--save_interval`
- **CLI Flag**: `--save_interval`
- **JSON Key**: `save_interval`
- **Type**: `int`
- **Default**: `1000`

#### In-Depth Explanation
Frequency in training steps at which stage checkpoints are written to disk. Checkpoint writes use atomic file swaps with retry logic and file locking to guarantee that crashes or sudden interruptions cannot corrupt existing checkpoint files.

---

<a id="step_limit"></a>
<a id="--step_limit"></a>
### `--step_limit`
- **CLI Flag**: `--step_limit`
- **JSON Key**: `step_limit`
- **Type**: `int`
- **Default**: `None`

#### In-Depth Explanation
Optional hard limit on the number of steps to execute in the current session. When the session reaches `step_limit`, the engine executes an immediate atomic checkpoint save and terminates cleanly. Ideal for step-budgeted training sessions, benchmarking, and scheduled workflows.

---

<a id="4-hardware-multi-gpu--precision"></a>
## 4. Hardware, Multi-GPU & Precision

<a id="device"></a>
<a id="--device"></a>
### `--device`
- **CLI Flag**: `--device`
- **JSON Key**: `device`
- **Type**: `str`
- **Default**: `None` (auto-detects `cuda` if available, else `cpu`)

#### In-Depth Explanation
Explicit target device specification (e.g. `cuda`, `cuda:0`, `cpu`). When omitted, automatically selects CUDA if an NVIDIA GPU is detected.

---

<a id="pol_device"></a>
<a id="--pol_device"></a>
### `--pol_device`
- **CLI Flag**: `--pol_device`
- **JSON Key**: `pol_device`
- **Type**: `str`
- **Default**: `None`

#### In-Depth Explanation
Target CUDA device specification for the trainable **policy model** during Direct Preference Optimization (`STAGE_OPTIMIZE`). In dual-GPU setups, assigning `--pol_device cuda:0` and `--ref_device cuda:1` allows both models to reside on dedicated GPUs without sharing VRAM.

---

<a id="ref_device"></a>
<a id="--ref_device"></a>
### `--ref_device`
- **CLI Flag**: `--ref_device`
- **JSON Key**: `ref_device`
- **Type**: `str`
- **Default**: `None`

#### In-Depth Explanation
Target CUDA device specification for the frozen **reference model** during Direct Preference Optimization (`STAGE_OPTIMIZE`). When multi-GPU is available and `single_gpu=False`, defaults to `cuda:1`.

---

<a id="single_gpu"></a>
<a id="--single_gpu"></a>
### `--single_gpu`
- **CLI Flag**: `--single_gpu`
- **JSON Key**: `single_gpu`
- **Type**: `bool`
- **Default**: `True`

#### In-Depth Explanation
Forces single-GPU execution even if multiple CUDA GPUs are physically present. When `True` (the default), multi-GPU wrappers (`MultiGpuGptModelDP` and `MultiGpuGptModelPP`) are completely bypassed, running directly on `--gpu_index`. Multi-GPU training must be opted into with `--single_gpu false` or `"single_gpu": false` in the stage options file.

---

<a id="gpu_index"></a>
<a id="--gpu_index"></a>
### `--gpu_index`
- **CLI Flag**: `--gpu_index`
- **JSON Key**: `gpu_index`
- **Type**: `int`
- **Default**: `0`

#### In-Depth Explanation
Selects which physical CUDA device index to run on when `--single_gpu` is enabled or when targeting a single GPU.

When multi-GPU execution is enabled (`--single_gpu false`):
- `--gpu_index` establishes the **primary master GPU** (holding the primary model replica, master weights, optimizer states, gradient accumulation buffers, and broadcast origin).
- Secondary GPUs host worker replicas (in Data Parallelism) or remaining pipeline stages (in Pipeline Parallelism).
- **Workstation Optimization**: In dual-GPU systems where GPU 0 drives the Windows display / desktop window manager (DWM) and uses baseline VRAM, setting `--gpu_index 1` routes the primary model replica and optimizer states to dedicated GPU 1, freeing GPU 0 from peak optimizer memory overhead and avoiding Windows PCIe shared memory spillover.

---

<a id="precision"></a>
<a id="--precision"></a>
### `--precision`
- **CLI Flag**: `--precision`
- **JSON Key**: `precision`
- **Type**: `str`
- **Choices**: `fp16`, `fp8`, `fp32`
- **Default**: `"fp16"`

#### In-Depth Explanation
Controls computation precision and hardware Tensor Core acceleration:
- **`fp16`** (Automatic Mixed Precision / AMP): Model weights reside in `torch.bfloat16` (or `torch.float16` depending on hardware support). Operations run in half precision via `torch.amp.autocast`, while master weights and optimizer moments are tracked with `GradScaler`. Provides optimal throughput and halved VRAM consumption on modern RTX / datacenter GPUs.
- **`fp8`** (Float8 training via `torchao`): Master weights, activations and autocast stay `bfloat16` exactly as in `fp16`; every `Linear` layer (including the tied LM head) is swapped for a `Float8Linear` that runs its matmuls on the FP8 tensor cores (E4M3 activations/weights, E5M2 gradients) with tensorwise dynamic scaling. Supported on Ada Lovelace (RTX 40-series), Blackwell (RTX 50-series) and Hopper; on other GPUs it falls back to `fp16` with a warning. Parameter names and checkpoints are unchanged, so precision can be switched at any checkpoint in either direction. **Requires `--compile`**: the casts only fuse away under `torch.compile` (eager fp8 is slower than `fp16`). Measured on RTX 5070 Ti with the 355M model: ~25% less step time and ~25% less peak VRAM than `fp16`.
- **`fp32`**: Full 32-bit floating point precision without autocast. Disables Tensor Core acceleration and doubles memory usage; useful strictly for numerical debugging.

---

<a id="compile"></a>
<a id="--compile"></a>
### `--compile`
- **CLI Flag**: `--compile`
- **JSON Key**: `compile`
- **Type**: `bool`
- **Default**: `False`

#### In-Depth Explanation
Enables PyTorch 2.0 `torch.compile(model)` graph compilation using the OpenAI Triton compiler backend. Fuses pointwise operations, LayerNorm/RMSNorm, and attention mechanisms into optimized GPU kernels.
- **Benefits**: Can boost training throughput (tokens/sec) by 15% to 30%.
- **Tradeoffs**: Incurs JIT compilation latency during the first forward and backward iterations (which can take 30 to 90 seconds) and allocates temporary compilation scratchpad VRAM during warmup.

---

<a id="coordinate_descent_tuning"></a>
<a id="--coordinate_descent_tuning"></a>
### `--coordinate_descent_tuning`
- **CLI Flag**: `--coordinate_descent_tuning`
- **JSON Key**: `coordinate_descent_tuning`
- **Type**: `bool`
- **Default**: `False`

#### In-Depth Explanation
Requires `--compile`. Makes Inductor autotune the launch configuration (block sizes, warp count) of every compiled Triton kernel by coordinate descent instead of trusting its heuristics. The math is unchanged (loss and gradient norm match to rounding noise); only the kernels get faster. It targets the fp8 amax/quantize/transpose kernels, which are ~30% of a step and whose heuristic configs run far below memory bandwidth on Blackwell.
- **Measured gain**: +9% tok/sec on `andres1s-350M-fp8` pretraining (2x RTX 5070 Ti, 69k -> 75k tok/sec), about 3.3 hours saved on a 37 hour run.
- **Cost**: every compile takes ~5x longer. A cold pretraining start needs ~15 minutes instead of ~3 (the two data-parallel replicas compile one after another, since concurrent compiles race on the Windows Triton cache), plus ~3 minutes at the first evaluation. Both are cached: warm restarts stay at ~1 minute.
- **When it pays off**: runs that compile a handful of times and then train for hours (static-shape pretraining: break-even after ~2.5 hours of training). It is a net loss when variable batch shapes trigger many recompiles, as each recompile pays the ~15 minutes again.

---

<a id="activation_checkpointing"></a>
<a id="--activation_checkpointing"></a>
<a id="no_grad_checkpointing"></a>
<a id="--no_grad_checkpointing"></a>
### `--activation_checkpointing`
- **CLI Flag**: `--activation_checkpointing`
- **JSON Key**: `activation_checkpointing`
- **Type**: `bool`
- **Default**: `False`

#### In-Depth Explanation
Controls whether intermediate activation tensors in transformer blocks are retained or recomputed. Can be specified on the command line as `--activation_checkpointing`, with an explicit boolean (`--activation_checkpointing true` / `--activation_checkpointing false`), or configured in stage-specific JSON files (`"activation_checkpointing": true` / `"activation_checkpointing": false`).
- **When Enabled (`--activation_checkpointing` or `--activation_checkpointing true`)**: Transformer blocks discard intermediate activations during the forward pass and recalculate them on-demand during backpropagation (`torch.utils.checkpoint`). **Cuts activation VRAM by 60% to 80%**, enabling much larger batch sizes or sequence lengths without OOM.
- **Tradeoff**: Imposes an extra forward pass during backprop, causing a **~25% to 33% reduction in tokens/sec throughput**.
- **When Disabled (`--activation_checkpointing false` or default `False`)**: Retains all forward activations in memory, delivering maximum training throughput at the expense of higher VRAM. Redundant negation flags (`--no_grad_checkpointing`) have been removed in favor of setting `--activation_checkpointing false`.
- **User Control**: The orchestrator strictly obeys this flag with zero hidden heuristics or automatic parameter overrides.

---

<a id="freeze_embeddings"></a>
<a id="--freeze_embeddings"></a>
### `--freeze_embeddings`
- **CLI Flag**: `--freeze_embeddings`
- **JSON Key**: `freeze_embeddings`
- **Type**: `bool`
- **Default**: `False`

#### In-Depth Explanation
Freezes token embedding (`tok_emb`) and positional embedding (`pos_emb`) weights by setting `requires_grad = False` during SFT (`STAGE_TUNE`) or DPO (`STAGE_OPTIMIZE`).
- **Memory Savings**: In large vocabulary models (e.g. 50,304 vocab x 1,024 dim = 51.5M parameters), freezing embeddings eliminates AdamW first and second momentum optimizer state allocation for those 51.5M weights, saving over 400 MB of VRAM per GPU.

---

<a id="multi_gpu_strategy"></a>
<a id="--multi_gpu_strategy"></a>
### `--multi_gpu_strategy`
- **CLI Flag**: `--multi_gpu_strategy`
- **JSON Key**: `multi_gpu_strategy`
- **Type**: `str`
- **Choices**: `data-parallelism`, `parallel-pipeline`
- **Default**: `"data-parallelism"`

#### In-Depth Explanation
Determines how multi-GPU hardware acceleration is partitioned:
1. **`data-parallelism` (`MULTI_GPU_DP`)**: Replicates the entire model onto every active GPU. Each GPU processes an independent slice of the physical batch (`batch_size // num_gpus`). Forward and backward passes run concurrently via background worker threads, gradients are asynchronously averaged across GPUs, and master weights are synchronized after optimizer updates. Provides near-linear throughput scaling.
2. **`parallel-pipeline` (`MULTI_GPU_PP`)**: Splits transformer layers across GPUs (e.g. GPU 0 hosts layers 0–4; GPU 1 hosts layers 5–7 and the output head). Necessary when a model is too large to fit on a single GPU's VRAM.

---

<a id="multi_stage_micro_batching"></a>
<a id="--multi_stage_micro_batching"></a>
### `--multi_stage_micro_batching`
- **CLI Flag**: `--multi_stage_micro_batching`
- **JSON Key**: `multi_stage_micro_batching`
- **Type**: `int`
- **Default**: `4`

#### In-Depth Explanation
Number of micro-batches used to pipeline execution across GPUs when using pipelined model parallelism (`parallel-pipeline`). Slices each mini-batch so GPU 1 can begin computing early layers of micro-batch 1 while GPU 0 processes micro-batch 2.
- **Note**: This argument is strictly utilized by `MultiGpuGptModelPP`. In single-GPU mode or Data Parallelism (`data-parallelism`), this parameter is completely bypassed.

---

<a id="even_layers"></a>
<a id="--even_layers"></a>
### `--even_layers`
- **CLI Flag**: `--even_layers`
- **JSON Key**: `even_layers`
- **Type**: `bool`
- **Default**: `False`

#### In-Depth Explanation
Used in pipelined model parallelism (`parallel-pipeline`):
- When `False` (default): Employs an uneven 60/40 layer split (60% of layers on GPU 0, 40% on GPU 1) to account for the heavy output head (`out_head`) and loss computation residing on GPU 1.
- When `True`: Divides transformer blocks exactly 50/50 across GPUs.

---

<a id="1f1b"></a>
<a id="--1f1b"></a>
### `--1f1b`
- **CLI Flag**: `--1f1b`
- **JSON Key**: `use_1f1b`
- **Type**: `bool`
- **Default**: `False`

#### In-Depth Explanation
Enables One-Forward-One-Backward (1F1B) scheduling in pipelined model parallelism. Alternates forward and backward micro-steps once primed, capping peak in-flight activation memory to the number of pipeline stages instead of accumulating all forward activations before starting backprop.

---

<a id="async_pcie"></a>
<a id="--async_pcie"></a>
### `--async_pcie`
- **CLI Flag**: `--async_pcie`
- **JSON Key**: `async_pcie`
- **Type**: `bool`
- **Default**: `False`

#### In-Depth Explanation
Enables asynchronous, non-blocking PCIe memory transfers (`tensor.to(device, non_blocking=True)`) between GPUs in pipelined model parallelism. Allows inter-GPU tensor communication to overlap with transformer computation kernels.

---

<a id="5-optimizers"></a>
## 5. Optimizers

<a id="use_muon"></a>
<a id="--use_muon"></a>
<a id="disable_adamw_only"></a>
<a id="--disable_adamw_only"></a>
<a id="disable_muon"></a>
<a id="--disable_muon"></a>
<a id="use_adamw_only"></a>
<a id="--use_adamw_only"></a>
### `--use_muon`
- **CLI Flag**: `--use_muon`
- **JSON Key**: `use_muon`
- **Type**: `bool`
- **Default**: `False`

#### In-Depth Explanation
Enables the cutting-edge **Hybrid CustomMuon + AdamW** optimizer architecture. Can be enabled on the command line via `--use_muon`, specified with an explicit boolean (`--use_muon true` / `--use_muon false`), or configured in stage-specific JSON files (`"use_muon": true` / `"use_muon": false`).
- **When Enabled (`--use_muon` or `--use_muon true`)**:
  - **CustomMuon (Momentum Orthogonalized by Newton-Schulz)**: Updates internal 2D weight matrices (attention projections, MLP layers) using iterative Newton-Schulz matrix sign orthogonalization. Replaces AdamW's 2x parameter memory overhead with a single momentum buffer, cutting optimizer memory by up to 75% while achieving faster empirical convergence.
  - **Fused AdamW**: Concurrently handles 1D parameters, LayerNorm/RMSNorm gains, biases, and token embeddings.
- **When Disabled (`--use_muon false` or default `False`)**: Standard AdamW is utilized across 100% of model parameters. Redundant negation flags (`--disable_muon`, `--disable_adamw_only`, `--use_adamw_only`) have been eliminated in favor of setting `--use_muon false`.

---

<a id="muon_lr"></a>
<a id="--muon_lr"></a>
### `--muon_lr`
- **CLI Flag**: `--muon_lr`
- **JSON Key**: `muon_lr`
- **Type**: `float`
- **Default**: `1e-3` (`0.001`)

#### In-Depth Explanation
Peak learning rate for the CustomMuon optimizer when hybrid optimization is enabled. Because Newton-Schulz orthogonalization normalizes update matrices to unit spectral norm, Muon operates with a higher optimal learning rate (typically `0.001` to `0.002`) than AdamW.

---

<a id="6-dataset-sequence--loss-computation"></a>
## 6. Dataset, Sequence & Loss Computation

<a id="override_data_folder"></a>
<a id="--override_data_folder"></a>
### `--override_data_folder`
- **CLI Flags**: `--override_data_folder`, `--override_data_dir`, `--data_folder`, `--data_dir`, `--data_file`
- **JSON Key**: `override_data_folder`
- **Type**: `str`
- **Default**: `None`

#### In-Depth Explanation
Explicit filesystem override specifying a direct dataset file or directory. Bypasses standard directory resolution (`bin/<model_name>/data/<stage>/`), allowing execution on datasets stored at arbitrary filesystem locations.

---

<a id="train_ratio"></a>
<a id="--train_ratio"></a>
### `--train_ratio`
- **CLI Flag**: `--train_ratio`
- **JSON Key**: `train_ratio`
- **Type**: `float`
- **Default**: `0.90` (90%)

#### In-Depth Explanation
Proportion of the dataset allocated to training splits in SFT (`STAGE_TUNE`) and DPO (`STAGE_OPTIMIZE`). In pretraining, controls the train/validation token split within each chunked text file.

---

<a id="test_ratio"></a>
<a id="--test_ratio"></a>
### `--test_ratio`
- **CLI Flag**: `--test_ratio`
- **JSON Key**: `test_ratio`
- **Type**: `float`
- **Default**: `0.05` (5%)

#### In-Depth Explanation
Proportion of the dataset reserved for held-out evaluation and testing. The remaining fraction (`1.0 - train_ratio - test_ratio`) is allocated to validation.

---

<a id="max_length"></a>
<a id="--max_length"></a>
### `--max_length`
- **CLI Flag**: `--max_length`
- **JSON Key**: `max_length`
- **Type**: `int`
- **Default**: `None` (defaults to model's architectural `context_length`)

#### In-Depth Explanation
Maximum sequence length in tokens for tokenization and padding. During instruction tuning and DPO, batches are dynamically padded to the longest sequence in the batch, up to `--max_length`. If `--max_length` exceeds the model's architectural `context_length` (defined in `.model-params.json`), it is clamped to `context_length`.

---

<a id="pad_to_multiple_of"></a>
<a id="--pad_to_multiple_of"></a>
### `--pad_to_multiple_of`
- **CLI Flag**: `--pad_to_multiple_of`
- **JSON Key**: `pad_to_multiple_of`
- **Type**: `int`
- **Default**: `0` (pad exactly to the longest item in the batch)

#### In-Depth Explanation
SFT and DPO only (pretraining windows already have a fixed length). Rounds every batch's padded sequence length up to a multiple of this many tokens, and makes the token-budget packer size batches from the rounded lengths, so peak memory is unchanged. With `128`, a 1024-token context sees at most 8 distinct sequence lengths instead of hundreds.
- **Why**: `torch.compile` builds a new version of the model for every batch shape it has not seen yet and falls back to slow eager mode after 64 of them. With exact padding, the `andres1s-350M-fp8` SFT run compiled 7 forward + 17 loss-head versions in its first 20 steps (about 15 minutes of compiling for 20 steps of training) and kept going. With `128` it compiled 22 versions during the first 200 steps and then none for the rest of the run. The remaining versions come from things the bucket width cannot remove: one copy per GPU, train vs eval mode, Inductor's large/small tensor classes, and the small partial batch at the end of each packing window.
- **Memory**: fewer distinct shapes also fragment the CUDA allocator less. The same fp8 SFT config ran out of memory on the primary GPU at step 20 with exact padding, at step 72 with `16`, and at step 792 with `128`, so wider buckets are the safer choice for a memory-tight configuration.
- **Cost**: the extra padding is masked out of the loss (`-100` targets, causal attention), so the training math is unchanged, but it still costs compute. Measured on the `andres1s-350M` SFT data: about +14% padded tokens per epoch at `128`, +6% at `64`, about +1.5% at `16`.
- **When it pays off**: only together with `--compile`. In eager mode (e.g. DPO, which does not compile) it is pure padding cost. Batch boundaries change with this setting, so start a stage fresh rather than resuming a checkpoint taken with a different value.

---

<a id="chunk_size"></a>
<a id="--chunk_size"></a>
### `--chunk_size`
- **CLI Flag**: `--chunk_size`
- **JSON Key**: `chunk_size`
- **Type**: `int`
- **Default**: `512`

#### In-Depth Explanation
Chunk size (in tokens) used by chunked cross-entropy loss computation.
- **How It Works**: Multiplying hidden states `[batch * seq_len, emb_dim]` by the output projection head `[emb_dim, vocab_size]` produces a massive logits matrix. For `vocab_size=50304` and `8,192` tokens, full logits require ~824 MB in float32, and cross-entropy creates multiple gigabytes of intermediate softmax buffers. Chunked cross-entropy slices tokens into blocks of `--chunk_size`, projects only `chunk_size` tokens at a time, accumulates scalar loss, and frees logits immediately.
- **Recommended Value**: `512` (or `256` on memory-constrained GPUs). Setting this too high (e.g. `4096`) negates the benefit and causes CUDA OOM.

---

<a id="recompute_lmhead"></a>
<a id="--recompute_lmhead"></a>
### `--recompute_lmhead`
- **CLI Flag**: `--recompute_lmhead`
- **JSON Key**: `recompute_lmhead`
- **Type**: `bool`
- **Default**: `False`

#### In-Depth Explanation
Controls what the chunked cross-entropy keeps alive for the backward pass. The fp32 softmax of each chunk is always recomputed in backward; this flag decides whether the LM head projection is recomputed as well:
- **When `False` (default)**: Each chunk's bf16 logits stay in VRAM until backward (`tokens_per_step x vocab_size x 2` bytes per GPU, e.g. ~824 MB for 8,192 tokens and a 50,304 vocabulary) and only the cheap pointwise part is recomputed. Fastest option; in practice the peak VRAM is often unchanged because the peak occurs elsewhere in the step.
- **When `True`**: Only the hidden states are kept; each chunk's `[chunk_size, vocab_size]` projection is recomputed during backward. Minimum VRAM, at the cost of one extra LM head matmul per step (~3% of step time for a 1024-context, 50k-vocabulary model). Use it only when that VRAM is needed.

---

<a id="vocab_padded"></a>
<a id="--vocab_padded"></a>
### `--vocab_padded`
- **CLI Flag**: `--vocab_padded`
- **JSON Key**: `vocab_padded`
- **Type**: `bool`
- **Default**: `True`

#### In-Depth Explanation
When enabled and the base vocabulary is 50,257 (GPT-2 standard), automatically pads `vocab_size` to `50,304`. Because 50,304 is cleanly divisible by 64 and 128, matrix multiplications align with NVIDIA Tensor Core tile boundaries, accelerating output head projections by up to 15%. Can be explicitly disabled by specifying `--vocab_padded false` on the command line or `"vocab_padded": false` in JSON options.

---

<a id="mask_prompt"></a>
<a id="--mask_prompt"></a>
<a id="no_mask_prompt"></a>
<a id="--no_mask_prompt"></a>
### `--mask_prompt`
- **CLI Flag**: `--mask_prompt`
- **JSON Key**: `mask_prompt`
- **Type**: `bool`
- **Default**: `True`

#### In-Depth Explanation
Controls prompt token masking during instruction fine-tuning (`STAGE_TUNE`). Can be configured on the command line via `--mask_prompt` / `--mask_prompt true`, disabled via `--mask_prompt false`, or set in JSON options via `"mask_prompt": true` / `"mask_prompt": false`.
- **When True (default `True` or `--mask_prompt`)**: Targets for prompt tokens are masked with `-100`, so cross-entropy loss is strictly computed and backpropagated on the assistant's response tokens.
- **When False (`--mask_prompt false` or `"mask_prompt": false`)**: Disables prompt masking, training the model to predict both prompt tokens and response tokens. Redundant negation flags (`--no_mask_prompt`) have been replaced by setting `--mask_prompt false`.

---

<a id="precompute_total_steps"></a>
<a id="--precompute_total_steps"></a>
### `--precompute_total_steps`
- **CLI Flag**: `--precompute_total_steps`
- **JSON Key**: `precompute_total_steps`
- **Type**: `bool`
- **Default**: `False`

#### In-Depth Explanation
Used during pretraining (`STAGE_TRAIN`). Proactively tokenizes and caches step counts across all text files in the corpus prior to starting training, saving the results to `steps_cache.json`. Ensures that step counts, progress bars, and ETA calculations are 100% accurate from step 1 instead of relying on running averages.

---

<a id="7-inference-evaluation--debugging"></a>
## 7. Inference, Evaluation & Debugging

<a id="temperature"></a>
<a id="--temperature"></a>
### `--temperature`
- **CLI Flag**: `--temperature`
- **JSON Key**: `temperature`
- **Type**: `float`
- **Default**: `0.0`

#### In-Depth Explanation
Sampling temperature for autoregressive text generation during evaluation passes:
- `0.0` (default): Greedy argmax decoding (deterministic, selects the highest-probability token at each step).
- `> 0.0` (e.g. `0.7` to `1.0`): Scales logits before softmax to introduce creative diversity.

---

<a id="top_k"></a>
<a id="--top_k"></a>
### `--top_k`
- **CLI Flag**: `--top_k`
- **JSON Key**: `top_k`
- **Type**: `int`
- **Default**: `None`

#### In-Depth Explanation
Filters text generation vocabulary to the `top_k` most probable candidate tokens before sampling. Prevents low-probability tokens from corrupting generation.

---

<a id="chat"></a>
<a id="--chat"></a>
### `--chat`
- **CLI Flag**: `--chat`
- **JSON Key**: `chat`
- **Type**: `bool`
- **Default**: `False`

#### In-Depth Explanation
When set, immediately launches an interactive multi-turn terminal chatbot session upon the completion of fine-tuning or preference optimization, allowing real-time testing of conversational responses.

---

<a id="save_timeout"></a>
<a id="--save_timeout"></a>
### `--save_timeout`
- **CLI Flag**: `--save_timeout`
- **JSON Key**: `save_timeout`
- **Type**: `float`
- **Default**: `600.0` (seconds)

#### In-Depth Explanation
Timeout in seconds when acquiring file system locks during atomic checkpoint saving. Protects against race conditions or locked file handles in multi-process environments.

---

<a id="verbose"></a>
<a id="--verbose"></a>
### `--verbose`
- **CLI Flag**: `--verbose`
- **JSON Key**: `verbose`
- **Type**: `bool`
- **Default**: `False`

#### In-Depth Explanation
Enables verbose generation output during periodic evaluations, printing prompt and response samples directly to the terminal console.

---

<a id="test_mode"></a>
<a id="--test_mode"></a>
### `--test_mode`
- **CLI Flag**: `--test_mode`
- **JSON Key**: `test_mode`
- **Type**: `bool`
- **Default**: `False`

#### In-Depth Explanation
Rapid debugging flag that truncates instruction and preference datasets to exactly 20 samples. Enables rapid end-to-end testing of data collation, forward passes, backward passes, optimizer steps, and checkpoint saving within seconds.

---

<a id="beta"></a>
<a id="--beta"></a>
### `--beta`
- **CLI Flag**: `--beta`
- **JSON Key**: `beta`
- **Type**: `float`
- **Default**: `0.1`

#### In-Depth Explanation
The implicit reward temperature parameter $\beta$ in Direct Preference Optimization (`STAGE_OPTIMIZE`). Controls the penalty strength against deviating from the reference policy:
- Typical values range from `0.05` to `0.2`.
- Smaller $\beta$ (e.g. `0.05`) gives the policy model more freedom to adapt to preferences.
- Larger $\beta$ (e.g. `0.2` to `0.5`) anchors the policy closely to the reference model, preserving general language coherence and preventing over-optimization.
