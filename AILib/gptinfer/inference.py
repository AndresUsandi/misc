# Copyright (c) Sebastian Raschka under Apache License 2.0 (see LICENSE.txt).
# High-Performance Text Generation and Inference Utilities for GPT Models.

from pathlib import Path
import sys
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from tokenizers import Tokenizer
import tiktoken
import torch
import torch.nn as nn

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from argsutil import ModelArgs
from gptio.pathutil import resolve_path, TARGET_TOKENIZER, TOKENIZER_FILE
from gptutils.consoleutils import print

EOS_TOKEN: str = "<|endoftext|>"  # every supported tokenizer must define it: it is the pretraining document separator and the SFT/DPO pad token


def compute_wpm(text_or_words: Union[str, int], elapsed_sec: float) -> float:
    """
    Computes words per minute (WPM) given generated text (or word count) and elapsed duration in seconds.
    """
    if elapsed_sec <= 0:
        return 0.0
    if isinstance(text_or_words, int):
        word_count = text_or_words
    else:
        word_count = len(str(text_or_words).split())
    return (word_count / elapsed_sec) * 60.0


def compute_generation_stats(text: str, num_tokens: int, elapsed_sec: float) -> Dict[str, Any]:
    """
    Computes comprehensive inference telemetry: words, tokens, latency, WPM, and tok/sec.
    """
    words = len(text.split()) if text else 0
    wpm = (words / elapsed_sec * 60.0) if elapsed_sec > 0 else 0.0
    tps = (num_tokens / elapsed_sec) if elapsed_sec > 0 else 0.0
    return {
        "words": words,
        "tokens": num_tokens,
        "elapsed_sec": elapsed_sec,
        "wpm": wpm,
        "tokens_per_sec": tps,
    }


CUSTOM_SPECIAL_TOKENS: Dict[str, int] = {
    # Standard GPT-2 EOS
    "<|endoftext|>": 50256,
    # ChatML boundary tags
    "<|im_start|>": 50257,
    "<|im_end|>": 50258,
    # Phi boundary tags
    "<|user|>": 50259,
    "<|assistant|>": 50260,
    "<|system|>": 50261,
    "<|end|>": 50262,
    # LLaMA 3 boundary tags
    "<|begin_of_text|>": 50263,
    "<|end_of_text|>": 50264,
    "<|start_header_id|>": 50265,
    "<|end_header_id|>": 50266,
    "<|eot_id|>": 50267,
    # Padding & special execution tags
    "<|pad|>": 50268,
    "<|python_tag|>": 50269,
}

_CUSTOM_TIKTOKEN_ENCODING: Optional[tiktoken.Encoding] = None


def get_custom_tiktoken_encoding() -> tiktoken.Encoding:
    """
    Returns the singleton tiktoken Encoding with extended special tokens for
    ChatML, Phi, and LLaMA formats mapped into padded vocabulary slots (50256-50269).
    """
    global _CUSTOM_TIKTOKEN_ENCODING
    if _CUSTOM_TIKTOKEN_ENCODING is None:
        base = tiktoken.get_encoding("gpt2")
        _CUSTOM_TIKTOKEN_ENCODING = tiktoken.Encoding(
            name="gpt2_special",
            pat_str=base._pat_str,
            mergeable_ranks=base._mergeable_ranks,
            special_tokens=dict(CUSTOM_SPECIAL_TOKENS),
        )
    return _CUSTOM_TIKTOKEN_ENCODING


class SafeTokenizerWrapper:
    """
    Robust tokenizer wrapper providing a uniform interface across Hugging Face Tokenizers,
    tiktoken, and Transformers AutoTokenizer instances.
    """
    def __init__(self, base_tokenizer: Any, arch_family: str = "gpt2", vocab_size: int = 50304):
        self.base_tokenizer = base_tokenizer
        self.arch_family = arch_family
        self.vocab_size = vocab_size  # the model's (padded) embedding rows
        # tokens the tokenizer can actually produce (incl. special tokens); must fit in vocab_size
        self.n_vocab = base_tokenizer.get_vocab_size(with_added_tokens=True) if hasattr(base_tokenizer, "get_vocab_size") else getattr(base_tokenizer, "n_vocab", max(self.special_tokens.values()) + 1)
        self.eos_id = self.token_id(EOS_TOKEN)
        if self.eos_id is None:
            raise ValueError(f"Tokenizer for '{arch_family}' does not define the required special token {EOS_TOKEN}.")
        self.pad_id = self.eos_id  # SFT/DPO pad with the end-of-text token, as GPT-2 does

    def token_id(self, token: str) -> Optional[int]:
        """Id of a single (special) token, or None if the tokenizer does not know it."""
        if hasattr(self.base_tokenizer, "token_to_id"):  # Hugging Face tokenizers
            return self.base_tokenizer.token_to_id(token)
        ids = self.encode(token, allowed_special="all")
        return ids[0] if len(ids) == 1 else None

    @property
    def special_tokens(self) -> Dict[str, int]:
        if hasattr(self.base_tokenizer, "_special_tokens"):
            return self.base_tokenizer._special_tokens
        if hasattr(self.base_tokenizer, "get_vocab") and callable(self.base_tokenizer.get_vocab):
            vocab = self.base_tokenizer.get_vocab()
            special = {k: v for k, v in vocab.items() if isinstance(k, str) and k.startswith("<|") and k.endswith("|>")}
            if special:
                return special
        return dict(CUSTOM_SPECIAL_TOKENS)

    def get_vocab(self) -> Dict[str, int]:
        if hasattr(self.base_tokenizer, "get_vocab") and callable(self.base_tokenizer.get_vocab):
            return self.base_tokenizer.get_vocab()
        if hasattr(self.base_tokenizer, "_special_tokens"):
            return dict(self.base_tokenizer._special_tokens)
        return dict(CUSTOM_SPECIAL_TOKENS)

    def encode(self, text: str, allowed_special: Any = "all", **kwargs) -> list:
        if hasattr(self.base_tokenizer, "encode"):
            try:
                res = self.base_tokenizer.encode(text, allowed_special=allowed_special)
                return res.ids if hasattr(res, "ids") else res
            except TypeError:
                try:
                    res = self.base_tokenizer.encode(text)
                    return res.ids if hasattr(res, "ids") else res
                except Exception as e:
                    raise RuntimeError(f"Tokenizer encoding error for '{self.arch_family}': {e}")
            except Exception as e:
                raise RuntimeError(f"Tokenizer encoding error for '{self.arch_family}': {e}")

        raise RuntimeError(f"Underlying tokenizer object {type(self.base_tokenizer)} does not have an 'encode' method.")

    def decode(self, token_ids: Any, errors: str = "replace", skip_special_tokens: bool = False) -> str:
        if isinstance(token_ids, torch.Tensor):
            token_ids = token_ids.squeeze().tolist()
        if isinstance(token_ids, int):
            token_ids = [token_ids]

        # Try standard decoding first
        if hasattr(self.base_tokenizer, "decode"):
            try:
                return self.base_tokenizer.decode(token_ids, skip_special_tokens=skip_special_tokens)
            except TypeError:
                try:
                    return self.base_tokenizer.decode(token_ids)
                except Exception:
                    pass
            except Exception:
                pass

        # Per-token safe byte decoding fallback
        byte_chunks = []
        for tid in token_ids:
            try:
                if hasattr(self.base_tokenizer, "decode_single_token_bytes"):
                    byte_chunks.append(self.base_tokenizer.decode_single_token_bytes(tid))
                elif hasattr(self.base_tokenizer, "decode"):
                    byte_chunks.append(self.base_tokenizer.decode([tid]).encode("utf-8", errors="replace"))
                else:
                    byte_chunks.append(f"<{tid}>".encode("utf-8"))
            except Exception:
                byte_chunks.append(f"<{tid}>".encode("utf-8"))

        return b"".join(byte_chunks).decode("utf-8", errors=errors)



def resolve_tokenizer_file(spec: str, args: ModelArgs) -> Path:
    """
    Locates the tokenizer file a model-params "tokenizer" entry refers to: a file name inside the model folder (e.g. "tokenizer.json"),
    an absolute path, or a Hugging Face repo id (e.g. "Qwen/Qwen2.5-0.5B") whose tokenizer.json is downloaded into the model folder once.
    """
    declared = resolve_path(args.model_name, target=spec, models_dir=args.models_base_dir)
    if declared.is_file():
        return declared
    if "/" in spec and not spec.lower().endswith((".json", ".model")):
        dest = resolve_path(args.model_name, target=TARGET_TOKENIZER, models_dir=args.models_base_dir)
        if not dest.exists():
            from repos.modelrepo import download_file
            download_file(f"https://huggingface.co/{spec}/resolve/main/{TOKENIZER_FILE}", dest)
        return dest
    raise FileNotFoundError(
        f"Tokenizer '{spec}' declared in the model-params file was not found at '{declared}'. "
        f"Expected a tokenizer.json / tokenizer.model file in the model folder, an absolute path, or a Hugging Face repo id such as 'Qwen/Qwen2.5-0.5B'."
    )


def load_tokenizer_file(path: Path, arch: str, vocab_size: int) -> SafeTokenizerWrapper:
    """Loads a tokenizer file as a Hugging Face fast tokenizer JSON, a tiktoken BPE model, or a generic Hugging Face tokenizer; raises listing every failed attempt."""
    load_errors = []
    if path.suffix == ".json" or path.name == "tokenizer.json":
        try:
            return SafeTokenizerWrapper(Tokenizer.from_file(str(path)), arch_family=arch, vocab_size=vocab_size)
        except Exception as e:
            load_errors.append(f"{path.name} (HF JSON): {e}")
    try:
        from tiktoken.load import load_tiktoken_bpe
        mergeable = load_tiktoken_bpe(str(path))
        special = {
            "<|begin_of_text|>": 128000,
            "<|end_of_text|>": 128001,
            "<|start_header_id|>": 128006,
            "<|end_header_id|>": 128007,
            "<|eot_id|>": 128009,
        }
        special.update({f"<|reserved_{i}|>": 128002 + i for i in range(256) if 128002 + i not in special.values()})
        tok = tiktoken.Encoding(
            name=path.name,
            pat_str=r"(?i:'s|'t|'re|'ve|'m|'ll|'d)|[^\r\n\p{L}\p{N}]?\p{L}+|\p{N}{1,3}| ?[^\s\p{L}\p{N}]+[\r\n]*|\s*[\r\n]+|\s+(?!\S)|\s+",
            mergeable_ranks=mergeable,
            special_tokens=special,
        )
        return SafeTokenizerWrapper(tok, arch_family=arch, vocab_size=vocab_size)
    except Exception as e:
        load_errors.append(f"{path.name} (tiktoken BPE): {e}")
    try:
        return SafeTokenizerWrapper(Tokenizer.from_file(str(path)), arch_family=arch, vocab_size=vocab_size)
    except Exception as e:
        load_errors.append(f"{path.name} (HF generic): {e}")
    raise RuntimeError(f"Could not load tokenizer '{path}':" + "".join(f"\n  - {err}" for err in load_errors))


def get_tokenizer(config_or_arch: Any = None, args: Optional[ModelArgs] = None) -> SafeTokenizerWrapper:
    """
    Loads the tokenizer for a model. A model config (dict) may declare one under "tokenizer" (see resolve_tokenizer_file);
    absent or "gpt2" selects the built-in GPT-2 encoding extended with ChatML / Phi / LLaMA special tokens.
    Never falls back to an incompatible vocabulary: a declared tokenizer that cannot be loaded, or whose tokens do not fit
    the model's vocab_size, raises and stops execution.
    """
    arch = "gpt2"
    vocab_size = 50304
    spec = None
    if isinstance(config_or_arch, dict):
        arch = config_or_arch.get("arch_family", "gpt2").lower()
        vocab_size = config_or_arch.get("vocab_size", 50304)
        spec = config_or_arch.get("tokenizer")
    elif isinstance(config_or_arch, str):
        arch = config_or_arch.lower()

    if spec and str(spec).lower() != "gpt2":
        if args is None or not args.model_name:
            raise ValueError(f"get_tokenizer needs the model's ModelArgs to locate the declared tokenizer '{spec}'.")
        tok_file = resolve_tokenizer_file(str(spec), args)
        tokenizer = load_tokenizer_file(tok_file, arch, vocab_size)
        if tokenizer.n_vocab > vocab_size:
            raise ValueError(
                f"Tokenizer '{tok_file.name}' produces {tokenizer.n_vocab:,} token ids but the model's vocab_size is {vocab_size:,}. "
                f"Set vocab_size to at least {tokenizer.n_vocab:,} in the model-params file (ideally a multiple of 64 or 128 for Tensor Cores)."
            )
        print(f"[Tokenizer] Loaded {tok_file.name} ({tokenizer.n_vocab:,} tokens, {EOS_TOKEN}={tokenizer.eos_id}, model vocab_size={vocab_size:,}).")
        return tokenizer

    # Built-in GPT-2 / Andres1 encoding with extended special tokens (vocab_size <= 50304)
    if arch in ["gpt2", "andres1", "gpt", "custom"] and vocab_size <= 50304:
        try:
            tok = get_custom_tiktoken_encoding()
            return SafeTokenizerWrapper(tok, arch_family="gpt2", vocab_size=vocab_size)
        except Exception as e:
            raise RuntimeError(f"Failed to load custom tiktoken encoding with special tokens: {e}")

    # Strict failure - do NOT silently fall back to wrong or generic encodings
    raise FileNotFoundError(
        f"No tokenizer for model architecture '{arch}' (vocab_size={vocab_size}).\n"
        f"Declare one in the model-params file, e.g. \"tokenizer\": \"tokenizer.json\" (a file in the model folder) or a Hugging Face repo id.\n"
        f"Execution stopped to prevent corrupted tokenization/generation with incompatible vocabulary encodings."
    )


def format_chat_prompt(messages: List[Dict[str, str]]) -> str:
    """Formats multi-turn chat messages into standard ChatML format (<|im_start|>, <|im_end|>)."""
    prompt = ""
    for m in messages:
        role = m.get("role", "user")
        content = m.get("content", "")
        prompt += f"<|im_start|>{role}\n{content}<|im_end|>\n"
    prompt += "<|im_start|>assistant\n"
    return prompt


def text_to_token_ids(text: str, tokenizer: Any = None) -> torch.Tensor:
    """Encodes text into a 2D token tensor (with batch dimension 1)."""
    if tokenizer is None:
        tokenizer = get_tokenizer("gpt2")
    if hasattr(tokenizer, "encode"):
        encoded = tokenizer.encode(text)
    else:
        encoded = [int(tok) for tok in text.split()]
    return torch.tensor(encoded).unsqueeze(0)


def token_ids_to_text(token_ids: torch.Tensor, tokenizer: Any = None) -> str:
    """Decodes a token tensor back into a string."""
    if tokenizer is None:
        tokenizer = get_tokenizer("gpt2")
    if hasattr(tokenizer, "decode"):
        return tokenizer.decode(token_ids)
    flat = token_ids.squeeze(0).tolist() if isinstance(token_ids, torch.Tensor) else token_ids
    return " ".join(str(t) for t in flat)


def _sample_next_token(
    logits: torch.Tensor,
    temperature: float = 0.0,
    top_k: Optional[int] = None,
    top_p: Optional[float] = None,
    min_p: Optional[float] = None,
    adaptive_temp: bool = False,
    temp_min: float = 0.15,
    temp_max: float = 0.85,
    repetition_penalty: float = 1.0,
    seen_tokens: Optional[torch.Tensor] = None,
    exempt_tokens: Optional[torch.Tensor] = None,
) -> torch.Tensor:
    """
    Samples the next token from model logits with repetition penalty, entropy-adaptive temperature,
    top-k filtering, top-p nucleus filtering, min-p dynamic tail cutoff, and numerically stable sampling.
    Special tokens (e.g. <|...|>) in exempt_tokens are strictly excluded from repetition penalty.
    """
    logits_step = logits[:, -1] if logits.ndim == 3 else logits
    if hasattr(torch, "float8_e4m3fn") and logits_step.dtype in (torch.float8_e4m3fn, getattr(torch, "float8_e5m2", None)):
        logits_step = logits_step.to(torch.float32)

    if seen_tokens is not None and seen_tokens.numel() > 0 and repetition_penalty != 1.0 and repetition_penalty > 0:
        if seen_tokens.ndim == 1:
            seen_tokens = seen_tokens.unsqueeze(0)
        seen_device = seen_tokens.to(logits_step.device)
        unique_seen = torch.unique(seen_device)
        if exempt_tokens is not None and exempt_tokens.numel() > 0:
            exempt_device = exempt_tokens.to(logits_step.device)
            unique_seen = unique_seen[~torch.isin(unique_seen, exempt_device)]
        if unique_seen.numel() > 0:
            unique_seen = unique_seen.unsqueeze(0)
            score = torch.gather(logits_step, 1, unique_seen)
            score = torch.where(score < 0, score * repetition_penalty, score / repetition_penalty)
            logits_step = logits_step.scatter(1, unique_seen, score)

    if temperature <= 0.0 and not adaptive_temp:
        return torch.argmax(logits_step, dim=-1, keepdim=True)

    logits_step = logits_step.to(torch.float32)

    if adaptive_temp:
        base_probs = torch.softmax(logits_step, dim=-1)
        h = -torch.sum(base_probs * torch.log(base_probs + 1e-12), dim=-1, keepdim=True)
        # Expected natural entropy range for ~50k vocab: ~0.5 (confident/factual) to ~4.0 (open-ended/creative)
        h_ratio = torch.clamp((h - 0.5) / 3.5, 0.0, 1.0)
        eff_temp = temp_min + h_ratio * (temp_max - temp_min)
        logits_step = logits_step / torch.clamp(eff_temp, min=1e-6)
    else:
        logits_step = logits_step / max(temperature, 1e-6)

    if top_k is not None and top_k > 0:
        top_logits, _ = torch.topk(logits_step, min(top_k, logits_step.shape[-1]), dim=-1)
        min_val = top_logits[:, -1, None]
        logits_step = torch.where(
            logits_step < min_val,
            torch.tensor(float("-inf"), device=logits_step.device, dtype=logits_step.dtype),
            logits_step
        )

    if top_p is not None and 0.0 < top_p < 1.0:
        sorted_logits, sorted_indices = torch.sort(logits_step, descending=True, dim=-1)
        cumulative_probs = torch.cumsum(torch.softmax(sorted_logits, dim=-1), dim=-1)
        sorted_indices_to_remove = cumulative_probs > top_p
        sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[..., :-1].clone()
        sorted_indices_to_remove[..., 0] = 0
        indices_to_remove = sorted_indices_to_remove.scatter(dim=-1, index=sorted_indices, src=sorted_indices_to_remove)
        logits_step = logits_step.masked_fill(indices_to_remove, float("-inf"))

    if min_p is not None and 0.0 < min_p < 1.0:
        step_probs = torch.softmax(logits_step, dim=-1)
        max_prob = step_probs.max(dim=-1, keepdim=True).values
        threshold = max_prob * min_p
        logits_step = logits_step.masked_fill(step_probs < threshold, float("-inf"))

    logits_step = logits_step - logits_step.max(dim=-1, keepdim=True).values
    probs = torch.softmax(logits_step, dim=-1)

    # Guard against zero or NaN probabilities
    prob_sum = probs.sum(dim=-1, keepdim=True)
    if torch.isnan(probs).any() or (prob_sum <= 0).any():
        return torch.argmax(logits_step, dim=-1, keepdim=True)

    probs = probs / prob_sum
    return torch.multinomial(probs, num_samples=1)


def generate_text(
    model: nn.Module,
    idx: torch.Tensor,
    max_new_tokens: int,
    context_size: int = None,
    use_cache: bool = True,
    use_cuda_graph: bool = False,
    temperature: float = 0.0,
    top_k: Optional[int] = None,
    top_p: Optional[float] = None,
    min_p: Optional[float] = None,
    adaptive_temp: bool = False,
    temp_min: float = 0.15,
    temp_max: float = 0.85,
    repetition_penalty: float = 1.0,
    eos_id: Any = None,
    stream_callback: Optional[Any] = None,
    stop_strings: Optional[List[str]] = None,
    tokenizer: Optional[Any] = None
) -> torch.Tensor:
    """
    High-performance text generation function supporting:
      1. Pre-allocated output token buffers (zero torch.cat reallocations)
      2. torch.inference_mode() execution
      3. Static pre-allocated KV caching with prefill & step decoding
      4. Masked CUDA Graph capture & replay on single GPU
      5. Pipeline-parallel multi-GPU model support
      6. Automatic fallback for models without KV cache
      7. Real-time token streaming callback
      8. Multi-token string stop sequence detection (e.g. ChatML and Phi tags)
    """
    model.eval()
    raw_model = model.raw_model if hasattr(model, "raw_model") else (model.module if hasattr(model, "module") else model)
    if hasattr(raw_model, "_orig_mod"):
        raw_model = raw_model._orig_mod

    ctx_len = context_size or (raw_model.pos_emb.num_embeddings if getattr(raw_model, "pos_emb", None) is not None else 1024)

    # Bound prompt within context window
    if idx.shape[1] >= ctx_len:
        idx = idx[:, -(ctx_len - 1):]

    batch_size, prompt_len = idx.shape
    max_new_tokens = max(1, min(max_new_tokens, ctx_len - prompt_len))
    total_len = prompt_len + max_new_tokens

    # Pre-allocate output token tensor once
    out_tokens = torch.empty(batch_size, total_len, dtype=torch.long, device=idx.device)
    out_tokens[:, :prompt_len] = idx

    eos_set = set()
    if eos_id is not None:
        if isinstance(eos_id, (int, float)):
            eos_set.add(int(eos_id))
        elif isinstance(eos_id, (list, tuple, set)):
            eos_set.update(int(x) for x in eos_id)

    if stop_strings and tokenizer and hasattr(tokenizer, "encode"):
        for s in stop_strings:
            try:
                s_toks = tokenizer.encode(s, allowed_special="all")
                if len(s_toks) == 1:
                    eos_set.add(s_toks[0])
            except Exception:
                pass

    # Collect all special tokens (<|...|>) to strictly exempt them from repetition penalties
    exempt_set = set(CUSTOM_SPECIAL_TOKENS.values())
    if eos_set:
        exempt_set.update(eos_set)
    if tokenizer is not None:
        if hasattr(tokenizer, "special_tokens") and isinstance(tokenizer.special_tokens, dict):
            exempt_set.update(tokenizer.special_tokens.values())
        if hasattr(tokenizer, "_special_tokens") and isinstance(tokenizer._special_tokens, dict):
            exempt_set.update(tokenizer._special_tokens.values())
        if hasattr(tokenizer, "all_special_ids") and isinstance(tokenizer.all_special_ids, (list, tuple, set)):
            exempt_set.update(tokenizer.all_special_ids)
        vocab = None
        if hasattr(tokenizer, "get_vocab") and callable(tokenizer.get_vocab):
            try:
                vocab = tokenizer.get_vocab()
            except Exception:
                pass
        elif hasattr(tokenizer, "base_tokenizer") and hasattr(tokenizer.base_tokenizer, "get_vocab") and callable(tokenizer.base_tokenizer.get_vocab):
            try:
                vocab = tokenizer.base_tokenizer.get_vocab()
            except Exception:
                pass
        if vocab and isinstance(vocab, dict):
            for tok_str, tok_id in vocab.items():
                if isinstance(tok_str, str) and tok_str.startswith("<|") and tok_str.endswith("|>"):
                    exempt_set.add(int(tok_id))
        if hasattr(tokenizer, "decode"):
            try:
                for tok_id in torch.unique(idx).tolist():
                    if tok_id not in exempt_set:
                        tok_str = tokenizer.decode([tok_id]).strip()
                        if tok_str.startswith("<|") and tok_str.endswith("|>"):
                            exempt_set.add(tok_id)
            except Exception:
                pass
    exempt_tokens_tensor = torch.tensor(sorted(exempt_set), device=idx.device, dtype=torch.long) if exempt_set else None

    def check_stop(cur_position: int) -> bool:
        if not stop_strings or tokenizer is None or not hasattr(tokenizer, "decode"):
            return False
        window_start = max(prompt_len, cur_position - 15)
        tail_ids = out_tokens[0, window_start:cur_position].tolist()
        try:
            tail_str = tokenizer.decode(tail_ids)
            for stop_str in stop_strings:
                if stop_str in tail_str:
                    return True
        except Exception:
            pass
        return False

    def is_eos(tok_tensor: torch.Tensor) -> bool:
        if not eos_set:
            return False
        if tok_tensor.numel() == 1:
            return tok_tensor.item() in eos_set
        return any(t.item() in eos_set for t in tok_tensor)

    with torch.inference_mode():
        if use_cache and hasattr(raw_model, "reset_kv_cache"):
            raw_model.reset_kv_cache()

            # Prefill phase
            input_tokens = out_tokens[:, :prompt_len]
            logits = model(input_tokens, use_cache=True)
            cur_pos = prompt_len

            # Check if CUDA Graph capture is eligible (single GPU, CUDA available, and static absolute pos_emb architecture)
            is_single_gpu = not hasattr(model, "devices") and next(model.parameters()).is_cuda
            is_static_gpt = hasattr(raw_model, "pos_emb") and getattr(raw_model, "pos_emb", None) is not None
            is_quantized = any("Linear4Bit" in type(m).__name__ or "LinearQuant" in type(m).__name__ for m in raw_model.modules())
            can_use_cuda_graph = use_cuda_graph and is_single_gpu and is_static_gpt and hasattr(raw_model, "trf_blocks") and not is_quantized

            graph_captured = False
            if can_use_cuda_graph:
                try:
                    dtype = next(model.parameters()).dtype
                    mask_len = raw_model.trf_blocks[0].att.max_seq_len if (
                        hasattr(raw_model.trf_blocks[0], "att") and hasattr(raw_model.trf_blocks[0].att, "max_seq_len")
                    ) else ctx_len

                    static_next_idx = torch.empty((1, 1), dtype=torch.long, device=idx.device)
                    static_pos_ids = torch.empty((1, 1), dtype=torch.long, device=idx.device)
                    mask_fill_val = -440.0 if (hasattr(torch, "float8_e4m3fn") and dtype == torch.float8_e4m3fn) else -10000.0
                    static_attn_mask = torch.full((1, 1, 1, mask_len), mask_fill_val, dtype=dtype, device=idx.device)

                    static_attn_mask[:, :, :, :prompt_len] = 0.0
                    static_pos_ids[0, 0] = prompt_len
                    static_next_idx.copy_(_sample_next_token(logits, temperature, top_k, top_p, min_p, adaptive_temp, temp_min, temp_max, repetition_penalty, out_tokens[:, :prompt_len], exempt_tokens=exempt_tokens_tensor))

                    # Warmup execution with static GPU memory buffers
                    s = torch.cuda.Stream()
                    s.wait_stream(torch.cuda.current_stream())
                    with torch.cuda.stream(s):
                        for _ in range(3):
                            static_logits = model(static_next_idx, use_cache=True, attn_mask=static_attn_mask, pos_ids=static_pos_ids)
                    torch.cuda.current_stream().wait_stream(s)

                    # Capture execution graph
                    g = torch.cuda.CUDAGraph()
                    with torch.cuda.graph(g):
                        static_logits = model(static_next_idx, use_cache=True, attn_mask=static_attn_mask, pos_ids=static_pos_ids)

                    graph_captured = True
                except Exception:
                    graph_captured = False
                    if torch.cuda.is_available():
                        torch.cuda.current_stream().synchronize()

            if graph_captured:
                for _ in range(max_new_tokens):
                    next_idx = _sample_next_token(logits, temperature, top_k, top_p, min_p, adaptive_temp, temp_min, temp_max, repetition_penalty, out_tokens[:, :cur_pos], exempt_tokens=exempt_tokens_tensor)
                    if is_eos(next_idx):
                        break
                    out_tokens[:, cur_pos:cur_pos+1] = next_idx
                    cur_pos += 1
                    if check_stop(cur_pos):
                        break
                    if stream_callback is not None:
                        stream_callback(next_idx.item())

                    static_next_idx.copy_(next_idx)
                    static_pos_ids[0, 0] = cur_pos
                    static_attn_mask[:, :, :, cur_pos] = 0.0

                    g.replay()
                    logits = static_logits
            else:
                # Standard static KV cache step decoding
                for _ in range(max_new_tokens):
                    next_idx = _sample_next_token(logits, temperature, top_k, top_p, min_p, adaptive_temp, temp_min, temp_max, repetition_penalty, out_tokens[:, :cur_pos], exempt_tokens=exempt_tokens_tensor)
                    if is_eos(next_idx):
                        break
                    out_tokens[:, cur_pos:cur_pos+1] = next_idx
                    cur_pos += 1
                    if check_stop(cur_pos):
                        break
                    if stream_callback is not None:
                        stream_callback(next_idx.item())
                    logits = model(next_idx, use_cache=True)
        else:
            # Full sequence forward pass (models without KV cache, e.g. gpt_original)
            cur_pos = prompt_len
            for _ in range(max_new_tokens):
                input_chunk = out_tokens[:, max(0, cur_pos - ctx_len):cur_pos]
                if hasattr(raw_model, "reset_kv_cache"):
                    logits = model(input_chunk, use_cache=False)
                else:
                    logits = model(input_chunk)
                next_idx = _sample_next_token(logits, temperature, top_k, top_p, min_p, adaptive_temp, temp_min, temp_max, repetition_penalty, out_tokens[:, :cur_pos], exempt_tokens=exempt_tokens_tensor)
                if is_eos(next_idx):
                    break
                out_tokens[:, cur_pos:cur_pos+1] = next_idx
                cur_pos += 1
                if check_stop(cur_pos):
                    break
                if stream_callback is not None:
                    stream_callback(next_idx.item())

        if use_cache and hasattr(raw_model, "reset_kv_cache"):
            raw_model.reset_kv_cache()

    return out_tokens[:, :cur_pos]

