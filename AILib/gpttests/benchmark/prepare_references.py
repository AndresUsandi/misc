# Copyright (c) Sebastian Raschka under Apache License 2.0 (see LICENSE.txt).
# Builds and measures the reference models of references.json with the benchmark harness, so that every number in the benchmark table's
# reference columns comes from this very harness: each model is downloaded into gpttests/benchmark/cache/ref/<name>/ (git-ignored; a rasbt
# .pth or a HuggingFace safetensors file translated to this project's weight names), benchmarked with benchcore.evaluate (every set but the
# chat-only GSM8K, full sets, bf16, 5-shot TriviaQA since they are base models) and its values, exact parameter count and measurement date
# written back into references.json.
#
#   python gpttests/benchmark/prepare_references.py                      # every reference not measured yet (~2-3 h on one GPU, ~17 GB download)
#   python gpttests/benchmark/prepare_references.py --only smollm2-360M  # one model
#   python gpttests/benchmark/prepare_references.py --force              # re-measure the ones already measured too
#   python gpttests/benchmark/prepare_references.py --quick              # smoke test: subsampled sets, nothing written

import argparse
import datetime
import json
import re
import shutil
import sys
from pathlib import Path
from typing import Any, Dict

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from gpttests.benchmark.benchcore import ALL_SETS, CACHE_DIR, REFERENCES_FILE, evaluate, load_references  # noqa: E402  (sets HF_HOME before the HF imports)

import torch  # noqa: E402

from gptio.modelio import _clean_state_dict_keys  # noqa: E402
from gptmodel.GptModel import GptModel  # noqa: E402
from repos.modelrepo import download_file  # noqa: E402

REF_DIR = CACHE_DIR / "ref"
HEADLINE = (("hellaswag", "hellaswag_norm"), ("arc_easy", "arc_easy"), ("arc_challenge", "arc_challenge"), ("sciq", "sciq"), ("winogrande", "winogrande"), ("lambada", "lambada"),
            ("lambada_ppl", "lambada_ppl"), ("triviaqa", "triviaqa"), ("wikitext", "wikitext_ppl"), ("fineweb_edu", "fineweb_edu_ppl"), ("pg19", "pg19_ppl"), ("c4", "c4_ppl"))  # references.json key -> evaluate() metric
HF_KEYS = {  # HuggingFace Llama / Qwen weight names -> this project's (layer keys are matched after "model.layers.<N>.")
    "model.embed_tokens.weight": "tok_emb.weight", "model.norm.weight": "final_norm.scale", "lm_head.weight": "out_head.weight",
    "input_layernorm.weight": "norm1.scale", "post_attention_layernorm.weight": "norm2.scale",
    "self_attn.q_proj": "att.W_query", "self_attn.k_proj": "att.W_key", "self_attn.v_proj": "att.W_value", "self_attn.o_proj": "att.out_proj",
    "self_attn.q_norm.weight": "att.q_norm.scale", "self_attn.k_norm.weight": "att.k_norm.scale",
    "mlp.gate_proj": "ff.fc1", "mlp.up_proj": "ff.fc2", "mlp.down_proj": "ff.fc3",
}


def translate_hf_key(key: str) -> str:
    m = re.match(r"^model\.layers\.(\d+)\.(.*)$", key)
    if not m:
        return HF_KEYS.get(key, key)
    rest = m.group(2)
    for hf, ours in HF_KEYS.items():
        if rest == hf or rest.startswith(hf + "."):
            return f"trf_blocks.{m.group(1)}.{ours}{rest[len(hf):]}"
    return key


def target_model(params: Dict[str, Any]) -> GptModel:
    """The project's model for a model-params dict, on the meta device when possible (names and shapes only, no memory)."""
    cfg = dict(params)
    cfg.setdefault("n_kv_groups", cfg["n_heads"])
    cfg.setdefault("n_kv_producing_layers", cfg["n_layers"])
    try:
        with torch.device("meta"):
            return GptModel(cfg)
    except Exception:
        return GptModel(cfg)


def check_keys(sd: Dict[str, torch.Tensor], params: Dict[str, Any], name: str) -> None:
    """Raises when the weights would not load strictly into the project's model (checked at the file's own vocab size: GPT-2's 50,257 rows are padded to 50,304 by the loader)."""
    model = target_model({**params, "vocab_size": sd["tok_emb.weight"].shape[0]})
    tgt = model.state_dict()
    got = _clean_state_dict_keys(sd, model) if set(sd) != set(tgt) else sd
    missing, extra = set(tgt) - set(got), set(got) - set(tgt)
    bad = [k for k in set(tgt) & set(got) if tuple(got[k].shape) != tuple(tgt[k].shape)]
    if missing or extra or bad:
        raise ValueError(f"{name}: weights do not match the model-params. Missing {sorted(missing)[:8]}, unexpected {sorted(extra)[:8]}, shape mismatch {bad[:8]}")


def prepare(name: str, spec: Dict[str, Any]) -> Path:
    """Downloads (and for HuggingFace safetensors, translates) one reference into REF_DIR/<name>/ with its model-params; returns the folder."""
    folder = REF_DIR / name
    folder.mkdir(parents=True, exist_ok=True)
    params = dict(spec["model_params"])
    pth = folder / f"{name}.pth"
    if spec["kind"] == "pth":
        download_file(spec["url"], pth)
        payload = torch.load(pth, map_location="cpu", weights_only=True)
        sd = payload.get("model_state_dict", payload.get("state_dict", payload)) if isinstance(payload, dict) else payload
    else:  # HuggingFace safetensors, translated once to this project's weight names; the tokenizer.json comes from the same repo
        from huggingface_hub import hf_hub_download
        from safetensors.torch import load_file
        if not pth.exists():
            sd = {translate_hf_key(k): v for k, v in load_file(hf_hub_download(spec["repo"], "model.safetensors")).items()}
            if "out_head.weight" not in sd and params.get("tie_embeddings"):
                sd["out_head.weight"] = sd["tok_emb.weight"]
            check_keys(sd, params, name)
            torch.save({"model_state_dict": sd, "config": params}, pth)
            print(f"[References] {name}: translated {spec['repo']} safetensors to {pth.name} ({len(sd)} tensors).")
        else:
            sd = torch.load(pth, map_location="cpu", weights_only=True)["model_state_dict"]
        if not (folder / "tokenizer.json").exists():
            shutil.copyfile(hf_hub_download(spec["repo"], "tokenizer.json"), folder / "tokenizer.json")
    check_keys(sd, params, name)  # the "tokenizer" repo id in model-params resolves to <folder>/tokenizer.json, downloaded by get_tokenizer when absent
    (folder / f"{name}.model-params.json").write_text(json.dumps(params, indent=2), encoding="utf-8")
    return folder


def main() -> int:
    p = argparse.ArgumentParser(description="Download, convert and benchmark the reference models of references.json.")
    p.add_argument("--only", nargs="*", default=None, help="Reference names to process (default: every reference with a set not measured yet).")
    p.add_argument("--force", action="store_true", help="Also re-measure references that already have every value.")
    p.add_argument("--quick", action="store_true", help="Subsampled sets for a smoke test; results are printed, not written.")
    p.add_argument("--device", default=None, help="cuda, cuda:N or cpu (default: cuda:0 when available).")
    a = p.parse_args()
    device = torch.device(a.device if a.device else ("cuda:0" if torch.cuda.is_available() else "cpu"))
    refs = load_references()
    names = a.only or [n for n, r in refs["models"].items() if a.force or any(r.get(k) is None for k, _ in HEADLINE)]
    failed = []
    for name in names:
        r = refs["models"][name]
        try:
            prepare(name, r["prepare"])
            E = evaluate(name, str(REF_DIR), "pth", device, ALL_SETS, a.quick, 200 if a.quick else 1000, "fewshot")
            M = E["metrics"]
            values = {k: round(M[m], 1) for k, m in HEADLINE if m in M}
            print(f"[References] {name} ({E['n_params'] / 1e6:.1f}M params, {E['elapsed']:.0f}s): " + ", ".join(f"{k} {v}" for k, v in values.items()), flush=True)
            if not a.quick:
                r.update(values)
                r["params_M"] = round(E["n_params"] / 1e6, 1)
                r["measured"] = datetime.date.today().isoformat()
                r.pop("published", None)
                r.pop("published_source", None)
                REFERENCES_FILE.write_text(json.dumps(refs, indent=2), encoding="utf-8")
        except Exception as e:
            failed.append(name)
            print(f"[References] {name} FAILED: {type(e).__name__}: {e}", flush=True)
    print(f"[References] done: {len(names) - len(failed)} measured, {len(failed)} failed{' (' + ', '.join(failed) + ')' if failed else ''}; values in {REFERENCES_FILE}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
