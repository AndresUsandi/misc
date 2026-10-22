# Copyright (c) Sebastian Raschka under Apache License 2.0 (see LICENSE.txt).
# GGUF export: writes a final model file (.pth) as a GGUF file that llama.cpp and Ollama can load.
# Only the GPT-2 family is exported (learned absolute positions, LayerNorm, GELU, multi-head attention): that is llama.cpp's "gpt2" architecture.

import re
import sys
from pathlib import Path
from typing import List, Tuple

import gguf
import numpy as np
import torch

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from gptinfer.inference import CUSTOM_SPECIAL_TOKENS, EOS_TOKEN, get_custom_tiktoken_encoding
from gptio.modelio import _clean_state_dict_keys
from gptmodel.GptModel import GptModel
from gptmodel.Modules import LayerNorm

_T = gguf.MODEL_TENSOR
GGUF_MODULES = {  # module of GptModel -> GGUF tensor (the GGUF name is that tensor's name plus ".weight" / ".bias")
    "tok_emb": _T.TOKEN_EMBD, "pos_emb": _T.POS_EMBD, "final_norm": _T.OUTPUT_NORM, "out_head": _T.OUTPUT,
    "att.W_qkv": _T.ATTN_QKV, "att.out_proj": _T.ATTN_OUT, "ff.fc1": _T.FFN_UP, "ff.fc2": _T.FFN_DOWN, "norm1": _T.ATTN_NORM, "norm2": _T.FFN_NORM,
}
GGUF_PARAMS = {"weight": "weight", "scale": "weight", "bias": "bias", "shift": "bias"}  # this project's LayerNorm calls its weight "scale" and its bias "shift"
CHATML_TEMPLATE = (  # the format gptinfer.inference.format_chat_prompt builds
    "{% for message in messages %}{{ '<|im_start|>' + message['role'] + '\\n' + message['content'] + '<|im_end|>' + '\\n' }}{% endfor %}"
    "{% if add_generation_prompt %}{{ '<|im_start|>assistant\\n' }}{% endif %}"
)


def gpt2_vocab(vocab_size: int) -> Tuple[List[str], List[int], List[str]]:
    """Tokens (in GPT-2's byte-level spelling), token types and merge rules of the built-in tokenizer: one token per embedding row; ids with no token become unused placeholders."""
    if vocab_size < 50257:
        raise ValueError(f"vocab_size {vocab_size} is smaller than the GPT-2 vocabulary (50257 tokens).")
    enc = get_custom_tiktoken_encoding()
    ranks = enc._mergeable_ranks
    spell = gguf.vocab.bytes_to_unicode()
    text = lambda b: "".join(spell[x] for x in b)
    token_of = {rank: tok for tok, rank in ranks.items()}
    special_of = {rank: tok for tok, rank in enc._special_tokens.items()}
    tokens, types = [], []
    for i in range(vocab_size):
        if i in token_of:
            tokens.append(text(token_of[i])); types.append(gguf.TokenType.NORMAL)
        elif i in special_of:
            tokens.append(special_of[i]); types.append(gguf.TokenType.CONTROL)
        else:
            tokens.append(f"[PAD{i}]"); types.append(gguf.TokenType.UNUSED)
    merges = []
    for tok, rank in sorted(ranks.items(), key=lambda kv: kv[1]):
        if len(tok) > 1 and rank < vocab_size:
            # the merge that created this token: run BPE on its bytes using only the merges that rank before it; the two parts left are the pair
            parts = [bytes([b]) for b in tok]
            while True:
                best, i = min((ranks.get(a + b, rank), i) for i, (a, b) in enumerate(zip(parts, parts[1:])))
                if best >= rank:
                    break
                parts[i:i + 2] = [parts[i] + parts[i + 1]]
            merges.append(f"{text(parts[0])} {text(parts[1])}")
    return tokens, types, merges


def write_gguf(model_file: Path, gguf_file: Path) -> None:
    """Writes the model file (.pth) as an F16 GGUF file (norms, biases and the position table stay F32), tokenizer and ChatML chat template included."""
    try:
        payload = torch.load(model_file, map_location="cpu", weights_only=True)
    except Exception:
        payload = torch.load(model_file, map_location="cpu", weights_only=False)
    if not isinstance(payload, dict) or "model_state_dict" not in payload or "config" not in payload:
        raise ValueError(f"'{model_file}' has no 'model_state_dict' and 'config' entries; it is not a model file saved by this project.")
    sd, cfg = payload["model_state_dict"], dict(payload["config"])
    cfg["vocab_size"] = sd["tok_emb.weight"].shape[0]
    with torch.device("meta"):  # the architecture without its weights: the model class itself says what the config builds
        model = GptModel(cfg)
    blk, vocab_size, n_layers = model.trf_blocks[0], cfg["vocab_size"], len(model.trf_blocks)

    unsupported = {
        "RoPE positions": model.pos_emb is None, "a norm other than LayerNorm": not isinstance(blk.norm1, LayerNorm), "a SwiGLU feed-forward": blk.ff.ffn_type == "swiglu",
        "qk_norm": blk.att.qk_norm, "grouped-query attention": blk.att.num_kv_groups != blk.att.num_heads, "a sliding attention window": blk.att.window_size is not None,
        "shared key/value layers": model.n_kv_producing_layers != n_layers, "a head_dim that is not emb_dim / n_heads": blk.att.d_out != cfg["emb_dim"],
        "a custom tokenizer": str(cfg.get("tokenizer") or "gpt2").lower() != "gpt2",
    }
    if any(unsupported.values()):
        raise ValueError(f"'{model_file}' cannot be exported to GGUF: it uses {', '.join(k for k, v in unsupported.items() if v)}, which llama.cpp's gpt2 architecture does not have.")

    sd = _clean_state_dict_keys(sd, model)
    tied = model.out_head.weight is model.tok_emb.weight
    tokens, types, merges = gpt2_vocab(vocab_size)
    eos = get_custom_tiktoken_encoding().encode_single_token(EOS_TOKEN)

    w = gguf.GGUFWriter(str(gguf_file), "gpt2")
    w.add_name(model_file.stem)
    w.add_context_length(cfg["context_length"])
    w.add_embedding_length(cfg["emb_dim"])
    w.add_block_count(n_layers)
    w.add_feed_forward_length(blk.ff.fc1.out_features)
    w.add_head_count(blk.att.num_heads)
    w.add_layer_norm_eps(blk.norm1.eps)
    w.add_file_type(gguf.LlamaFileType.MOSTLY_F16)
    w.add_tokenizer_model("gpt2")
    w.add_tokenizer_pre("gpt-2")
    w.add_token_list(tokens)
    w.add_token_types(types)
    w.add_token_merges(merges)
    w.add_bos_token_id(eos)
    w.add_eos_token_id(eos)
    w.add_add_bos_token(False)
    w.add_add_eos_token(False)
    im_end = CUSTOM_SPECIAL_TOKENS["<|im_end|>"]
    if im_end < vocab_size:  # the ChatML tokens exist (the original GPT-2 vocabulary has none)
        w.add_eot_token_id(im_end)
        w.add_chat_template(CHATML_TEMPLATE)

    written = set()
    for key, tensor in sd.items():
        m = re.fullmatch(r"(?:trf_blocks\.(\d+)\.)?(.+)\.(weight|bias|scale|shift)", key)
        if m is None or m.group(2) not in GGUF_MODULES:
            raise ValueError(f"'{model_file}': parameter '{key}' has no GGUF counterpart.")
        kind = GGUF_MODULES[m.group(2)]
        if kind == _T.OUTPUT and tied:
            continue  # llama.cpp reuses the token embedding as the output head when the file has no output tensor
        name = f"{gguf.TENSOR_NAMES[kind].format(bid=int(m.group(1) or 0))}.{GGUF_PARAMS[m.group(3)]}"
        data = tensor.detach().float().numpy()
        w.add_tensor(name, data.astype(np.float16) if data.ndim > 1 and kind != _T.POS_EMBD else data)
        written.add(name)
    for bid in range(n_layers):  # llama.cpp's gpt2 always has these biases; a model trained without them gets zeros, which changes nothing
        for kind, size in ((_T.ATTN_QKV, 3 * cfg["emb_dim"]), (_T.ATTN_OUT, cfg["emb_dim"])):
            name = f"{gguf.TENSOR_NAMES[kind].format(bid=bid)}.bias"
            if name not in written:
                w.add_tensor(name, np.zeros(size, dtype=np.float32))

    w.write_header_to_file()
    w.write_kv_data_to_file()
    w.write_tensors_to_file()
    w.close()
