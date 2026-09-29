# Copyright (c) Sebastian Raschka under Apache License 2.0 (see LICENSE.txt).
# Command-line argument parsers for GPT Inference and Training pipelines.

import argparse
from dataclasses import dataclass
from pathlib import Path
import sys
from typing import List, Optional

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from gptio.options import apply_options_overrides
from gptio.pathutil import MULTI_GPU_DP, MULTI_GPU_PP, STAGE_TRAIN, STAGE_TUNE, STAGE_OPTIMIZE, STAGE_INFER
from gptutils.consoleutils import str_to_bool


@dataclass
class ModelArgs:
    """Options shared by train.py and infer.py: which model, where it lives on disk, and where it runs.
    Base class of TrainingArgs and InferenceArgs; the gptio / gptmodel primitives take this instead of model_name / models_dir pairs."""
    model_name: Optional[str] = None
    models_base_dir: str = "bin"
    device: Optional[str] = None  # None: use CUDA when available, else CPU
    precision: str = "fp16"
    single_gpu: bool = True
    gpu_index: int = 0


@dataclass
class InferenceArgs(ModelArgs):
    """All infer.py options. Value precedence: command line > <model_name>.options-infer.json > these defaults."""
    prompt: Optional[str] = None
    max_new_tokens: int = 1024
    temperature: float = 0.7
    top_k: Optional[int] = 50
    top_p: float = 0.9
    min_p: Optional[float] = None
    adaptive_temp: bool = False
    temp_min: float = 0.15
    temp_max: float = 0.85
    repetition_penalty: float = 1.15
    use_cache: bool = True
    use_cuda_graph: bool = True
    autocorrect: bool = True
    system_prompt: str = "You are a helpful and coherent AI assistant."


@dataclass
class TrainingArgs(ModelArgs):
    """All train.py options. Value precedence: command line > <model_name>.options-<stage>.json > these defaults."""
    training_process: Optional[str] = None
    resume: bool = True
    batch_size: int = 4
    accum_steps: int = 1
    num_epochs: int = 1
    learning_rate: float = 5e-4
    min_lr: float = 1e-6
    warmup_steps: int = 100
    warmup_ratio: float = 0.03
    weight_decay: float = 0.01
    eval_freq: int = 5
    eval_iter: int = 1
    save_interval: int = 1000
    step_limit: Optional[int] = None
    pol_device: Optional[str] = None
    ref_device: Optional[str] = None
    compile: bool = False
    coordinate_descent_tuning: bool = False
    activation_checkpointing: bool = False
    freeze_embeddings: bool = False
    multi_stage_micro_batching: int = 4
    multi_gpu_strategy: str = MULTI_GPU_DP
    even_layers: bool = False
    use_1f1b: bool = False
    async_pcie: bool = False
    use_muon: bool = False
    muon_lr: float = 1e-3
    override_data_folder: Optional[str] = None
    train_ratio: float = 0.90
    test_ratio: float = 0.05
    max_length: Optional[int] = None
    pad_to_multiple_of: int = 0
    chunk_size: int = 512
    recompute_lmhead: bool = False
    vocab_padded: bool = True
    temperature: float = 0.0
    top_k: Optional[int] = None
    save_timeout: float = 600.0
    mask_prompt: bool = True
    verbose: bool = False
    test_mode: bool = False
    beta: float = 0.1
    precompute_total_steps: bool = False
    json_precompute: bool = False

    @property
    def stage(self) -> str:
        """Pipeline stage (STAGE_TRAIN / STAGE_TUNE / STAGE_OPTIMIZE) derived from --training_process."""
        process_str = self.training_process.lower()
        if "opt" in process_str or "dpo" in process_str:
            return STAGE_OPTIMIZE
        if "tune" in process_str or "sft" in process_str or "fine" in process_str:
            return STAGE_TUNE
        return STAGE_TRAIN


def build_inference_parser(argv: Optional[List[str]] = None) -> InferenceArgs:
    """Builds InferenceArgs for infer.py: defaults, overridden by <model_name>.options-infer.json, overridden by the command line (argv defaults to sys.argv)."""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Interactive Multi-Turn GPT Chat & Execution Interface.",
        argument_default=argparse.SUPPRESS,  # only arguments actually typed on the command line end up in the namespace
    )
    parser.add_argument("--model_name", type=str, required=True, help="Canonical model identifier (e.g. 'gpt2:124M', 'andres1xs-150M', 'andres1-1B') or custom directory path. Dictates model architecture configuration, tokenizer selection, and checkpoint resolution. Required.")
    parser.add_argument("--models_base_dir", type=str, help="Root filesystem directory where models, options files, and logs reside. Defaults to 'bin' so paths resolve to bin/<model_name>/...")
    parser.add_argument("--prompt", type=str, help="Initial input prompt text for single-turn generation. When omitted or empty, launches an interactive multi-turn terminal conversation session with streaming token output. Useful for scripting automated queries or benchmarking.")
    parser.add_argument("--max_new_tokens", type=int, help="Hard ceiling on the number of new tokens generated per response turn. Generation terminates early if an end-of-sequence token (<|endoftext|>, <|im_end|>, etc.) is decoded. Default is 1024 tokens.")
    parser.add_argument("--temperature", type=float, help="Softmax sampling temperature controlling response randomness and creativity. Setting to 0.0 enforces deterministic greedy decoding. Values between 0.6 and 0.8 provide balanced conversational responses, while higher values increase variability.")
    parser.add_argument("--top_k", type=int, help="Filters candidate tokens to the k highest-probability entries prior to sampling. Eliminates tail probabilities that could introduce nonsensical completions. Set to None to disable top-k filtering; default is 50.")
    parser.add_argument("--top_p", type=float, help="Nucleus sampling threshold retaining the cumulative top probability mass up to p. Dynamically adapts candidate set size depending on model confidence. Default is 0.9 (90%% cumulative probability).")
    parser.add_argument("--min_p", type=float, help="Minimum probability threshold relative to top token (e.g. 0.05). Prunes candidate tokens with prob < min_p * p_max. Set to None to disable.")
    parser.add_argument("--adaptive_temp", type=str_to_bool, nargs="?", const=True, help="Dynamically scales softmax temperature token-by-token based on Shannon entropy of model logits. Cools temperature down for confident/factual tokens and warms it up for open-ended/creative tokens.")
    parser.add_argument("--temp_min", type=float, help="Minimum temperature floor for confident/factual tokens during adaptive temperature scaling. Defaults to 0.15.")
    parser.add_argument("--temp_max", type=float, help="Maximum temperature ceiling for creative/open-ended tokens during adaptive temperature scaling. Defaults to 0.85.")
    parser.add_argument("--repetition_penalty", type=float, help="Penalty factor applied to logits of previously generated tokens to discourage repetition and loops. Values > 1.0 penalize repeated tokens, while 1.0 disables the penalty. Default is 1.2.")
    parser.add_argument("--use_cache", type=str_to_bool, nargs="?", const=True, help="Enables static Key-Value (KV) attention caching to accelerate autoregressive decoding. Eliminates quadratic recomputation of previous token representations, drastically improving generation speed. Set to False to disable KV caching for debugging.")
    parser.add_argument("--device", type=str, help="Target execution device: 'cuda', 'cuda:N', 'cpu', or 'auto'. When omitted, set to 'auto' or 'cuda', automatically detects and routes execution to available CUDA acceleration. Overrides default GPU placement when specified.")
    parser.add_argument("--single_gpu", type=str_to_bool, nargs="?", const=True, help="Forces single-GPU inference even if multiple CUDA devices are available in the system. Multi-GPU pipelined sharding is bypassed, targeting the device specified by --gpu_index. Defaults to True since single-device execution is faster for models that fit in VRAM.")
    parser.add_argument("--gpu_index", type=int, help="Physical CUDA device index to execute on when single-GPU execution is active, or the primary device when multi-GPU is enabled. Must be within the range [0, device_count - 1]. Default is device 0 (same as train.py).")
    parser.add_argument("--use_cuda_graph", type=str_to_bool, nargs="?", const=True, help="Enables CUDA Graph capture for the static KV cache decoding step. Reduces CPU launch latency to near zero, substantially boosting token generation throughput on single-GPU CUDA setups. Set to False to disable graph capture.")
    parser.add_argument("--precision", type=str, choices=["fp16", "fp8", "fp32"], help="Computation precision mode: 'fp16' (bfloat16/float16 mixed precision), 'fp8' (hardware 8-bit tensor cores on Ada/Blackwell/Hopper GPUs), or 'fp32' (32-bit full float). FP16 provides optimal throughput and memory footprint on modern GPUs. Defaults to 'fp16'.")
    parser.add_argument("--autocorrect", type=str_to_bool, nargs="?", const=True, help="Automatically corrects misspelled words and character transpositions in user prompts before generation to prevent subword token fragmentation and attention collapse. Defaults to True.")
    parser.add_argument("--system_prompt", type=str, help="System instructions establishing model role, behavioral guidelines, and conversational tone. Prepended as the initial system turn in the conversation context.")

    cli = vars(parser.parse_args(argv))
    args = InferenceArgs(**{k: cli[k] for k in ("model_name", "models_base_dir") if k in cli})
    apply_options_overrides(args, stage=STAGE_INFER)
    for key, val in cli.items():
        setattr(args, key, val)
    return args


def parse_arguments() -> TrainingArgs:
    """Builds TrainingArgs for the unified training pipeline: defaults, overridden by the stage .options-*.json, overridden by the command line."""
    parser = argparse.ArgumentParser(
        description="Unified GPT Training, Fine-Tuning, and Optimization Orchestrator",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        argument_default=argparse.SUPPRESS,  # only arguments actually typed on the command line end up in the namespace
    )

    # 1. Primary Process Selector
    parser.add_argument("--training_process", type=str, required=True, choices=["Training", "Fine-Tuning", "Optimizing"], help="Target workflow stage to execute: 'Training' (pretraining), 'Fine-Tuning' (SFT), or 'Optimizing' (DPO). Determines which dataset directory, options file, and checkpoint format are loaded. See ARGUMENTS-TRAIN.md for in-depth pipeline details.")

    # 2. Model & Path Identification
    parser.add_argument("--model_name", type=str, required=True, help="Canonical model identifier (e.g. 'andres1xs-150M', 'andres1-1B'). Dictates model directory path, architecture configuration, options overrides, and checkpoint naming. Required for all operations.")
    parser.add_argument("--models_base_dir", type=str, help="Root filesystem directory where models, datasets, checkpoints, and telemetry logs reside. Defaults to 'bin' so paths resolve to bin/<model_name>/... Ensure adequate disk space on this volume.")
    parser.add_argument("--resume", type=str_to_bool, nargs="?", const=True, help="Determines whether to resume training from an existing stage checkpoint (.trn.chk, .sft.chk, or .dpo.chk). When enabled, restores model weights, optimizer moments, step counts, and accumulated training time. Set to False to restart training fresh from step 0.")

    # 3. Hyperparameters
    parser.add_argument("--batch_size", type=int, help="Physical mini-batch size processed per forward/backward step. In Multi-GPU Data Parallelism, this batch is divided evenly across all active GPUs. Higher values improve GPU Tensor Core saturation but consume more VRAM.")
    parser.add_argument("--accum_steps", type=int, help="Number of gradient accumulation sub-steps before executing an optimizer step and clearing gradients. Multiplies with physical batch_size to define the effective batch size (batch_size * accum_steps). Enables large effective batches without exceeding VRAM capacity.")
    parser.add_argument("--num_epochs", type=int, help="Total number of complete passes across the training dataset. Checkpoints track the current epoch and resume seamlessly from remaining epochs. If a checkpoint already completed requested epochs, execution notices and skips.")
    parser.add_argument("--learning_rate", type=float, help="Peak learning rate reached at the end of the warmup schedule. Governs AdamW parameter updates across training. Typical values: 3e-4 to 6e-4 for pretraining, 2e-5 to 5e-5 for SFT, and 5e-7 to 5e-6 for DPO.")
    parser.add_argument("--min_lr", type=float, help="Minimum learning rate floor for the cosine decay schedule. Prevents learning rate from reaching absolute zero, allowing continuous fine parameter adaptation late in training. Typically set to approximately 10%% of peak learning rate.")
    parser.add_argument("--warmup_steps", type=int, help="Number of initial training steps over which learning rate ramps linearly from zero to peak learning rate. Primary warmup mechanism during pretraining (STAGE_TRAIN). Stabilizes early attention dynamics and prevents weight disruption from initial large gradients.")
    parser.add_argument("--warmup_ratio", type=float, help="Fraction of total planned training steps dedicated to linear warmup during SFT and DPO stages. Calculated dynamically as int(total_steps * warmup_ratio). Standard values range from 0.03 (3%%) to 0.05 (5%%).")
    parser.add_argument("--weight_decay", type=float, help="L2 weight decay regularization coefficient applied by the optimizer to 2D weight matrices. Normalization scale factors and 1D biases are automatically excluded. Pretraining typically uses 0.05 to 0.10, whereas fine-tuning uses 0.01.")
    parser.add_argument("--eval_freq", type=int, help="Frequency in training steps at which validation evaluation and text generation sampling occur. Evaluates validation loss over --eval_iter batches and logs telemetry. Increase for production runs (e.g. 50 to 100) to minimize evaluation latency.")
    parser.add_argument("--eval_iter", type=int, help="Number of mini-batches sampled from the validation dataloader during each periodic evaluation pass. Higher values yield more accurate, lower-variance validation loss estimates. Lower values speed up periodic evaluation checkpoints.")
    parser.add_argument("--save_interval", type=int, help="Interval in training steps between periodic checkpoint saves to disk. Checkpoints use atomic file replacement with file locks to protect against corruption. Adjust based on step duration and training budget.")
    parser.add_argument("--step_limit", type=int, help="Hard upper limit on training steps to run in the current session before saving and exiting cleanly. Checkpoints are saved immediately when reached. Ideal for benchmarking, step-budgeted sessions, or scheduled runs.")

    # 4. Hardware, Acceleration, & Precision
    parser.add_argument("--device", type=str, help="Target compute device specification (e.g. 'cuda', 'cuda:0', 'cpu'). When omitted, automatically detects and uses CUDA if available. Overrides automatic multi-GPU orchestration when explicit single device is given.")
    parser.add_argument("--pol_device", type=str, help="Dedicated CUDA device specification for the trainable policy model during DPO preference optimization. In dual-GPU setups, setting this to cuda:0 and ref_device to cuda:1 splits memory cleanly across GPUs. See ARGUMENTS-TRAIN.md.")
    parser.add_argument("--ref_device", type=str, help="Dedicated CUDA device specification for the frozen reference model during DPO preference optimization. When multi-GPU is enabled, defaults to cuda:1 so the policy and reference models do not compete for VRAM.")
    parser.add_argument("--single_gpu", type=str_to_bool, nargs="?", const=True, help="Forces single-GPU execution even if multiple CUDA devices are present in the system. Multi-GPU wrappers (DP and PP) are completely bypassed. Targets the device specified by --gpu_index. Defaults to True; set --single_gpu false (or \"single_gpu\": false in the options file) to enable multi-GPU training.")
    parser.add_argument("--gpu_index", type=int, help="Physical CUDA GPU index to run on when --single_gpu is enabled, or to establish the primary master device when multi-GPU is enabled. Must be within the range [0, device_count - 1]. Default is device 0.")
    parser.add_argument("--precision", type=str, choices=["fp16", "fp8", "fp32"], help="Computation precision mode: 'fp16' (Automatic Mixed Precision via bfloat16/float16 autocast), 'fp8' (bf16 master weights with every Linear layer running on FP8 tensor cores via torchao float8 training; RTX 40/50 and Hopper GPUs, requires --compile, ~25%% faster and less VRAM than fp16), or 'fp32' (full single precision).")
    parser.add_argument("--compile", type=str_to_bool, nargs="?", const=True, help="Enables PyTorch 2.0 torch.compile graph capture with Triton kernel fusion. Can improve training throughput (tokens/sec) by 15%% to 30%%. Incurs JIT compilation overhead on initial forward and backward steps.")
    parser.add_argument("--coordinate_descent_tuning", type=str_to_bool, nargs="?", const=True, help="Requires --compile. Makes Inductor coordinate-descent autotune the launch configuration (block sizes, warps) of every compiled Triton kernel instead of using its heuristics; same math, only faster kernels. The fp8 amax/quantize/transpose kernels are ~30%% of a step and their heuristic configs run far below memory bandwidth on Blackwell: measured +9%% tok/sec on andres1s-350M-fp8 (2x RTX 5070 Ti, 69k -> 75k tok/sec, ~3.3 h saved on a 37 h run). Cost: every compile takes ~5x longer, i.e. a cold pretraining start needs ~15 min instead of ~3 min plus ~3 min at the first eval (both cached afterwards, warm restarts stay ~1 min). Worth it when a run compiles a handful of times and then trains for hours (static-shape pretraining); a net loss when variable batch shapes trigger many recompiles (each one pays the ~15 min again).")
    parser.add_argument("--activation_checkpointing", type=str_to_bool, nargs="?", const=True, help="Discards intermediate activations during forward pass and recomputes them during backward pass (torch.utils.checkpoint). Slashes activation VRAM by 60%% to 80%%, enabling larger batches or longer sequences. Tradeoff: reduces tokens/sec throughput by 25%% to 33%%.")
    parser.add_argument("--freeze_embeddings", type=str_to_bool, nargs="?", const=True, help="Freezes token and position embedding weights (requires_grad = False) during SFT or DPO. Eliminates optimizer state allocation (AdamW moments) for the large vocabulary embedding matrix, saving hundreds of megabytes of VRAM.")
    parser.add_argument("--multi_stage_micro_batching", type=int, help="Number of micro-batches used to pipeline execution across GPUs in pipelined model parallelism (MultiGpuGptModelPP). Ignored and inert during single-GPU execution or Data Parallelism (MultiGpuGptModelDP). See ARGUMENTS-TRAIN.md.")
    parser.add_argument("--multi_gpu_strategy", type=str, choices=[MULTI_GPU_DP, MULTI_GPU_PP], help="Multi-GPU acceleration strategy: 'data-parallelism' (replicates model on all GPUs, divides physical batch, and averages gradients) or 'parallel-pipeline' (splits model layers across GPUs). Data parallelism is recommended whenever the model fits on a single GPU.")
    parser.add_argument("--even_layers", type=str_to_bool, nargs="?", const=True, help="Used in pipelined model parallelism (parallel-pipeline) to distribute transformer blocks evenly 50/50 across dual GPUs. Default (False) uses an uneven 60/40 split to compensate for the heavy output head and loss computation on GPU 1.")
    parser.add_argument("--1f1b", dest="use_1f1b", type=str_to_bool, nargs="?", const=True, help="Enables One-Forward-One-Backward (1F1B) scheduling in pipelined model parallelism. Alternates forward and backward micro-steps once primed, capping peak in-flight activation memory to the number of pipeline stages.")
    parser.add_argument("--async_pcie", type=str_to_bool, nargs="?", const=True, help="Enables asynchronous, non-blocking PCIe transfers across GPUs in pipelined model parallelism. Allows inter-GPU tensor communication to overlap with transformer computation kernels.")

    # 5. Optimizers
    parser.add_argument("--use_muon", type=str_to_bool, nargs="?", const=True, help="Enables the hybrid CustomMuon + AdamW optimizer architecture. Updates internal 2D weight matrices via Newton-Schulz matrix sign iterations (saving up to 75%% optimizer memory) while using AdamW for embeddings and 1D norms. Set to False to force standard AdamW.")
    parser.add_argument("--muon_lr", type=float, help="Peak learning rate for the CustomMuon optimizer when hybrid Muon optimization is enabled. Because Newton-Schulz updates are normalized to unit spectral norm, Muon optimal learning rate is typically higher (0.001 to 0.002) than AdamW.")

    # 6. Data & Text Generation Options
    parser.add_argument("--override_data_folder", type=str, help="Explicit filesystem path to a custom dataset file or directory. Bypasses standard directory resolution (bin/<model_name>/data/<stage>/), allowing execution on arbitrary external datasets.")
    parser.add_argument("--train_ratio", type=float, help="Proportion of the dataset allocated to the training split in SFT instruction tuning and DPO preference optimization. In pretraining, controls the train/validation token split within each chunked text file. Default is 0.90 (90%%).")
    parser.add_argument("--test_ratio", type=float, help="Proportion of the dataset reserved for held-out evaluation testing in SFT and DPO splits. The remaining proportion (1.0 - train_ratio - test_ratio) is allocated to validation. Default is 0.05 (5%%).")
    parser.add_argument("--max_length", type=int, help="Maximum sequence length in tokens for tokenization and padding. Batches are dynamically padded up to the longest sequence in the batch or max_length. Automatically clamped to the model's architectural context_length.")
    parser.add_argument("--pad_to_multiple_of", type=int, help="SFT and DPO only (pretraining windows already have a fixed length). Rounds every batch's padded sequence length up to a multiple of this many tokens; 0 (default) pads exactly to the longest item in the batch. With 128 a 1024-token context sees at most 8 distinct sequence lengths instead of hundreds, and the token-budget packer sizes batches from the rounded lengths so peak memory is unchanged.")
    parser.add_argument("--chunk_size", type=int, help="Sequence chunk size (in tokens) for chunked cross-entropy loss computation. Slices the vocabulary projection into manageable chunks to prevent massive intermediate logit allocations. Values of 256 or 512 are recommended; 4096 risks OOM.")
    parser.add_argument("--recompute_lmhead", type=str_to_bool, nargs="?", const=True, help="Recomputes each chunk's LM head projection during backward instead of keeping its bf16 logits alive (saves tokens x vocab_size x 2 bytes of VRAM per GPU, costs one extra head matmul per step, ~3%% of step time). Default False; set to True only when that VRAM is needed.")
    parser.add_argument("--vocab_padded", type=str_to_bool, nargs="?", const=True, help="Automatically pads vocab_size from 50,257 to 50,304 when using standard GPT-2 tokenizers. Aligns matrix dimensions to multiples of 64 and 128 to unlock NVIDIA Tensor Core hardware acceleration. Set to False to preserve unpadded vocabulary dimensions.")
    parser.add_argument("--temperature", type=float, help="Sampling temperature for autoregressive text generation during evaluation passes. Value of 0.0 performs deterministic greedy argmax decoding. Values > 0.0 (e.g. 0.7) scale logits before softmax for creative diversity.")
    parser.add_argument("--top_k", type=int, help="Top-k filtering threshold for random sampling during text generation evaluation. Restricts token selection to the k highest-probability candidates, filtering out improbable tail tokens.")
    parser.add_argument("--save_timeout", type=float, help="Timeout in seconds when acquiring file system locks during atomic checkpoint saving. Protects against race conditions or locked file handles during concurrent operations.")
    parser.add_argument("--mask_prompt", type=str_to_bool, nargs="?", const=True, help="Controls prompt masking during instruction fine-tuning (STAGE_TUNE). When True (default), loss is computed strictly on assistant responses by masking prompts with -100 cross-entropy targets. Set to False to compute loss across both user prompts and assistant responses.")
    parser.add_argument("--verbose", type=str_to_bool, nargs="?", const=True, help="Enables verbose evaluation output, printing generated text responses directly to the terminal console during periodic evaluation intervals. Set to True to stream sample generations.")
    parser.add_argument("--test_mode", type=str_to_bool, nargs="?", const=True, help="Rapid debugging mode that truncates datasets to exactly 20 samples. Allows end-to-end verification of collation, forward/backward passes, optimizer stepping, and checkpointing within seconds.")
    parser.add_argument("--beta", type=float, help="Implicit reward temperature parameter beta in Direct Preference Optimization (STAGE_OPTIMIZE). Governs the trade-off between maximizing preferred response likelihood and penalizing policy divergence from the reference model (typically 0.05 to 0.2).")
    parser.add_argument("--precompute_total_steps", type=str_to_bool, nargs="?", const=True, help="Pre-scans and caches step counts across all text files in the corpus prior to pretraining, saving to steps_cache.json. Guarantees 100%% accurate global step counts, progress bars, and ETA reporting from step 1.")
    parser.add_argument("--json_precompute", type=str_to_bool, nargs="?", const=True, help="When enabled, precomputes reference model log-probabilities offline and caches them in JSON, eliminating reference model VRAM and speeding up DPO training on single GPUs.")

    cli = vars(parser.parse_args())
    args = TrainingArgs(**{k: cli[k] for k in ("training_process", "model_name", "models_base_dir") if k in cli})
    apply_options_overrides(args, stage=args.stage)
    for key, val in cli.items():
        setattr(args, key, val)
    return args
