# Copyright (c) Sebastian Raschka under Apache License 2.0 (see LICENSE.txt).
# Model initialization, device placement, and single-turn conversational generation engine.

import importlib
from pathlib import Path
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

import torch
import torch.nn as nn

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from argsutil import InferenceArgs
from gptmodel.GptModel import GptModel
from gptmodel.MultiGpuGptModelPP import MultiGpuGptModelPP
from gptmodel.GptModel_Quantized import QuantizedGptModel
from gptio.modelio import load_model_config, load_model_weights, resolve_model_path_and_config
from gptio.precision import get_supported_precision_dtype
from gptinfer.inference import (
    generate_text,
    get_tokenizer,
    format_chat_prompt,
    compute_generation_stats,
)
from gptinfer.spellcheck import init_spell_checker, autocorrect_prompt
from gptutils.consoleutils import print as printutil

print_plain = print
print = printutil


def setup_inference(args: InferenceArgs) -> Dict[str, Any]:
    """Initializes hardware, model, weights, tokenizer, and spell-checker context."""
    spell_checker = init_spell_checker() if args.autocorrect else None
    if spell_checker:
        print("[SpellCheck] Autocorrect initialized (SymSpell dictionary-based cleanup active).")

    # Determine device
    gpu_idx = args.gpu_index
    if args.device is None or args.device == "auto":
        device = torch.device(f"cuda:{gpu_idx}" if torch.cuda.is_available() else "cpu")
    elif args.device.startswith("cuda"):
        if ":" in args.device:
            device = torch.device(args.device)
        else:
            device = torch.device(f"cuda:{gpu_idx}" if torch.cuda.is_available() else "cpu")
    else:
        device = torch.device(args.device)

    num_gpus = torch.cuda.device_count() if (device.type == "cuda" and not args.single_gpu) else 0  # --device cpu never shards onto GPUs
    use_cuda_graph = (args.use_cuda_graph) and (num_gpus <= 1)

    # Resolve model configuration
    loaded_config = load_model_config(args)

    # Determine precision dtype
    model_dtype = get_supported_precision_dtype(device, precision=args.precision)

    print("=" * 60)
    print("           Interactive GPT Conversation Console")
    print("=" * 60)
    print(f"Model Target    : {args.model_name}")
    print(f"Precision       : {args.precision.upper()} (dtype: {model_dtype})")
    print(f"Device          : {device} (Available GPUs: {num_gpus})")
    sampling_info = f"Temperature     : {args.temperature}"
    if args.adaptive_temp:
        sampling_info += f" (Adaptive [{args.temp_min} - {args.temp_max}])"
    sampling_info += f" | Top-K: {args.top_k} | Top-P: {args.top_p}"
    if args.min_p is not None:
        sampling_info += f" | Min-P: {args.min_p}"
    print(sampling_info)
    if args.system_prompt and str(args.system_prompt).strip():
        print(f"System Prompt   : {str(args.system_prompt).strip()}")
    print("=" * 60)

    if loaded_config:
        config = loaded_config.copy()
        if config.get("vocab_size") == 50257:
            config["vocab_size"] = 50304  # ChatML special tokens live above 50,256; mirrors train.py's --vocab_padded default
    else:
        config = {
            "vocab_size": 50257,
            "context_length": 1024,
            "emb_dim": 768,
            "n_heads": 12,
            "n_kv_groups": 12,
            "n_layers": 12,
            "drop_rate": 0.0,
            "qkv_bias": True,
            "sliding_window_size": None,
        }

    if "n_kv_groups" not in config:
        config["n_kv_groups"] = config.get("n_heads", 12)
    if "n_kv_producing_layers" not in config:
        config["n_kv_producing_layers"] = config.get("n_layers", 12)

    model_cls = GptModel 
    multi_gpu_cls = MultiGpuGptModelPP
    model = model_cls(config)

    # Move model to target device & precision
    model.to(device=device, dtype=model_dtype)

    if model_cls == QuantizedGptModel:
        model_path, _ = resolve_model_path_and_config(args.model_name, models_dir=args.models_base_dir)
        mod = importlib.import_module("gpt_quantized")
        try:
            raw_sd = torch.load(model_path, map_location="cpu", weights_only=True)
        except Exception:
            raw_sd = torch.load(model_path, map_location="cpu", weights_only=False)
        if isinstance(raw_sd, dict) and ("model_state_dict" in raw_sd or "state_dict" in raw_sd):
            sd = raw_sd.get("model_state_dict", raw_sd.get("state_dict"))
        else:
            sd = raw_sd
        if any("weight_packed" in k for k in sd.keys()):
            load_model_weights(model, args, device=device)
        else:
            mod.quantize_from_state_dict(model, sd)
            print(f"[gptstart] Quantized float weights on-the-fly from: {model_path}")
    else:
        load_model_weights(model, args, device=device)

    # Handle multi-GPU sharding if available
    if num_gpus > 1 and multi_gpu_cls is not None:
        gpu_devices = [torch.device(f"cuda:{(gpu_idx + i) % num_gpus}") for i in range(num_gpus)]
        print(f"Multi-GPU: Sharding {config['n_layers']} layers across {num_gpus} GPUs via Pipeline Parallelism (primary={device}).")
        model = multi_gpu_cls(model, devices=gpu_devices)
        use_cuda_graph = False

    model.eval()

    tokenizer = get_tokenizer(config, args)
    context_window = config.get("context_length", 1024)

    # Determine EOS token IDs
    eos_id = [tokenizer.eos_id]
    if hasattr(tokenizer, "encode"):
        detected_eos = []
        for special in ["<|im_end|>", "<|endoftext|>"]:
            try:
                res = tokenizer.encode(special, allowed_special={special})
                if res and isinstance(res, list) and len(res) == 1:
                    detected_eos.extend(res)
            except Exception:
                pass
        if detected_eos:
            eos_id = list(set(detected_eos))

    first_device = device if (num_gpus <= 1 or args.single_gpu) else torch.device("cuda:0")
    stop_strings = ["<|im_end|>", "<|im_start|>", "<|endoftext|>"]

    return {
        "model": model,
        "tokenizer": tokenizer,
        "spell_checker": spell_checker,
        "config": config,
        "device": device,
        "first_device": first_device,
        "use_cuda_graph": use_cuda_graph,
        "stop_strings": stop_strings,
        "eos_id": eos_id,
        "context_window": context_window,
        "args": args,
    }


def run_generation(
    ctx: Dict[str, Any],
    conversation_messages: List[Dict[str, str]],
    user_input: str,
    stream: bool = True,
    seed: Optional[int] = None,
) -> Tuple[str, Dict[str, Any]]:
    """Executes a single conversational generation turn and updates conversation_messages. seed overrides args.seed for this turn."""
    model = ctx["model"]
    tokenizer = ctx["tokenizer"]
    spell_checker = ctx["spell_checker"]
    first_device = ctx["first_device"]
    use_cuda_graph = ctx["use_cuda_graph"]
    stop_strings = ctx["stop_strings"]
    eos_id = ctx["eos_id"]
    context_window = ctx["context_window"]
    args = ctx["args"]

    if spell_checker:
        cleaned_input, corrections = autocorrect_prompt(user_input, spell_checker)
        user_input = cleaned_input
    else:
        cleaned_input = user_input

    if stream:
        print_plain(f"User (cleaned): {cleaned_input}")

    if not any(m.get("role") == "system" for m in conversation_messages):
        sys_prompt = args.system_prompt
        if sys_prompt and str(sys_prompt).strip():
            conversation_messages.insert(0, {"role": "system", "content": str(sys_prompt).strip()})

    conversation_messages.append({"role": "user", "content": user_input})
    prompt_text = format_chat_prompt(conversation_messages)

    encoded_tokens = tokenizer.encode(prompt_text)

    # The reply gets whatever the context window leaves after the prompt; a long conversation is trimmed to its most recent
    # tokens so that at least half the window stays available for the reply. Generation also stops at an end-of-sequence token.
    max_prompt_len = max(1, context_window - context_window // 2)
    if len(encoded_tokens) > max_prompt_len:
        encoded_tokens = encoded_tokens[-max_prompt_len:]

    input_tensor = torch.tensor(encoded_tokens, device=first_device).unsqueeze(0)
    prompt_len = input_tensor.shape[1]
    allowed_new_tokens = max(1, context_window - prompt_len)

    if torch.cuda.is_available():
        torch.cuda.synchronize()
    if (seed if seed is not None else args.seed) is not None:
        torch.manual_seed(seed if seed is not None else args.seed)
    t0 = time.time()

    if stream:
        print_plain("Assistant: ", end="", flush=True)

    stream_buffer = ""
    def token_callback(tid: int) -> None:
        nonlocal stream_buffer
        try:
            t_str = tokenizer.decode([tid])
            stream_buffer += t_str
            is_prefix = False
            for stop_s in stop_strings:
                if stop_s.startswith(stream_buffer):
                    is_prefix = True
                    break
                if stop_s in stream_buffer:
                    return
            if is_prefix:
                return
            print_plain(stream_buffer, end="", flush=True)
            stream_buffer = ""
        except Exception:
            pass

    output_tokens = generate_text(
        model=model,
        idx=input_tensor,
        max_new_tokens=allowed_new_tokens,
        context_size=context_window,
        use_cache=args.use_cache,
        use_cuda_graph=use_cuda_graph,
        temperature=args.temperature,
        top_k=args.top_k,
        top_p=args.top_p,
        min_p=args.min_p,
        adaptive_temp=args.adaptive_temp,
        temp_min=args.temp_min,
        temp_max=args.temp_max,
        repetition_penalty=args.repetition_penalty,
        no_repeat_ngram=args.no_repeat_ngram,
        eos_id=eos_id,
        stream_callback=token_callback if stream else None,
        stop_strings=stop_strings,
        tokenizer=tokenizer
    )

    if torch.cuda.is_available():
        torch.cuda.synchronize()
    elapsed_time = time.time() - t0
    if stream:
        print("\n", flush=True)

    generated_token_ids = output_tokens[0, prompt_len:].tolist()
    assistant_response = tokenizer.decode(generated_token_ids).strip()

    for special_stop in ["<|im_end|>", "<|im_start|>", "<|endoftext|>"]:
        if assistant_response.endswith(special_stop):
            assistant_response = assistant_response[:-len(special_stop)].strip()

    for stop_seq in stop_strings:
        if stop_seq in assistant_response:
            assistant_response = assistant_response.split(stop_seq)[0].strip()

    stats = compute_generation_stats(assistant_response, len(generated_token_ids), elapsed_time)
    stats["allowed_new_tokens"] = allowed_new_tokens  # the window left for the reply: a reply this long ran into the context limit

    clean_content = assistant_response
    if "<think>" in clean_content and "</think>" in clean_content:
        clean_content = clean_content.split("</think>")[-1].strip()
    conversation_messages.append({"role": "assistant", "content": clean_content})

    if hasattr(model, "reset_kv_cache"):
        model.reset_kv_cache()
    elif hasattr(model, "raw_model") and hasattr(model.raw_model, "reset_kv_cache"):
        model.raw_model.reset_kv_cache()

    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    return assistant_response, stats
