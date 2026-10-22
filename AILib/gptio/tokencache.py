# Token cache for pretraining text files: every <file>.txt is tokenized once into a memory-mapped <file>.tokens.npy sidecar, so an
# epoch can draw its context windows from all files at random (gptmodel.Dataset.StreamingTextDataset) instead of streaming one file
# at a time, and every step count is exact from the start.

import json
import os
import time
from pathlib import Path
from typing import Any, List, Tuple, Union

import numpy as np

from gptio.fileutil import read_text_file
from gptutils.consoleutils import print

TOKEN_CACHE_SUFFIX: str = ".tokens.npy"
TOKEN_META_SUFFIX: str = ".tokens.json"
EOS_TOKEN: str = "<|endoftext|>"  # the document separator of every pretraining file (see gptinfer.inference.EOS_TOKEN)
ENCODE_BATCH_DOCS: int = 4096  # documents per encode_batch call: bounds the transient Python int lists to a few hundred MB


def token_cache_paths(text_file: Union[str, Path]) -> Tuple[Path, Path]:
    """(token array, manifest) sidecar paths of a text file."""
    p = Path(text_file)
    return p.with_name(p.name + TOKEN_CACHE_SUFFIX), p.with_name(p.name + TOKEN_META_SUFFIX)


def token_dtype(tokenizer: Any) -> Any:
    """Smallest unsigned integer type that holds every token id of the tokenizer."""
    return np.uint16 if int(getattr(tokenizer, "n_vocab", 1 << 20)) <= np.iinfo(np.uint16).max else np.uint32


def tokenize_text_file(text_file: Path, tokenizer: Any) -> np.ndarray:
    """
    Token ids of a text file plus the trailing " <|endoftext|> " the streaming loader used to append. The text is split at the
    document separator and encoded per batch of documents (parallel threads inside the tokenizer): the tokenizer itself splits at
    special tokens before running BPE, so the result is identical to encoding the whole file in one call.
    """
    docs = (read_text_file(text_file) + f" {EOS_TOKEN} ").split(EOS_TOKEN)
    dtype, eos_id = token_dtype(tokenizer), int(tokenizer.eos_id)
    chunks: List[np.ndarray] = []
    for start in range(0, len(docs), ENCODE_BATCH_DOCS):
        for i, ids in enumerate(tokenizer.encode_batch(docs[start:start + ENCODE_BATCH_DOCS], allowed_special="all"), start):
            if i < len(docs) - 1:  # every document but the last is followed by the separator it was split on
                ids = ids + [eos_id]
            if ids:
                chunks.append(np.fromiter(ids, dtype=dtype, count=len(ids)))
    return np.concatenate(chunks) if chunks else np.empty(0, dtype=dtype)


def load_token_cache(text_file: Union[str, Path], tokenizer: Any, label: str = "") -> np.ndarray:
    """
    Memory-mapped token ids of a text file. Built on first use (and rebuilt when the text file or the tokenizer changed: the manifest
    records the source size/mtime and the tokenizer's vocabulary); later runs and the other stages just map the sidecar.
    """
    text_file = Path(text_file)
    npy_path, meta_path = token_cache_paths(text_file)
    st = text_file.stat()
    expected = {"source_bytes": st.st_size, "source_mtime_ns": st.st_mtime_ns, "n_vocab": int(getattr(tokenizer, "n_vocab", 0)), "eos_id": int(tokenizer.eos_id)}
    if npy_path.exists() and meta_path.exists():
        try:
            if all(json.loads(meta_path.read_text(encoding="utf-8")).get(k) == v for k, v in expected.items()):
                return np.load(npy_path, mmap_mode="r")
        except Exception:
            pass
    t0 = time.time()
    tokens = tokenize_text_file(text_file, tokenizer)
    tmp_path = npy_path.with_name(npy_path.name + ".tmp.npy")
    np.save(tmp_path, tokens)
    os.replace(tmp_path, npy_path)
    meta_path.write_text(json.dumps({**expected, "n_tokens": int(tokens.size)}), encoding="utf-8")
    print(f"[Token Cache] Tokenized {label or text_file.name}: {tokens.size:,} tokens in {time.time() - t0:.1f}s -> {npy_path.name}")
    del tokens
    return np.load(npy_path, mmap_mode="r")
