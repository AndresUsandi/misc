# Unified GPT Inference & Interactive Chat Arguments Guide

This document provides a comprehensive technical reference for every command-line argument and configuration option in the interactive inference engine (`infer.py`). All arguments can be specified on the command line or persisted in model-specific JSON configuration files (`<model_name>.options-infer.json`).

---

## Table of Contents

1. [Model & Input Specification](#1-model--input-specification)
   - [`--model_name`](#model_name)
   - [`--models_base_dir`](#models_base_dir)
   - [`--prompt`](#prompt)
   - [`--autocorrect`](#autocorrect)
2. [Sampling & Generation Controls](#2-sampling--generation-controls)
   - [`--max_new_tokens`](#max_new_tokens)
   - [`--temperature`](#temperature)
   - [`--top_k`](#top_k)
   - [`--top_p`](#top_p)
   - [`--repetition_penalty`](#repetition_penalty)
3. [Hardware, Acceleration & Precision](#3-hardware-acceleration--precision)
   - [`--device`](#device)
   - [`--single_gpu`](#single_gpu)
   - [`--gpu_index`](#gpu_index)
   - [`--precision`](#precision)
   - [`--use_cache`](#use_cache)
   - [`--use_cuda_graph`](#use_cuda_graph)
4. [Input Preprocessing & Spell Correction](#4-input-preprocessing--spell-correction)
   - [`--autocorrect`](#autocorrect)

---

<a id="1-model--input-specification"></a>
## 1. Model & Input Specification

<a id="model_name"></a>
<a id="--model_name"></a>
### `--model_name`
- **CLI Flag**: `--model_name`
- **JSON Key**: `model_name`
- **Type**: `str`
- **Default**: none (required, same as `train.py`)

#### In-Depth Explanation
Designates the target model architecture and weights to load for execution:
- **Registry / Hub Models**: Supports official pretrained open weights including the standard GPT-2 family (`gpt2:124M`, `gpt2:355M`, `gpt2:774M`, `gpt2:1.5B`), LLaMA 3.2 (`llama3.2:1B`, `llama3.2:3B`), Qwen 2.5 / 3 (`qwen3:0.6B`), and Gemma 2 (`gemma2:2B`).
- **Custom Local Models**: Resolves local model subdirectories inside `<models_base_dir>/<model_name>/` (e.g. `andres1xs-150M`, `andres1-1B`). Checks for configuration metadata in `<model_name>.config.json` and automatically discovers stage checkpoints (`.dpo.chk`, `.sft.chk`, `.trn.chk`, or base `.pth` weights).
- **Filesystem Paths**: Accepts direct filesystem paths to custom checkpoint files or weights directories.
- **Tokenizer**: Taken from the model's `model-params.json` (`"tokenizer"` key; see ARGUMENTS-TRAIN.md). There is no inference-side override, so the exact vocabulary the model was trained with is always used.

---

<a id="models_base_dir"></a>
<a id="--models_base_dir"></a>
### `--models_base_dir`
- **CLI Flag**: `--models_base_dir`
- **JSON Key**: not overridable from JSON (it locates the JSON file itself)
- **Type**: `str`
- **Default**: `"bin"`

#### In-Depth Explanation
Root directory under which model folders live, identical to the `train.py` flag of the same name. Weights, `<model_name>.model-params.json`, `<model_name>.options-infer.json`, and `log.txt` are all resolved as `<models_base_dir>/<model_name>/...`, so a model trained with `train.py --models_base_dir D:\models` is served with `infer.py --models_base_dir D:\models`.

---

<a id="prompt"></a>
<a id="--prompt"></a>
### `--prompt`
- **CLI Flag**: `--prompt`
- **JSON Key**: `prompt`
- **Type**: `str`
- **Default**: `None`

#### In-Depth Explanation
Controls single-query execution versus continuous conversational interaction:
- **Single-Turn Mode (`--prompt "..."`)**: Executes text generation on the specified prompt string, streams decoded tokens in real time to the terminal console, displays performance telemetry (generation throughput in tokens/sec and total latency), and terminates. Ideal for scripting, automated evaluation, batch queries, or integration testing.
- **Interactive Chat Mode (`--prompt` omitted)**: Launches a multi-turn conversation loop directly in the terminal console. The engine maintains conversation history across dialogue turns, applies the appropriate chat template boundaries (`User:`, `Assistant:`), and supports session management commands (`exit`, `quit`, `clear`, `reset`).

---

<a id="autocorrect"></a>
<a id="--autocorrect"></a>
### `--autocorrect`
- **CLI Flag**: `--autocorrect`
- **JSON Key**: `autocorrect`
- **Type**: `bool`
- **Default**: `True`

#### In-Depth Explanation
Enables automated dictionary-based spell checking and character transposition cleanup on user input prompts prior to tokenization using `SymSpell` (frequency-weighted Damerau-Levenshtein distance):
- **Why It Matters**: Common typos and keyboard slips (e.g. `frankestain` instead of `frankenstein`, `teh` instead of `the`) fragment into rare subwords during BPE tokenization. For smaller or focused models, rare subword embeddings can cause out-of-distribution attention collapse, triggering repetitive or off-topic responses.
- **How It Works**: Pre-scans English words against an indexed frequency dictionary (~83k unigrams and ~243k bigrams) in < 1ms. Fixes typos while preserving punctuation, numerical entities, and sentence casing.
- **Console Transparency**: Logs any applied corrections to the terminal console (e.g. `[Autocorrect] Corrected: 'frankestain' -> 'frankenstein'`).
- **Disabling**: Can be turned off via `--autocorrect False` on the CLI or `"autocorrect": false` in JSON options.

---

<a id="2-sampling--generation-controls"></a>
## 2. Sampling & Generation Controls

<a id="max_new_tokens"></a>
<a id="--max_new_tokens"></a>
### `--max_new_tokens`
- **CLI Flag**: `--max_new_tokens`
- **JSON Key**: `max_new_tokens`
- **Type**: `int`
- **Default**: `1024`

#### In-Depth Explanation
Enforces an absolute ceiling on the number of new tokens generated during a single response turn:
- **Early Termination**: Autoregressive generation halts as soon as the model predicts any registered end-of-sequence (EOS) token (e.g. `<|endoftext|>`, `<|im_end|>`, `<|eot_id|>`, or `<end_of_turn>`).
- **Context Length Clamping**: If the input prompt length plus requested `max_new_tokens` exceeds the model's architectural `context_length` (e.g. 1024 or 2048 tokens), the engine automatically clamps `max_new_tokens` to `context_length - prompt_len` to prevent out-of-bounds positional encoding errors.

---

<a id="temperature"></a>
<a id="--temperature"></a>
### `--temperature`
- **CLI Flag**: `--temperature`
- **JSON Key**: `temperature`
- **Type**: `float`
- **Default**: `0.7`

#### In-Depth Explanation
Controls the sharpness of the probability distribution over the vocabulary prior to token sampling via logit scaling:
$$\tilde{z}_i = \frac{z_i}{T}$$

- **`0.0` (Greedy Decoding)**: Evaluates $\text{argmax}(z_i)$, deterministically selecting the single token with the highest predicted probability at every step. Ensures 100% reproducible completions with zero variance. Best for factual question answering, code generation, and mathematical reasoning.
- **`0.1` to `0.5` (Conservative Sampling)**: Tightly concentrates probability mass on top candidates while permitting slight lexical variety.
- **`0.6` to `0.8` (Balanced Conversational)**: Standard default for multi-turn conversational agents. Produces creative, human-like dialogue without incoherence.
- **`> 0.9` (High Diversity / Creative)**: Flattens the probability distribution across vocabulary tokens. Increases stylistic diversity but significantly elevates the probability of hallucination or repetition loops.

---

<a id="top_k"></a>
<a id="--top_k"></a>
### `--top_k`
- **CLI Flag**: `--top_k`
- **JSON Key**: `top_k`
- **Type**: `int`
- **Default**: `50`

#### In-Depth Explanation
Restricts candidate token selection to the top $k$ highest-probability tokens at each generation step:
- **Mechanism**: Sorts unnormalized logits in descending order, identifies the $k$-th value, and sets all subsequent logits to $-\infty$.
- **Purpose**: Eliminates improbable, low-scoring tail tokens that can corrupt generation coherence, preventing bizarre vocabulary substitutions.
- **Tuning**: Typical values range from `20` to `50`. Passing `--top_k None` or `0` disables top-k truncation, allowing top-p or raw temperature sampling across the entire vocabulary.

---

<a id="top_p"></a>
<a id="--top_p"></a>
### `--top_p`
- **CLI Flag**: `--top_p`
- **JSON Key**: `top_p`
- **Type**: `float`
- **Default**: `0.9`

#### In-Depth Explanation
Implements **Nucleus (Top-p) Sampling** (Holtzman et al.), dynamically truncating the candidate vocabulary to the smallest subset of tokens whose cumulative probability exceeds threshold $p$:
$$\sum_{i \in V^{(p)}} P(w_i \mid w_{<t}) \ge p$$

- **Dynamic Vocabulary Adaptation**: Unlike static top-k filtering, nucleus sampling dynamically expands the candidate pool when the model is uncertain (flat probability distribution) and contracts it to a handful of tokens when confidence is high (sharp distribution).
- **Default (`0.9`)**: Retains the top 90% of probability mass, trimming the tail 10%.
- **Combined Filtering Pipeline**: When combined with `--top_k` and `--temperature`, operations execute sequentially:
  1. Temperature scaling ($z / T$)
  2. Top-k filtering (cuts pool to top $k$)
  3. Softmax computation
  4. Top-p thresholding (retains cumulative mass $p$)
  5. Multinomial token sampling

---

<a id="repetition_penalty"></a>
<a id="--repetition_penalty"></a>
### `--repetition_penalty`
- **CLI Flag**: `--repetition_penalty`
- **JSON Key**: `repetition_penalty`
- **Type**: `float`
- **Default**: `1.2`

#### In-Depth Explanation
Penalizes the unnormalized logit values of tokens that have already appeared in the prompt or previously generated sequence to prevent repetitive degeneration and phrase looping (Keskar et al., 2019):

$$\text{logit}(w_i) = \begin{cases} \text{logit}(w_i) / \theta & \text{if } \text{logit}(w_i) > 0 \\ \text{logit}(w_i) \times \theta & \text{if } \text{logit}(w_i) < 0 \end{cases} \quad \forall w_i \in \text{context}$$

where $\theta \ge 1.0$ is the repetition penalty factor:
- **`1.0`**: Repetition penalty disabled (unmodified model logits).
- **`> 1.0`**: Penalizes seen tokens. Positive logits are scaled down towards zero; negative logits are amplified downwards (more negative).
- **Typical Range**: `1.1` to `1.3`. A default of `1.2` provides effective protection against degeneration and loops without degrading natural language fluency or grammatical phrasing. For compact models susceptible to context echoing, `1.25` is recommended.
- **Special Token Exemption**: All special control and boundary tokens (`<|...|>`, e.g. `<|im_start|>`, `<|im_end|>`, `<|endoftext|>`) are strictly exempt from repetition penalties, ensuring conversation turn delimiters and EOS stop signals are never suppressed when seen in context.

---

<a id="3-hardware-acceleration--precision"></a>
## 3. Hardware, Acceleration & Precision

<a id="device"></a>
<a id="--device"></a>
### `--device`
- **CLI Flag**: `--device`
- **JSON Key**: `device`
- **Type**: `str`
- **Default**: none (same as `train.py`: CUDA when available, otherwise CPU)

#### In-Depth Explanation
Specifies the target compute backend:
- **Omitted**: Uses CUDA (device `--gpu_index`) when available, otherwise CPU. Equivalent to `"auto"`.
- **`"cuda"`**: Standard CUDA device execution. Automatically falls back to CPU if no NVIDIA CUDA device is detected.
- **`"cuda:0"` / `"cuda:1"`**: Pins execution to an explicit physical CUDA GPU.
- **`"auto"`**: Detects system capabilities and routes execution to CUDA when available, otherwise CPU.
- **`"cpu"`**: Forces execution entirely in host system RAM on the CPU. Disables CUDA Graphs and Tensor Core acceleration, and never shards onto GPUs regardless of `--single_gpu`.

---

<a id="single_gpu"></a>
<a id="--single_gpu"></a>
### `--single_gpu`
- **CLI Flag**: `--single_gpu`
- **JSON Key**: `single_gpu`
- **Type**: `bool`
- **Default**: `True` (same as `train.py`)

#### In-Depth Explanation
Controls whether inference is executed on a single GPU or distributed across multiple GPUs:
- **When `True` (default `True` or `--single_gpu`)**: Forces inference to run exclusively on the device targeted by `--gpu_index`. Bypasses multi-GPU pipeline sharding. For all models that fit within the VRAM of a single GPU (e.g. 124M to 3B models on 12GB+ GPUs), single-GPU execution delivers the lowest latency and highest tokens/sec throughput because inter-GPU PCIe transmission overhead is eliminated.
- **When `False` (`--single_gpu false` or `"single_gpu": false`)**: In multi-GPU workstations with 2 or more CUDA GPUs, automatically shards transformer blocks across available GPUs via `MultiGpuGptModelPP`. Enables executing models whose weights and KV cache exceed single-device memory limits.

---

<a id="gpu_index"></a>
<a id="--gpu_index"></a>
### `--gpu_index`
- **CLI Flag**: `--gpu_index`
- **JSON Key**: `gpu_index`
- **Type**: `int`
- **Default**: `0` (same as `train.py`)

#### In-Depth Explanation
Selects which physical CUDA device index to execute on when `--single_gpu` is enabled, or the primary device when multi-GPU sharding is active:
- **Dual-GPU Workstations**: In configurations where GPU 0 drives the primary desktop display, UI compositors, or a concurrent training run, set `"gpu_index": 1` in the model's `options-infer.json` (or pass `--gpu_index 1`) so chat generation gets dedicated VRAM and uninterrupted compute bandwidth.
- **Single-GPU Systems**: Device `0` is the only valid index.

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
Selects the floating-point execution precision:
- **`fp16` (Automatic Mixed Precision / Half Precision)**: Weights reside in `torch.bfloat16` (or `torch.float16` on devices lacking native bfloat16 hardware support). Unlocks NVIDIA Tensor Core matrix multiplication units, cutting VRAM footprint in half and doubling decoding throughput compared to full precision. Recommended for 99% of production and local chat sessions.
- **`fp8` (8-Bit Floating Point)**: Leverages native hardware FP8 tensor cores (Float8 E4M3FN format) available on NVIDIA Ada Lovelace (RTX 40-series), Blackwell (RTX 50-series), and Hopper architectures. Reduces memory bandwidth pressure by another 50%, accelerating memory-bound autoregressive decoding.
- **`fp32` (Single Precision)**: Full 32-bit floating point. Doubles memory usage and disables Tensor Cores. Strictly recommended for numerical verification or debugging precision divergence.

---

<a id="use_cache"></a>
<a id="--use_cache"></a>
<a id="no_cache"></a>
<a id="--no_cache"></a>
### `--use_cache`
- **CLI Flag**: `--use_cache`
- **JSON Key**: `use_cache`
- **Type**: `bool`
- **Default**: `True`

#### In-Depth Explanation
Enables static Key-Value (KV) attention caching across autoregressive generation turns:
- **Algorithmic Advantage**: Without KV caching, predicting token $t+1$ requires recomputing key and value projections for all preceding tokens $1 \dots t$, causing computational complexity to scale quadratically $O(t^2)$ with generated sequence length.
- **With KV Cache Enabled (`default True` or `--use_cache`)**: Attention projections for historical tokens are computed exactly once and stored in pre-allocated static tensors. Generating each subsequent token requires only $O(1)$ projection for the new token and $O(t)$ attention dot-product, resulting in **5x to 15x faster generation speeds**.
- **Disabling KV Caching**: Can be explicitly disabled via `--use_cache false` or `"use_cache": false`. Redundant negation flags (`--no_cache`) have been replaced by setting `--use_cache false`. Useful strictly for measuring non-cached reference baselines or debugging state retention.

---

<a id="use_cuda_graph"></a>
<a id="--use_cuda_graph"></a>
<a id="no_cuda_graph"></a>
<a id="--no_cuda_graph"></a>
### `--use_cuda_graph`
- **CLI Flag**: `--use_cuda_graph`
- **JSON Key**: `use_cuda_graph`
- **Type**: `bool`
- **Default**: `True`

#### In-Depth Explanation
Enables PyTorch CUDA Graph capture for the static KV cache decoding step:
- **The CPU Overhead Problem**: Autoregressive decoding processes one token per step with tiny batch sizes ($B=1$). Because individual GPU kernels execute in microseconds, the CPU driver overhead of launching dozens of individual CUDA kernels (LayerNorm, QKV projections, attention dot-products, MLP blocks) often becomes the primary throughput bottleneck.
- **CUDA Graph Acceleration (`default True` or `--use_cuda_graph`)**: Captures the entire forward graph into a single executable hardware task sequence. Subsequent generation steps execute via a single CPU launch call, driving CPU dispatch latency to near zero and maximizing GPU Tensor Core memory bandwidth saturation.
- **Requirements & Constraints**: Operates in conjunction with static KV caching on a single GPU (`num_gpus <= 1`).
- **Disabling CUDA Graphs**: Can be disabled via `--use_cuda_graph false` or `"use_cuda_graph": false`. Redundant negation flags (`--no_cuda_graph`) have been replaced by setting `--use_cuda_graph false`.

---

<a id="4-input-preprocessing--spell-correction"></a>
## 4. Input Preprocessing & Spell Correction

All multi-turn conversations and dataset cleanup strictly utilize standard **ChatML** format (`<|im_start|>role\ncontent<|im_end|>\n<|im_start|>assistant\n`), ensuring universal delimiter syntax and clean turn boundaries across all models.

<a id="autocorrect"></a>
<a id="--autocorrect"></a>
### `--autocorrect`
- **CLI Flag**: `--autocorrect`
- **JSON Key**: `autocorrect`
- **Type**: `bool` (`str_to_bool`)
- **Default**: `True`

#### In-Depth Explanation
Automatically corrects typographical errors and character transpositions in user prompts prior to tokenization and inference:
- **Typo & Transposition Mitigation**: Uses SymSpell's frequency-weighted dictionary (`frequency_dictionary_en_82_765.txt` and bigram frequencies) with Damerau-Levenshtein distance (handling adjacent keystroke transpositions such as "teh" -> "the", "helo" -> "hello", "frankestain" -> "frankenstein").
- **Preserving Attention Integrity**: Typos cause subword BPE tokenizers to shatter familiar words into obscure, rare byte fragments (e.g. `['frank', 'est', 'ain']`), causing attention collapse in smaller language models. Autocorrecting beforehand ensures high-frequency vocabulary representations are passed into the transformer.
- **Disabling Autocorrect**: Can be disabled via `--autocorrect false` or `"autocorrect": false` in options files when raw verbatim text evaluation or adversarial testing is required.

---

## 5. Configuration via JSON Options Files

All parameters documented in this guide (except `--model_name` and `--models_base_dir`, which are needed to find the file) can be persistently defined in a model-specific options file located alongside the model checkpoint at `<models_base_dir>/<model_name>/<model_name>.options-infer.json`.

When present, the orchestrator automatically loads this file and applies overrides to default arguments before initializing hardware devices. Values are resolved in three layers, lowest to highest: built-in defaults (`argsutil.InferenceArgs`), then the options file, then the command line.

### Example Configuration (`andres1-1B.options-infer.json`)
```json
{
  "max_new_tokens": 1024,
  "temperature": 0.7,
  "top_k": 50,
  "top_p": 0.9,
  "precision": "fp16",
  "single_gpu": true,
  "gpu_index": 1,
  "use_cache": true,
  "use_cuda_graph": true,
  "autocorrect": true
}
```
Command-line arguments provided at execution time take ultimate precedence over options file values, allowing dynamic experimentation without modifying saved JSON files.
