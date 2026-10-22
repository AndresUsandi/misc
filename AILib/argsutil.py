# Copyright (c) Sebastian Raschka under Apache License 2.0 (see LICENSE.txt).
# Command-line argument parsers for GPT Inference and Training pipelines.

import argparse
from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Any, List, Optional

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from gptio.options import apply_options_overrides
from gptio.pathutil import (
    MULTI_GPU_DP,
    MULTI_GPU_DP_ZERO1,
    MULTI_GPU_PP,
    STAGE_TRAIN,
    STAGE_TUNE,
    STAGE_OPTIMIZE,
    STAGE_INFER,
    CHECKPOINT_TRN_EXT,
    CHECKPOINT_SFT_EXT,
    CHECKPOINT_DPO_EXT,
)
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
    temperature: float = 0.7
    top_k: Optional[int] = 50
    top_p: float = 0.9
    min_p: Optional[float] = None
    adaptive_temp: bool = False
    temp_min: float = 0.15
    temp_max: float = 0.85
    repetition_penalty: float = 1.05
    no_repeat_ngram: int = 0
    use_cache: bool = True
    use_cuda_graph: bool = True
    autocorrect: bool = True
    system_prompt: str = "You are a helpful and coherent AI assistant."
    seed: Optional[int] = None


@dataclass
class TrainingArgs(ModelArgs):
    """All train.py options. Value precedence: command line > <model_name>.options-<stage>.json > these defaults."""
    training_process: Optional[str] = None
    resume: bool = True
    batch_size: int = 4
    accum_steps: int = 1
    num_epochs: int = 1
    num_epochs_dataset_specific: Optional[Any] = None  # options file only, any stage: {"wikipedia": 4} or [{"wikipedia": 4}, {"cosmopedia": 3}] = passes over that dataset folder across the run (unlisted folders: num_epochs; 0 excludes one)
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
    max_autotune: bool = False
    activation_checkpointing: bool = False
    freeze_embeddings: bool = False
    multi_stage_micro_batching: int = 4
    multi_gpu_strategy: str = MULTI_GPU_DP
    even_layers: bool = False
    use_1f1b: bool = False
    async_pcie: bool = False
    use_muon: bool = False
    use_torchao_adamw8bit: bool = False
    use_bf16_for_muon_momentum: bool = False
    use_autocast_weight_cache: bool = False
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
    checkpoint_keep_n: int = 10
    mask_prompt: bool = True
    verbose: bool = False
    test_mode: bool = False
    beta: float = 0.1
    dpo_sft_weight: float = 0.5
    dpo_truncate_long_pairs: bool = False
    dpo_freeze_below_layer: Optional[int] = None  # DPO: freeze the embeddings and transformer blocks 0..N-1; only blocks N.. and the final norm train (None = everything trains)
    dpo_replay_datasets: Optional[List[str]] = None  # DPO: names of the model's tuning datasets (folders under data/Tuning) replayed with the ordinary SFT loss during the DPO
    dpo_replay_weight: float = 1.0  # DPO: weight of that replayed SFT loss (1.0 = the same weight the fine-tuning stage gave it)
    dpo_replay_batch_size: int = 4  # DPO: sequences of replayed tuning data per micro-step
    precompute_total_steps: Optional[bool] = None  # None = decided by stage in parse_arguments (False for STAGE_TRAIN, True for STAGE_TUNE / STAGE_OPTIMIZE)
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
    parser.add_argument("--temperature", type=float, help="Softmax sampling temperature controlling response randomness and creativity. Setting to 0.0 enforces deterministic greedy decoding. Values between 0.6 and 0.8 provide balanced conversational responses, while higher values increase variability.")
    parser.add_argument("--top_k", type=int, help="Filters candidate tokens to the k highest-probability entries prior to sampling. Eliminates tail probabilities that could introduce nonsensical completions. Set to None to disable top-k filtering; default is 50.")
    parser.add_argument("--top_p", type=float, help="Nucleus sampling threshold retaining the cumulative top probability mass up to p. Dynamically adapts candidate set size depending on model confidence. Default is 0.9 (90%% cumulative probability).")
    parser.add_argument("--min_p", type=float, help="Minimum probability threshold relative to top token (e.g. 0.05). Prunes candidate tokens with prob < min_p * p_max. Set to None to disable.")
    parser.add_argument("--adaptive_temp", type=str_to_bool, nargs="?", const=True, help="Dynamically scales softmax temperature token-by-token based on Shannon entropy of model logits. Cools temperature down for confident/factual tokens and warms it up for open-ended/creative tokens.")
    parser.add_argument("--temp_min", type=float, help="Minimum temperature floor for confident/factual tokens during adaptive temperature scaling. Defaults to 0.15.")
    parser.add_argument("--temp_max", type=float, help="Maximum temperature ceiling for creative/open-ended tokens during adaptive temperature scaling. Defaults to 0.85.")
    parser.add_argument("--repetition_penalty", type=float, help="Penalty factor applied to logits of previously generated tokens to discourage repetition and loops. Values > 1.0 penalize repeated tokens, while 1.0 disables the penalty. The penalty covers every token already in the context (system prompt, questions, earlier turns), so keep it mild: strong values steer small models away from reusing the very words a correct answer needs. Default is 1.05.")
    parser.add_argument("--no_repeat_ngram", type=int, help="Exact-repeat ban: forbids any token that would complete an n-gram (a run of n tokens) already present in the reply being generated, so a verbatim phrase or sentence loop cannot form; ordinary reuse of words stays allowed because only the exact n-token continuation is blocked. A hard ban, unlike the soft tax of --repetition_penalty, and it never looks at the prompt or earlier turns. 0 disables the feature; 1 or more enables it with that n-gram size (3-5 is sensible; 1 forbids any token from appearing twice). Special tokens are never banned. Default is 0.")
    parser.add_argument("--use_cache", type=str_to_bool, nargs="?", const=True, help="Enables static Key-Value (KV) attention caching to accelerate autoregressive decoding. Eliminates quadratic recomputation of previous token representations, drastically improving generation speed. Set to False to disable KV caching for debugging.")
    parser.add_argument("--device", type=str, help="Target execution device: 'cuda', 'cuda:N', 'cpu', or 'auto'. When omitted, set to 'auto' or 'cuda', automatically detects and routes execution to available CUDA acceleration. Overrides default GPU placement when specified.")
    parser.add_argument("--single_gpu", type=str_to_bool, nargs="?", const=True, help="Forces single-GPU inference even if multiple CUDA devices are available in the system. Multi-GPU pipelined sharding is bypassed, targeting the device specified by --gpu_index. Defaults to True since single-device execution is faster for models that fit in VRAM.")
    parser.add_argument("--gpu_index", type=int, help="Physical CUDA device index to execute on when single-GPU execution is active, or the primary device when multi-GPU is enabled. Must be within the range [0, device_count - 1]. Default is device 0 (same as train.py).")
    parser.add_argument("--use_cuda_graph", type=str_to_bool, nargs="?", const=True, help="Enables CUDA Graph capture for the static KV cache decoding step. Reduces CPU launch latency to near zero, substantially boosting token generation throughput on single-GPU CUDA setups. Set to False to disable graph capture.")
    parser.add_argument("--precision", type=str, choices=["fp16", "fp8", "fp32"], help="Computation precision mode: 'fp16' (bfloat16/float16 mixed precision), 'fp8' (hardware 8-bit tensor cores on Ada/Blackwell/Hopper GPUs), or 'fp32' (32-bit full float). FP16 provides optimal throughput and memory footprint on modern GPUs. Defaults to 'fp16'.")
    parser.add_argument("--autocorrect", type=str_to_bool, nargs="?", const=True, help="Automatically corrects misspelled words and character transpositions in user prompts before generation to prevent subword token fragmentation and attention collapse. Defaults to True.")
    parser.add_argument("--system_prompt", type=str, help="System instructions establishing model role, behavioral guidelines, and conversational tone. Prepended as the initial system turn in the conversation context.")
    parser.add_argument("--seed", type=int, help="Random seed applied (torch.manual_seed) before every generation turn so sampled outputs are reproducible run to run. Default None (non-deterministic sampling).")

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
    parser.add_argument("--resume", type=str_to_bool, nargs="?", const=True, help=f"Determines whether to resume training from an existing stage checkpoint ({CHECKPOINT_TRN_EXT}, {CHECKPOINT_SFT_EXT}, or {CHECKPOINT_DPO_EXT}). When enabled, restores model weights, optimizer moments, step counts, and accumulated training time. Set to False to restart training fresh from step 0.")

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
    parser.add_argument("--precision", type=str, choices=["fp16", "fp8", "fp32"], help="Computation precision mode: 'fp16' (Automatic Mixed Precision via bfloat16/float16 autocast), 'fp8' (every Linear layer running on FP8 tensor cores via torchao float8 training; RTX 40/50 and Hopper GPUs, requires --compile, ~25%% faster and less VRAM than fp16), or 'fp32' (full single precision). In every mode the trainable weights and optimizer states are kept in fp32 (master weights); bf16/fp16 weights silently drop most optimizer steps once the learning rate decays below ~1e-4.")
    parser.add_argument("--compile", type=str_to_bool, nargs="?", const=True, help="Enables PyTorch 2.0 torch.compile graph capture with Triton kernel fusion. Can improve training throughput (tokens/sec) by 15%% to 30%%. Incurs JIT compilation overhead on initial forward and backward steps.")
    parser.add_argument("--coordinate_descent_tuning", type=str_to_bool, nargs="?", const=True, help="Requires --compile. Makes Inductor coordinate-descent autotune the launch configuration (block sizes, warps) of every compiled Triton kernel instead of using its heuristics; same math, only faster kernels. The fp8 amax/quantize/transpose kernels are ~30%% of a step and their heuristic configs run far below memory bandwidth on Blackwell: measured +9%% tok/sec on andres1s-350M-fp8 (2x RTX 5070 Ti, 69k -> 75k tok/sec, ~3.3 h saved on a 37 h run). Cost: every compile takes ~5x longer, i.e. a cold pretraining start needs ~15 min instead of ~3 min plus ~3 min at the first eval (both cached afterwards, warm restarts stay ~1 min). Worth it when a run compiles a handful of times and then trains for hours (static-shape pretraining); a net loss when variable batch shapes trigger many recompiles (each one pays the ~15 min again).")
    parser.add_argument("--max_autotune", type=str_to_bool, nargs="?", const=True, help="Requires --compile. Compiles with Inductor's max-autotune-no-cudagraphs mode: every matmul is benchmarked against Triton-generated alternatives and every fused kernel's launch configuration is coordinate-descent tuned (this mode includes --coordinate_descent_tuning). Same math; the kernels that win differ from cuBLAS only in summation order (measured on andres1s-350M-fp8: loss 11.0380 vs 11.0387 on the same batch and weights). Measured +3.4%% tok/sec over coordinate-descent tuning alone on andres1s-350M-fp8 (2x RTX 5070 Ti). Cost: a cold compile takes ~15 min instead of ~9 (cached afterwards); every new input shape re-tunes, so keep it off for SFT/DPO, whose variable sequence lengths would compile for an hour.")
    parser.add_argument("--multi_stage_micro_batching", type=int, help="Number of micro-batches used to pipeline execution across GPUs in pipelined model parallelism (MultiGpuGptModelPP). Ignored and inert during single-GPU execution or Data Parallelism (MultiGpuGptModelDP). See ARGUMENTS-TRAIN.md.")
    parser.add_argument("--multi_gpu_strategy", type=str, choices=[MULTI_GPU_DP, MULTI_GPU_DP_ZERO1, MULTI_GPU_PP], help="Multi-GPU acceleration strategy. 'data-parallelism' (MultiGpuGptModelDP): every GPU holds the whole model and trains on its share of each batch; once per optimizer update the gradients are averaged onto the primary GPU, which alone holds the fp32 master weights plus the entire optimizer state (16 bytes per parameter with AdamW: 4 weight + 4 gradient + 8 moments) and runs the update, then broadcasts the new weights. The primary's memory is the model-size ceiling (~650M parameters at 2k context on 16 GB) and all update traffic flows through it. 'data-parallelism-zero1' (MultiGpuGptModelZeRO1, ZeRO stage 1 / zero-redundancy optimizer): identical forward/backward and identical arithmetic, but every parameter has an owner GPU that keeps its fp32 master and optimizer state and updates it; the update becomes a reduce-scatter (each owner receives only its shard's gradients), a per-shard optimizer step on every GPU in parallel, and an all-gather of the updated shards. Per GPU: weights + gradients + 1/N of the optimizer state (12 bytes/param on 2 GPUs, 9.3 on 6), so the ceiling rises (~900M on 2 x 16 GB, ~1.5B on 6) and traffic is spread evenly instead of funnelled through one card; nothing crosses the bus between micro-steps, so it is as bus-friendly as plain data parallelism. Checkpoints are interchangeable between the two. 'parallel-pipeline' (MultiGpuGptModelPP): splits the model's layers across GPUs so each holds and updates only its stage; the lowest traffic (activations at stage boundaries, per micro-step) and the way to train models that do not fit on one GPU even sharded, at the cost of pipeline bubbles unless many micro-batches are in flight (see --multi_stage_micro_batching, --1f1b). Use data parallelism while the model fits, zero1 when the optimizer state is what does not fit, the pipeline when the model itself does not.")
    parser.add_argument("--even_layers", type=str_to_bool, nargs="?", const=True, help="Used in pipelined model parallelism (parallel-pipeline) to distribute transformer blocks evenly 50/50 across dual GPUs. Default (False) uses an uneven 60/40 split to compensate for the heavy output head and loss computation on GPU 1.")
    parser.add_argument("--1f1b", dest="use_1f1b", type=str_to_bool, nargs="?", const=True, help="Enables One-Forward-One-Backward (1F1B) scheduling in pipelined model parallelism. Alternates forward and backward micro-steps once primed, capping peak in-flight activation memory to the number of pipeline stages.")
    parser.add_argument("--async_pcie", type=str_to_bool, nargs="?", const=True, help="Enables asynchronous, non-blocking PCIe transfers across GPUs in pipelined model parallelism. Allows inter-GPU tensor communication to overlap with transformer computation kernels.")

    # 5. Optimizers
    parser.add_argument("--use_muon", type=str_to_bool, nargs="?", const=True, help="Enables the hybrid CustomMuon + AdamW optimizer architecture. Updates internal 2D weight matrices via Newton-Schulz matrix sign iterations (saving up to 75%% optimizer memory) while using AdamW for embeddings and 1D norms. Set to False to force standard AdamW.")
    parser.add_argument("--muon_lr", type=float, help="Peak learning rate for the CustomMuon optimizer when hybrid Muon optimization is enabled. Because Newton-Schulz updates are normalized to unit spectral norm, Muon optimal learning rate is typically higher (0.001 to 0.002) than AdamW.")

    # VRAM consumption optimizations parameters - start
    parser.add_argument("--activation_checkpointing", type=str_to_bool, nargs="?", const=True, help="Discards intermediate activations during forward pass and recomputes them during backward pass (torch.utils.checkpoint). Slashes activation VRAM by 60%% to 80%%, enabling larger batches or longer sequences. Tradeoff: reduces tokens/sec throughput by 25%% to 33%%.")
    parser.add_argument("--recompute_lmhead", type=str_to_bool, nargs="?", const=True, help="Recomputes each chunk's LM head projection during backward instead of keeping its bf16 logits alive (saves tokens x vocab_size x 2 bytes of VRAM per GPU, costs one extra head matmul per step, ~3%% of step time). Default False; set to True only when that VRAM is needed.")
    parser.add_argument("--chunk_size", type=int, help="Sequence chunk size (in tokens) for chunked cross-entropy loss computation. Slices the vocabulary projection into manageable chunks to prevent massive intermediate logit allocations. Values of 256 or 512 are recommended; 4096 risks OOM.")
    parser.add_argument("--freeze_embeddings", type=str_to_bool, nargs="?", const=True, help="Freezes token and position embedding weights (requires_grad = False) during SFT or DPO. Eliminates optimizer state allocation (AdamW moments) for the large vocabulary embedding matrix, saving hundreds of megabytes of VRAM.")
    parser.add_argument("--use_torchao_adamw8bit", type=str_to_bool, nargs="?", const=True, help="Stores the AdamW optimizer state in 8 bits (torchao.optim.AdamW8bit) instead of fp32, for every parameter AdamW manages (all of them by default; embeddings and norms when --use_muon is on). The update rule is unchanged (AdamW with decoupled weight decay and bias correction, same lr/betas/eps/weight_decay); only the two moment buffers (exp_avg, exp_avg_sq) are stored block-wise quantized: blocks of 256 values with one fp32 scale each, dequantized on the fly inside the torch.compile'd step (parameters under 4096 elements, i.e. norm gains, stay fp32). Master weights and gradients stay fp32, so the per-parameter footprint on the optimizer GPU (cuda:0 in data parallelism) drops from 16 bytes (4 weight + 4 grad + 8 moments) to ~10 bytes: a 911M model needs ~8.5 GiB instead of ~13.6 GiB before activations, which is what lets a 700M-900M model train on a 16 GB card with fp32 masters and no optimizer sharding. Quality: 8-bit block-wise moments match fp32 AdamW on language-model pretraining and fine-tuning within noise (Dettmers et al. 2022, '8-bit Optimizers via Block-wise Quantization', the bitsandbytes method torchao reimplements); the residual risk is quantization noise in the second moment at very low learning rates late in a cosine schedule, which has not mattered in practice. Costs and caveats: CUDA only; the first optimizer step compiles (~30 s, cached); the lr lives in a tensor (set_optimizer_lr fills it in place); checkpoints store the quantized moments and resume restores them (the loader's NaN scan reads the per-block scales). Decide before a run starts and keep it for the whole run (including SFT/DPO resumes of that stage): fp32 and 8-bit moments cannot be loaded into each other, so flipping the flag mid-run makes the checkpoint loader print a notice and resume with freshly initialized moments (the model weights and step counters are kept). Default False: plain fused AdamW, identical to every run before this option existed.")
    parser.add_argument("--use_bf16_for_muon_momentum", type=str_to_bool, nargs="?", const=True, help="Stores the CustomMuon momentum buffer (the running average of past gradients that Muon orthogonalizes into every update, one buffer per 2D weight matrix) in bf16 instead of the fp32 it otherwise inherits from the fp32 master weights. Halves that part of the optimizer state (2 instead of 4 bytes per 2D parameter: ~1.4 GiB on the 774M, ~0.6 GiB on the 355M) and shrinks the checkpoint by the same amount; nothing else changes (master weights, gradients, the Newton-Schulz iteration and the AdamW moments all stay as they are). Why this is safe where bf16 master weights are not (see --precision): the weight problem is a tiny update landing on a large value (a 1e-4 step onto a 0.03 weight is below bf16 resolution and rounds back to the old value, so the weight silently stops learning); the momentum buffer instead receives a whole gradient every step, 5-30%% of its own magnitude, 25-150x above the bf16 half-ulp, so nothing is absorbed. What is given up: each step's add rounds to ~0.2%% relative error, which with the 0.95 decay (~20-step memory) accumulates to ~0.5%% noise in the momentum direction, two orders of magnitude below the minibatch gradient noise itself, and Newton-Schulz normalizes the update magnitude anyway, so only the direction wobbles. The reference Muon implementation (modded-nanogpt speedrun records) keeps its momentum in bf16 and runs Newton-Schulz in bf16 too; this code keeps Newton-Schulz in fp32, so it stays the more conservative variant. bf16 specifically, never fp16: bf16 has the fp32 exponent range, so no overflow/underflow handling is needed. Measured against an otherwise identical fp32-momentum run (25M e2e model, same seed, deterministic kernels, 20 pretraining + 16 SFT + 10 DPO optimizer updates, fp16 autocast on an RTX 2080 SUPER): every logged train/val loss matched to the printed 3 decimals (largest difference 0.001), perplexities agreed to 4-5 significant digits, DPO margins +1.069 vs +1.071; the two trajectories drift apart as any two differently-rounded runs do, 0.17%% median relative Frobenius difference of the weights after the 20 pretraining updates and 1.6%% after SFT, the momentum buffers themselves differing by 0.7%% then 2.6%%, i.e. a perturbed but equivalent run; Muon state 96 MiB -> 48 MiB, checkpoint 48 MB smaller, allocated VRAM at the eval points 0.74 -> 0.69 GB. Resume semantics (verified both ways): the flag is authoritative, not the checkpoint. With the flag on, fp32 buffers from an older checkpoint are cast to bf16 right after loading (the fp32 copies exist only transiently during the load); with the flag off, bf16 buffers from a newer checkpoint load back as fp32 (torch casts optimizer state to the parameter dtype), so flipping it mid-run in either direction is harmless. No effect without --use_muon (AdamW-only runs have no Muon buffer) and none on the AdamW moments (--use_torchao_adamw8bit covers those). Default False: fp32 buffers, identical to every run before this option existed.")
    parser.add_argument("--use_autocast_weight_cache", type=str_to_bool, nargs="?", const=True, help="Turns torch.autocast's weight cache back on for the single-GPU training forward of pretraining and SFT (calc_loss_batch), which otherwise always runs with cache_enabled=False. What the cache does: inside an autocast region, the first time an fp32 weight is needed in bf16/fp16, autocast makes the low-precision copy and keeps it until the region ends, so a weight used several times in one forward is cast once and every use shares that one copy. In this model the only weight used more than once per forward is the tied token embedding / LM head: the chunked cross-entropy applies it once per chunk, ceil(tokens / --chunk_size) times per micro-batch (8 times at batch 4 x 1024 tokens with chunk_size 512). Without the cache each chunk gets its own copy and autograd keeps all of them until backward; with it there is one. Saving: (chunks - 1) x vocab_size x emb_dim x 2 bytes: ~720 MB on the 355M at batch 4 x 1024 / chunk 512 (7 x 103 MB), ~390 MB on the 774M at batch 1 x 1024 / chunk 256; measured on the 25M e2e model: reserved VRAM 1.77 -> 1.38 GB in SFT (8 chunks) and 1.98 -> 1.89 GB in pretraining (4 chunks). Cost, and why it is off by default: when the chunks share one copy, autograd sums their per-chunk gradients for that copy in the autocast dtype before the single cast back to fp32, instead of casting each chunk\'s gradient to fp32 first and summing in fp32. That is zero-mean rounding noise on the embedding / LM-head gradient only (every transformer block weight is used once per forward and is unaffected): measured 2.8e-4 relative in fp16 (one fp16 rounding, 2^-11); in bf16 (Ampere and newer) the rounding step is 8x coarser and with 7 adds expect ~0.2-0.5%% per step, two orders of magnitude below the minibatch gradient noise, and AdamW averages ~10 steps before using it. In the validation runs every logged loss matched the cache-off run to the printed 3 decimals and perplexity differed by 0.003%%; everything else in the model differed only at fp32-epsilon level (1e-7: the changed graph shape makes cuBLAS pick different kernels). Expected effect on model quality: not measurable; but bit-exactness with the default path is lost, so it is opt-in. The same memory is available exactly with --recompute_lmhead (recomputes the head projection per chunk in backward instead of keeping the copies, ~3%% step time, no numerical change), which is the first thing to reach for. Rejected together with --activation_checkpointing (parse error): with checkpointing the transformer blocks drop their weight copies right after use and only the cache would keep them alive (~2 bytes per parameter) for no benefit. Not applied to the DPO forwards, where it was measured to be pointless: numerically neutral (bitwise-identical weights with it on and off, because split_dpo_backward backpropagates the chosen and rejected graphs separately, so their partial gradients meet in fp32, and compute_logprobs_chunked recomputes the head per chunk inside a checkpoint) and no lower a peak (+50 MiB on the 25M model, since the cache pins the head copy that the checkpointed chunks would otherwise discard), so they always run without the cache. Also not applied to data parallelism (it computes on bf16 weight copies that need no cast) or to the pipeline-parallel forward (keeps its own rule: cache on unless checkpointing). Default False: identical to every run before this option existed.")
    # VRAM consumption optimizations parameters - end

    # 6. Data & Text Generation Options
    parser.add_argument("--override_data_folder", type=str, help="Explicit filesystem path to a custom dataset file or directory. Bypasses standard directory resolution (bin/<model_name>/data/<stage>/), allowing execution on arbitrary external datasets.")
    parser.add_argument("--train_ratio", type=float, help="Proportion of the dataset allocated to the training split in SFT instruction tuning and DPO preference optimization. In pretraining, controls the train/validation split of every text file's context windows (the validation windows are the tail of each file). Default is 0.90 (90%%).")
    parser.add_argument("--test_ratio", type=float, help="Proportion of the dataset reserved for held-out evaluation testing in SFT and DPO splits. The remaining proportion (1.0 - train_ratio - test_ratio) is allocated to validation. Default is 0.05 (5%%).")
    parser.add_argument("--max_length", type=int, help="Maximum sequence length in tokens for tokenization and padding. Batches are dynamically padded up to the longest sequence in the batch or max_length. Automatically clamped to the model's architectural context_length.")
    parser.add_argument("--pad_to_multiple_of", type=int, help="SFT and DPO only (pretraining windows already have a fixed length). Rounds every batch's padded sequence length up to a multiple of this many tokens; 0 (default) pads exactly to the longest item in the batch. With 128 a 1024-token context sees at most 8 distinct sequence lengths instead of hundreds, and the token-budget packer sizes batches from the rounded lengths so peak memory is unchanged.")
    parser.add_argument("--vocab_padded", type=str_to_bool, nargs="?", const=True, help="Automatically pads vocab_size from 50,257 to 50,304 when using standard GPT-2 tokenizers. Aligns matrix dimensions to multiples of 64 and 128 to unlock NVIDIA Tensor Core hardware acceleration. Set to False to preserve unpadded vocabulary dimensions.")
    parser.add_argument("--temperature", type=float, help="Sampling temperature for autoregressive text generation during evaluation passes. Value of 0.0 performs deterministic greedy argmax decoding. Values > 0.0 (e.g. 0.7) scale logits before softmax for creative diversity.")
    parser.add_argument("--top_k", type=int, help="Top-k filtering threshold for random sampling during text generation evaluation. Restricts token selection to the k highest-probability candidates, filtering out improbable tail tokens.")
    parser.add_argument("--save_timeout", type=float, help="Timeout in seconds when acquiring file system locks during atomic checkpoint saving. Protects against race conditions or locked file handles during concurrent operations.")
    parser.add_argument("--checkpoint_keep_n", type=int, help="Every N-th checkpoint save (any stage) keeps the previous checkpoint as a rollback point: instead of being overwritten by the next save, the backup is renamed to <model_name>-<YYYYMMDD-hhmmss>.chk.<stage> (its own save time; a rename, no copy). If training later goes wrong, rename the last good archive back to <model_name>.chk.<stage> and resume. Default 10 (with save_interval 2500: an archive every 25,000 steps); 0 disables. Archives are never loaded automatically and never deleted: prune them by hand.")
    parser.add_argument("--mask_prompt", type=str_to_bool, nargs="?", const=True, help="Controls prompt masking during instruction fine-tuning (STAGE_TUNE). When True (default), loss is computed strictly on assistant responses by masking prompts with -100 cross-entropy targets. Set to False to compute loss across both user prompts and assistant responses.")
    parser.add_argument("--verbose", type=str_to_bool, nargs="?", const=True, help="Enables verbose evaluation output, printing generated text responses directly to the terminal console during periodic evaluation intervals. Set to True to stream sample generations.")
    parser.add_argument("--test_mode", type=str_to_bool, nargs="?", const=True, help="Rapid debugging mode that truncates datasets to exactly 20 samples. Allows end-to-end verification of collation, forward/backward passes, optimizer stepping, and checkpointing within seconds.")
    parser.add_argument("--beta", type=float, help="Implicit reward temperature parameter beta in Direct Preference Optimization (STAGE_OPTIMIZE). Governs the trade-off between maximizing preferred response likelihood and penalizing policy divergence from the reference model (typically 0.05 to 0.2).")
    parser.add_argument("--dpo_sft_weight", type=float, help="DPO (STAGE_OPTIMIZE): weight of the ordinary SFT loss on the chosen answer (its mean per-token negative log-likelihood) added to the DPO loss, i.e. loss = DPO + weight x NLL(chosen) - the 'NLL on chosen' / RPO term of the Llama 3 recipe. Plain DPO only rewards a growing gap between the chosen and the rejected answer, so it is equally happy making both less likely as long as the rejected one falls faster, and the freed probability flows to something degenerate: with per-token-averaged log-probs and preference sets that mostly prefer the shorter answer, andres-350M-2-fp8v2c (2026-10-14) collapsed to 'answer in three words, then stop' within 180 updates while its margin and pair accuracy looked excellent. The term keeps the chosen answers themselves likely, so the gap can only grow by pushing the rejected answers down. Watch 'Chosen vs ref' in the log (policy minus reference log-prob of the chosen answers): it should hover near or above 0; a steady fall is the collapse starting. Default 0.5 (the NLL of a chosen answer is ~1.5-2.5 nats per token, so the term is of the same order as the DPO term's initial 0.69); 0 restores plain DPO.")
    parser.add_argument("--dpo_truncate_long_pairs", type=str_to_bool, nargs="?", const=True, help="DPO (STAGE_OPTIMIZE): keep preference pairs whose chosen or rejected answer runs past max_length by cutting the answer (prompt + the head of the answer, the end marker put back as the last token) instead of dropping the pair. Default False (drop). The model's context window caps max_length, so this is the only way to use long pairs (on andres-350M-2-fp8v2d 4.6%% of OffsetBias, 388 pairs with long rejected answers, was dropped at 1,024). Pairs whose prompt leaves fewer than 32 answer tokens are still dropped.")
    parser.add_argument("--dpo_freeze_below_layer", type=int, help="DPO (STAGE_OPTIMIZE): freeze the token and position embeddings (and the tied output head) and transformer blocks 0..N-1, so that only blocks N.. and the final norm are updated. Confines the DPO's perturbation to the upper part of the network: on andres-350M-2-fp8v3 every DPO run that moved all the weights by ~0.2%% cost ~40%% of GSM8K and flipped brittle facts ('the capital of Egypt is Thebes') within its first 40 updates, whatever the preference data. Default None (everything trains).")
    parser.add_argument("--dpo_replay_datasets", nargs="+", help="DPO (STAGE_OPTIMIZE): names of the model's fine-tuning datasets (folders under data/Tuning, e.g. gsm8k metamath_qa numinamath_cot) whose examples are replayed during the DPO with the ordinary SFT loss, --dpo_replay_batch_size sequences per micro-step at weight --dpo_replay_weight, next to the preference loss. The anti-forgetting remedy for a skill the preference pairs do not exercise: the 0.2 x NLL anchor on the chosen answers only protects what the pairs contain. Default None (no replay).")
    parser.add_argument("--dpo_replay_weight", type=float, help="DPO (STAGE_OPTIMIZE): weight of the replayed SFT loss (--dpo_replay_datasets). Default 1.0, the weight the fine-tuning stage gave that data.")
    parser.add_argument("--dpo_replay_batch_size", type=int, help="DPO (STAGE_OPTIMIZE): sequences of replayed fine-tuning data per micro-step (--dpo_replay_datasets); 4 sequences of up to max_length tokens add roughly one preference pair's worth of activations. Default 4.")
    parser.add_argument("--precompute_total_steps", type=str_to_bool, nargs="?", const=True, help="Makes the step plan (steps per epoch, hence the total updates the cosine LR schedule decays over) exact before the first step, in every stage, by scanning the data once and saving the counts to steps_cache.json. Pretraining (STAGE_TRAIN) tokenizes every file into its token cache before the first step anyway, so its counts are exact regardless and the flag only forces the scan (and the per-file report) up front; default False there. Fine-tuning and DPO (STAGE_TUNE / STAGE_OPTIMIZE) stream their JSON files with token-budget batching, so without the flag the first session plans from an estimate (a sample of 1,024 items per file) that is replaced by the exact count only after the first pass, and a later resume then re-plans on a slightly different horizon; with the flag the first epoch is streamed once on the CPU (no GPU work, nothing trained) to record the exact counts. Default True for those stages. The plan's source is printed with the [Training Plan] / [Streaming Loader] lines.")
    parser.add_argument("--json_precompute", type=str_to_bool, nargs="?", const=True, help="When enabled, precomputes reference model log-probabilities offline and caches them in JSON, eliminating reference model VRAM and speeding up DPO training on single GPUs.")

    cli = vars(parser.parse_args())
    args = TrainingArgs(**{k: cli[k] for k in ("training_process", "model_name", "models_base_dir") if k in cli})
    apply_options_overrides(args, stage=args.stage)
    for key, val in cli.items():
        setattr(args, key, val)
    if args.precompute_total_steps is None:
        args.precompute_total_steps = args.stage in (STAGE_TUNE, STAGE_OPTIMIZE)
    # Consistency of the VRAM options (checked after the options file and the command line are merged, so both sources are covered)
    if args.use_bf16_for_muon_momentum and not args.use_muon:
        parser.error("--use_bf16_for_muon_momentum requires --use_muon true: it only changes the dtype of the CustomMuon momentum buffer, and without Muon there is none (set both on the command line or in the options file).")
    if args.use_autocast_weight_cache and args.activation_checkpointing:
        parser.error("--use_autocast_weight_cache cannot be combined with --activation_checkpointing: with checkpointing the cache would pin the low-precision copy of every weight until the forward ends and only cost VRAM (set one or the other on the command line or in the options file).")
    return args
