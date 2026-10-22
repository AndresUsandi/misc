# Copyright (c) Sebastian Raschka under Apache License 2.0 (see LICENSE.txt).
# Shared benchmark core for the model benchmark tests: five standard benchmarks scored the way lm-evaluation-harness scores them,
# so the numbers are comparable with published small-model results, printed to the console.
#
#   hellaswag  commonsense sentence completion, 4-way multiple choice (validation split). acc_norm: per-character normalized log-likelihood.
#   arc_easy   grade-school science questions, multiple choice (test split). acc: summed log-likelihood of each option.
#   lambada    predict the last word of a passage from its long context (OpenAI test set): accuracy of the greedy word, and its perplexity.
#   triviaqa   closed-book trivia (rc.nocontext validation, fixed seeded sample): the answer (any alias) appears in the reply. Fine-tuned
#              weights are asked in chat format and decoded greedily; pretrained weights get a 5-shot "Q:/A:" prompt.
#   wikitext   perplexity of the WikiText-103 test split over non-overlapping 1,024-token windows (all andres models train on Wikipedia,
#              so this measures how well the pretraining text itself was learned; compare it only between models of the same data recipe).
# Added 2026-10-16 (the sets the dataset-recipe comparisons used):
#   arc_challenge, sciq   multiple choice like arc_easy (ARC-Challenge test, SciQ test).
#   winogrande  pronoun resolution (XL validation): the option whose continuation is likelier, lm-eval "partial evaluation".
#   gsm8k       grade-school math word problems (test split), zero-shot chat prompt, greedy, the last number of the reply is the answer.
#   fineweb_edu, pg19, c4   perplexity on text outside WikiText: FineWeb-Edu (in the andres-350M-2 pretraining recipe), PG-19 books and C4 web
#               text (in neither recipe), ~300-400 windows each.
# --output_to_file writes every score plus the per-item correctness strings to a JSON that gpttests/compare_models.py turns into a comparison
# with paired significance tests.
#
# Weights are evaluated in bf16 with plain Linear layers, exactly as infer.py runs them. The datasets are downloaded from the Hugging Face
# Hub once: the raw files land in gpttests/benchmark/cache/hf and the prepared evaluation sets in cache/bench_data.json (git-ignored);
# every later run reads the JSON and needs no network. Delete the cache folder to re-download.

import argparse
import json
import math
import os
import random
import re
import string
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

CACHE_DIR = Path(__file__).resolve().parent / "cache"  # downloaded once, kept (git-ignored)
DATA_CACHE = CACHE_DIR / "bench_data.json"
os.environ.setdefault("HF_HOME", str(CACHE_DIR / "hf"))  # must be set before anything imports huggingface_hub / datasets
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")

import torch

from argsutil import ModelArgs
from gptinfer.inference import format_chat_prompt, get_tokenizer
from gptio.modelio import _clean_state_dict_keys, load_model_config
from gptio.pathutil import STAGE_OPTIMIZE, STAGE_TRAIN, STAGE_TUNE, TARGET_CHECKPOINT, TARGET_MODEL, resolve_path
from gptmodel.GptModel import GptModel
from gpttests.testutil import run_test
from gptutils.consoleutils import str_to_bool

WEIGHT_STAGES = {"trn": STAGE_TRAIN, "sft": STAGE_TUNE, "dpo": STAGE_OPTIMIZE}  # "pth" = the final exported weights
CONTEXT = 1024
TRIVIA_SHOTS = ("Q: What is the capital of Australia?\nA: Canberra\nQ: Who painted the ceiling of the Sistine Chapel?\nA: Michelangelo\n"
                "Q: In which year did World War II end?\nA: 1945\nQ: What is the chemical symbol for gold?\nA: Au\nQ: Which planet is known as the Red Planet?\nA: Mars\n")
# Context for reading a result: random-guess level, and two reference models of the size class closest to the benchmarked model's parameter
# count (references.json: 150M / 350M / 750M / 1B / 1.5B, each an older baseline such as GPT-2 Medium and a strong modern model such as SmolLM2-360M),
# measured with this very harness by prepare_references.py (full sets, bf16; they are base models, so their TriviaQA figure is the 5-shot one).
# A value the JSON lists under "published" was taken from the model card instead and is printed with a *. WikiText perplexity is per token
# of the model's own tokenizer, so a reference with another tokenizer shows n/a there. LAMBADA passages come from BookCorpus novels and
# WikiText from Wikipedia, both part of the andres pretraining recipes, so on those two the andres models have seen related text.
CHANCE = {"hellaswag": 25.0, "arc_easy": 25.0, "lambada": 0.0, "triviaqa": 0.0}
REFERENCES_FILE = Path(__file__).resolve().parent / "references.json"


def load_references() -> Dict[str, Any]:
    return json.loads(REFERENCES_FILE.read_text(encoding="utf-8"))


def size_class(n_params: int, refs: Dict[str, Any]) -> str:
    """The reference size class (150M, 350M, 750M, 1B, 1.5B) whose parameter count is closest to n_params."""
    return min(refs["classes"], key=lambda c: abs(refs["classes"][c]["params"] - n_params))


def tokenizer_family(spec: Any) -> str:
    """gpt2 / smollm / qwen / <spec>: references share WikiText perplexity only with models of the same tokenizer."""
    s = str(spec or "gpt2").lower()
    return next((f for f in ("gpt2", "smollm", "qwen") if f in s), s)


def load_model(model_name: str, models_dir: str, weights: str, device: torch.device) -> Tuple[GptModel, Path]:
    """The model with the requested weights ("pth", or the "trn" / "sft" / "dpo" stage checkpoint) in bf16 on device, eval mode."""
    cfg = dict(load_model_config(ModelArgs(model_name=model_name, models_base_dir=models_dir)) or {})
    if cfg.get("vocab_size") == 50257:
        cfg["vocab_size"] = 50304
    cfg.setdefault("n_kv_groups", cfg["n_heads"])
    cfg.setdefault("n_kv_producing_layers", cfg["n_layers"])
    path = (resolve_path(model_name, target=TARGET_MODEL, models_dir=models_dir) if weights == "pth"
            else resolve_path(model_name, target=TARGET_CHECKPOINT, stage=WEIGHT_STAGES[weights], models_dir=models_dir))
    if not path.exists():
        raise FileNotFoundError(f"No '{weights}' weights for {model_name}: {path}")
    try:
        payload = torch.load(path, map_location="cpu", weights_only=True)
    except Exception:
        payload = torch.load(path, map_location="cpu", weights_only=False)
    sd = payload.get("model_state_dict", payload.get("state_dict", payload)) if isinstance(payload, dict) else payload
    model = GptModel(cfg)
    model.load_state_dict(_clean_state_dict_keys(sd, model), strict=True)
    dtype = torch.bfloat16 if device.type == "cuda" else torch.float32
    return model.to(device, dtype=dtype).eval(), path


ALL_SETS = ("hellaswag", "arc_easy", "arc_challenge", "sciq", "winogrande", "lambada", "triviaqa", "gsm8k", "wikitext", "fineweb_edu", "pg19", "c4")


def prepare_data(seed: int = 1234, keys: Optional[List[str]] = None) -> Dict[str, Any]:
    """Reads the evaluation sets (all, or just keys) from the Hugging Face Hub and returns them as plain lists / strings (full sets; TriviaQA
    is a fixed seeded 3,000-question sample of the validation split). Everything is streamed, so only the split that is used is fetched and
    nothing but the resulting JSON is stored (a plain load_dataset(split="test") would also download and convert the training splits)."""
    from datasets import load_dataset

    def pre(t: str) -> str:  # lm-eval-harness HellaSwag text cleanup
        t = t.strip().replace(" [title]", ". ")
        return re.sub(r"\[.*?\]", "", t).replace("  ", " ")

    def docs(name: str, config: Optional[str], split: str, field: str, chars: int) -> List[str]:
        out, total = [], 0
        for r in load_dataset(name, config, split=split, streaming=True) if config else load_dataset(name, split=split, streaming=True):
            out.append(r[field]); total += len(r[field])
            if total >= chars:
                break
        return out

    want = set(keys or ALL_SETS)
    data: Dict[str, Any] = {}
    if "hellaswag" in want:
        hs = load_dataset("Rowan/hellaswag", split="validation", streaming=True)
        data["hellaswag"] = [{"ctx": pre(r["activity_label"] + ": " + r["ctx_a"] + " " + r["ctx_b"].capitalize()), "choices": [" " + pre(e) for e in r["endings"]], "gold": int(r["label"])} for r in hs]
    for key, config in (("arc_easy", "ARC-Easy"), ("arc_challenge", "ARC-Challenge")):
        if key in want:
            arc = load_dataset("allenai/ai2_arc", config, split="test", streaming=True)
            data[key] = [{"ctx": "Question: " + r["question"] + "\nAnswer:", "choices": [" " + c for c in r["choices"]["text"]], "gold": r["choices"]["label"].index(r["answerKey"])} for r in arc]
    if "sciq" in want:  # lm-eval-harness form: the supporting passage precedes the question, correct answer last
        data["sciq"] = [{"ctx": r["support"].lstrip() + "\nQuestion: " + r["question"] + "\nAnswer:", "choices": [" " + c for c in (r["distractor1"], r["distractor2"], r["distractor3"], r["correct_answer"])], "gold": 3}
                        for r in load_dataset("allenai/sciq", split="test", streaming=True)]
    if "winogrande" in want:
        items = []
        for r in load_dataset("allenai/winogrande", "winogrande_xl", split="validation", streaming=True):
            i = r["sentence"].index("_")
            items.append({"prefixes": [r["sentence"][:i] + r["option1"], r["sentence"][:i] + r["option2"]], "cont": r["sentence"][i + 1:], "gold": int(r["answer"]) - 1})
        data["winogrande"] = items
    if "lambada" in want:
        lb = load_dataset("EleutherAI/lambada_openai", "default", split="test", streaming=True)
        data["lambada"] = [{"ctx": " ".join(r["text"].split(" ")[:-1]), "target": " " + r["text"].split(" ")[-1]} for r in lb]
    if "wikitext" in want:
        wt = load_dataset("Salesforce/wikitext", "wikitext-103-raw-v1", split="test", streaming=True)
        data["wikitext"] = "".join(r["text"] for r in wt)
    if "triviaqa" in want:
        rows = []
        for r in load_dataset("mandarjoshi/trivia_qa", "rc.nocontext", split="validation", streaming=True):
            rows.append({"q": r["question"], "aliases": [a for a in r["answer"]["normalized_aliases"] if a]})
            if len(rows) >= 3000:
                break
        random.Random(seed).shuffle(rows)
        data["triviaqa"] = rows
    if "gsm8k" in want:
        data["gsm8k"] = [{"q": r["question"], "a": r["answer"].split("####")[-1].strip().replace(",", "")} for r in load_dataset("openai/gsm8k", "main", split="test", streaming=True)]
    if "fineweb_edu" in want:
        data["fineweb_edu"] = docs("HuggingFaceFW/fineweb-edu", "sample-10BT", "train", "text", 2_000_000)
    if "pg19" in want:
        data["pg19"] = docs("emozilla/pg19-test", None, "test", "text", 1_600_000)
    if "c4" in want:
        data["c4"] = docs("allenai/c4", "en", "validation", "text", 1_600_000)
    return data


def load_data(quick: bool, trivia_n: int, seed: int = 1234, sets: Optional[List[str]] = None) -> Dict[str, Any]:
    """The evaluation sets for one run: prepared once into DATA_CACHE (first run downloads; sets added later are fetched into the existing
    cache), then read from there. --quick subsamples HellaSwag, LAMBADA and GSM8K to 1,000 / 1,000 / 200 items with a fixed seed; TriviaQA
    is the first trivia_n of the cached fixed sample."""
    data = json.loads(DATA_CACHE.read_text(encoding="utf-8")) if DATA_CACHE.exists() else {}
    missing = [k for k in (sets or ALL_SETS) if k not in data]
    if missing:
        print(f"[Benchmark] Downloading the evaluation set(s) {', '.join(missing)} into {CACHE_DIR} (kept for later runs) ...", flush=True)
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        data.update(prepare_data(seed, missing))
        DATA_CACHE.write_text(json.dumps(data), encoding="utf-8")
    rng = random.Random(seed)
    for key, n in (("hellaswag", 1000), ("lambada", 1000), ("gsm8k", 200)):
        if quick and key in data:
            rng.shuffle(data[key])
            data[key] = data[key][:n]
    if "triviaqa" in data:
        data["triviaqa"] = data["triviaqa"][:trivia_n]
    return data


class Scorer:
    """Log-likelihood scoring and greedy decoding for one loaded model."""

    def __init__(self, model: GptModel, tokenizer: Any, device: torch.device):
        self.m, self.tok, self.dev = model, tokenizer, device
        self.eot, self.im_end = tokenizer.eos_id, tokenizer.token_id("<|im_end|>")
        # Scoring is restricted to the tokenizer's real text tokens: the embedding rows padded above them (and, for GPT-2 models
        # trained elsewhere, the ChatML/Phi/LLaMA special rows) were never trained and would otherwise leak probability mass.
        self.text_vocab = tokenizer.eos_id + 1 if tokenizer.arch_family == "gpt2" else tokenizer.n_vocab

    def logits(self, h: torch.Tensor) -> torch.Tensor:
        """fp32 logits over the text vocabulary for hidden states h (..., emb_dim)."""
        return self.m.out_head(h)[..., :self.text_vocab].float()

    def pair(self, ctx: str, cont: str) -> Tuple[List[int], List[int]]:
        c = self.tok.encode(ctx)
        return c, self.tok.encode(ctx + cont)[len(c):]

    @torch.inference_mode()
    def loglik(self, pairs: List[Tuple[List[int], List[int]]], bs: int = 32) -> List[Tuple[float, bool]]:
        """(summed log-probability of the continuation, whether every continuation token is the greedy choice) per (ctx, cont) pair;
        only the hidden states at the continuation positions go through the LM head."""
        out: List[Optional[Tuple[float, bool]]] = [None] * len(pairs)
        order = sorted(range(len(pairs)), key=lambda i: len(pairs[i][0]) + len(pairs[i][1]))
        for s in range(0, len(order), bs):
            idx = order[s:s + bs]
            seqs = [(pairs[i][0] + pairs[i][1])[-CONTEXT:] for i in idx]
            x = torch.full((len(idx), max(len(q) for q in seqs)), self.eot, dtype=torch.long, device=self.dev)
            for r, q in enumerate(seqs):
                x[r, :len(q)] = torch.tensor(q, device=self.dev)
            h = self.m.forward_features(x)
            for r, i in enumerate(idx):
                n, n_c = len(seqs[r]), len(pairs[i][1])
                lp = torch.log_softmax(self.logits(h[r, n - n_c - 1:n - 1]), -1)
                tgt = x[r, n - n_c:n]
                out[i] = (lp.gather(1, tgt[:, None]).sum().item(), bool((lp.argmax(-1) == tgt).all().item()))
        return out  # type: ignore[return-value]

    def multiple_choice(self, items: List[Dict[str, Any]], details: bool = False):
        """(acc, acc_norm) in percent over items with ctx / choices / gold; with details also the per-item hit lists (acc, acc_norm)."""
        res = self.loglik([self.pair(it["ctx"], ch) for it in items for ch in it["choices"]])
        k = 0
        hits: List[int] = []
        hits_norm: List[int] = []
        for it in items:
            n = len(it["choices"])
            raw = [res[k + j][0] for j in range(n)]
            per_char = [raw[j] / max(1, len(it["choices"][j])) for j in range(n)]
            hits.append(int(max(range(n), key=lambda j: raw[j]) == it["gold"]))
            hits_norm.append(int(max(range(n), key=lambda j: per_char[j]) == it["gold"]))
            k += n
        acc, acc_norm = 100 * sum(hits) / len(items), 100 * sum(hits_norm) / len(items)
        return (acc, acc_norm, hits, hits_norm) if details else (acc, acc_norm)

    def winogrande(self, items: List[Dict[str, Any]]) -> Tuple[float, List[int]]:
        """(accuracy in percent, per-item hits): the option whose prefix makes the shared continuation likelier wins."""
        res = self.loglik([self.pair(pre, it["cont"]) for it in items for pre in it["prefixes"]])
        hits = [int((res[2 * i][0] > res[2 * i + 1][0]) == (it["gold"] == 0)) for i, it in enumerate(items)]
        return 100 * sum(hits) / len(items), hits

    def lambada(self, items: List[Dict[str, Any]], details: bool = False):
        """(accuracy in percent, perplexity of the final word) lm-eval style; with details also the per-item hits."""
        res = self.loglik([self.pair(it["ctx"], it["target"]) for it in items])
        acc, ppl = 100 * sum(int(g) for _, g in res) / len(items), math.exp(-sum(lp for lp, _ in res) / len(items))
        return (acc, ppl, [int(g) for _, g in res]) if details else (acc, ppl)

    def perplexity_docs(self, docs: List[str], max_windows: int) -> Tuple[float, int]:
        """Perplexity over documents joined with <|endoftext|>, at most max_windows CONTEXT-token windows."""
        ids: List[int] = []
        for d in docs:
            ids += self.tok.encode(d) + [self.eot]
        return self.perplexity_ids(ids, max_windows)

    @torch.inference_mode()
    def perplexity_ids(self, ids: List[int], max_windows: Optional[int] = None, bs: int = 8) -> Tuple[float, int]:
        n = (len(ids) - 1) // CONTEXT
        n = min(n, max_windows) if max_windows else n
        nll = count = 0.0
        for s in range(0, n, bs):
            w = torch.tensor([ids[i * CONTEXT:(i + 1) * CONTEXT + 1] for i in range(s, min(n, s + bs))], device=self.dev)
            h = self.m.forward_features(w[:, :-1].contiguous())
            for r in range(w.shape[0]):  # one row at a time keeps the fp32 logits small
                nll += torch.nn.functional.cross_entropy(self.logits(h[r]), w[r, 1:], reduction="sum").item()
            count += w.shape[0] * CONTEXT
        return math.exp(nll / count), int(count)

    def gsm8k(self, items: List[Dict[str, Any]]) -> Tuple[float, List[int], float, List[str]]:
        """(accuracy in percent, per-item hits, average reply tokens, three example lines): zero-shot chat prompt, greedy, 256 new tokens;
        the last number in the reply (after '####' when the reply uses the GSM8K format) is the answer."""
        preds = self.greedy([self.tok.encode(format_chat_prompt([{"role": "user", "content": it["q"]}])) for it in items], max_new=256)
        num = re.compile(r"-?\d[\d,]*(?:\.\d+)?")
        def last_number(s: str) -> Optional[str]:
            m = num.findall(s.split("####")[-1] if "####" in s else s)
            return m[-1].replace(",", "").rstrip(".") if m else None
        def same(p: Optional[str], g: str) -> bool:
            try:
                return p is not None and abs(float(p) - float(g)) < 1e-6
            except ValueError:
                return False
        hits = [int(same(last_number(p), it["a"])) for p, it in zip(preds, items)]
        examples = [f"{'ok ' if h else 'MISS'} | {it['q'][:60]}... -> {p.strip()[-60:]!r} (answer: {it['a']})" for it, p, h in list(zip(items, preds, hits))[:3]]
        return 100 * sum(hits) / len(items), hits, sum(len(self.tok.encode(p)) for p in preds) / len(preds), examples

    @torch.inference_mode()
    def perplexity(self, text: str, max_windows: Optional[int] = None, bs: int = 8) -> Tuple[float, int]:
        """(perplexity, tokens scored) over non-overlapping CONTEXT-token windows of text."""
        ids = self.tok.encode(text)
        n = (len(ids) - 1) // CONTEXT
        n = min(n, max_windows) if max_windows else n
        nll = count = 0.0
        for s in range(0, n, bs):
            w = torch.tensor([ids[i * CONTEXT:(i + 1) * CONTEXT + 1] for i in range(s, min(n, s + bs))], device=self.dev)
            h = self.m.forward_features(w[:, :-1].contiguous())
            for r in range(w.shape[0]):  # one row at a time keeps the fp32 logits small
                nll += torch.nn.functional.cross_entropy(self.logits(h[r]), w[r, 1:], reduction="sum").item()
            count += w.shape[0] * CONTEXT
        return math.exp(nll / count), int(count)

    @torch.inference_mode()
    def greedy(self, prompts: List[List[int]], max_new: int, stop_at_newline: bool = False, chat: bool = True, bs: int = 32) -> List[str]:
        """Greedy continuations of many prompts, decoded in right-padded batches (every row keeps its own exact positions, so this
        equals one-by-one decoding) with a full forward per step; stops a row at <|endoftext|>, at <|im_end|> for chat models, or at a newline."""
        stops = {self.eot, self.im_end} if chat else {self.eot}
        outs: List[str] = [""] * len(prompts)
        order = sorted(range(len(prompts)), key=lambda i: len(prompts[i]))
        for s in range(0, len(order), bs):
            idx = order[s:s + bs]
            rows = [list(prompts[i][-(CONTEXT - max_new):]) for i in idx]
            lens = [len(r) for r in rows]
            gen: List[List[int]] = [[] for _ in idx]
            done = [False] * len(idx)
            for _ in range(max_new):
                width = max(lens)
                x = torch.full((len(idx), width), self.eot, dtype=torch.long, device=self.dev)
                for r, row in enumerate(rows):
                    x[r, :lens[r]] = torch.tensor(row, device=self.dev)
                last = self.m.forward_features(x)[torch.arange(len(idx), device=self.dev), torch.tensor(lens, device=self.dev) - 1]
                lg = self.m.out_head(last).float()
                lg[:, self.text_vocab:] = float("-inf")
                if chat:
                    lg[:, self.im_end] = self.m.out_head(last).float()[:, self.im_end]
                nxt = lg.argmax(-1).tolist()
                for r, t in enumerate(nxt):
                    if done[r]:
                        continue
                    if t in stops or (stop_at_newline and "\n" in self.tok.decode(gen[r][-1:] + [t])):
                        done[r] = True
                        continue
                    gen[r].append(t); rows[r].append(t); lens[r] += 1
                if all(done):
                    break
            for r, i in enumerate(idx):
                outs[i] = self.tok.decode(gen[r])
        return outs

    def triviaqa(self, items: List[Dict[str, Any]], chat: bool, details: bool = False):
        """(answer-contained %, exact-match %, three example lines; with details also the per-item hits). SQuAD-style normalization (case, punctuation, articles)."""
        def norm(s: str) -> str:
            s = "".join(ch for ch in s.lower() if ch not in set(string.punctuation))
            return " ".join(re.sub(r"\b(a|an|the)\b", " ", s).split())
        if chat:
            preds = self.greedy([self.tok.encode(format_chat_prompt([{"role": "user", "content": it["q"]}])) for it in items], max_new=40)
        else:
            preds = [p.split("\n")[0] for p in self.greedy([self.tok.encode(TRIVIA_SHOTS + "Q: " + it["q"] + "\nA:") for it in items], max_new=16, stop_at_newline=True, chat=False)]
        hits: List[int] = []
        exact = 0
        examples: List[str] = []
        for it, pred in zip(items, preds):
            p, aliases = norm(pred), [norm(a) for a in it["aliases"]]
            hit = any(a and a in p for a in aliases)
            hits.append(int(hit))
            exact += int(p in aliases)
            if len(examples) < 3:
                examples.append(f"{'ok ' if hit else 'MISS'} | {it['q'][:70]} -> {pred.strip()[:60]!r} (answer: {it['aliases'][0] if it['aliases'] else '?'})")
        contained, em = 100 * sum(hits) / len(items), 100 * exact / len(items)
        return (contained, em, examples, hits) if details else (contained, em, examples)


def se(p: float, n: int) -> float:
    """Standard error of a percentage over n items."""
    return 100 * math.sqrt(max(p / 100 * (1 - p / 100), 1e-9) / n)


def run_benchmark(model_name: str, weights: str = "pth", argv: Optional[List[str]] = None) -> int:
    """Runs the benchmarks on one model from the repository root, between the Running / [PASS] / [FAIL] banners. Returns a process exit code."""
    return run_test(f"Model Benchmark: {model_name}", "HellaSwag, ARC, SciQ, Winogrande, LAMBADA, TriviaQA, GSM8K, perplexities", lambda: _benchmark(model_name, weights, argv))


def _benchmark(model_name: str, weights: str, argv: Optional[List[str]]) -> int:
    parser = argparse.ArgumentParser(description=f"Benchmark {model_name}: " + ", ".join(ALL_SETS) + ".")
    parser.add_argument("--weights", choices=["pth", "trn", "sft", "dpo"], default=weights, help="Which weights to benchmark: the final .pth, or the pretraining / SFT / DPO stage checkpoint.")
    parser.add_argument("--models_base_dir", default="bin", help="Folder holding the model folders (default bin).")
    parser.add_argument("--device", default=None, help="cuda, cuda:N or cpu (default: cuda:0 when available).")
    parser.add_argument("--quick", type=str_to_bool, nargs="?", const=True, default=False, help="Subsample: 1,000 HellaSwag, 1,000 LAMBADA, 200 TriviaQA, 200 GSM8K, 100 perplexity windows (a few minutes).")
    parser.add_argument("--sets", default=",".join(ALL_SETS), help=f"Comma-separated benchmarks to run (default all: {','.join(ALL_SETS)}).")
    parser.add_argument("--trivia_n", type=int, default=1000, help="TriviaQA questions (fixed seeded sample of the validation split).")
    parser.add_argument("--trivia_mode", choices=["auto", "chat", "fewshot"], default="auto", help="How TriviaQA is asked: auto = chat format for fine-tuned weights, 5-shot Q/A for pretrained ('trn') weights. GSM8K is chat-only and skipped for pretrained weights.")
    parser.add_argument("--output_to_file", nargs="?", const="auto", default="auto", help="Write every score and the per-item correctness strings to a JSON file for gpttests/compare_models.py: a path, or (default) bin/<model>/<model with underscores>_benchmark.json; 'none' to skip.")
    a = parser.parse_args(argv)
    sets = [s.strip() for s in a.sets.split(",") if s.strip()]
    device = torch.device(a.device if a.device else ("cuda:0" if torch.cuda.is_available() else "cpu"))
    E = evaluate(model_name, a.models_base_dir, a.weights, device, sets, a.quick, 200 if a.quick else a.trivia_n, a.trivia_mode)
    M, n, chat, path = E["metrics"], E["n"], E["chat"], E["path"]
    refs = load_references()
    cls = size_class(E["n_params"], refs)
    R1, R2 = (refs["models"][refs["classes"][cls][k]] for k in ("baseline", "strong"))
    same_tok = [tokenizer_family(r.get("tokenizer")) == tokenizer_family(E["tokenizer"]) for r in (R1, R2)]

    def ref(r: Dict[str, Any], key: str, ok: bool = True) -> str:  # a reference's value for a set: "-" until measured, * when published
        v = r.get(key)
        return "n/a" if not ok else "-" if v is None else f"{v:.1f}" + ("*" if key in r.get("published", []) else "")

    def cols(key: str, score: float, ppl: bool = False) -> List[str]:  # the two reference columns of a row; perplexities only against references with the same tokenizer
        out = []
        for i, r in enumerate((R1, R2)):
            ok, v = not ppl or same_tok[i], r.get(key)
            out += [ref(r, key, ok), "-" if v is None or not ok else f"{score - v:+.2f}" if ppl else f"{score - v:+.1f}"]
        return out

    w = 118
    row = lambda b, metric, score, count, err, chance, r1, d1, r2, d2, notes: f" {b:<13} {metric:<11} {score:>8} {count:>9} {err:>6} {chance:>7} {r1:>15} {d1:>8} {r2:>15} {d2:>8}   {notes}"
    lines = [row("benchmark", "metric", "score", "n", "+-SE", "chance", R1["label"][:15], "diff", R2["label"][:15], "diff", "notes")]
    for key in ("hellaswag", "arc_easy", "arc_challenge", "sciq"):
        if key in M:
            acc, acc_norm = M[key], M[key + "_norm"]
            metric, score, note = ("acc_norm", acc_norm, f"acc {acc:.1f} %") if key == "hellaswag" else ("acc", acc, f"acc_norm {acc_norm:.1f} %")  # lm-eval's headline metric per set
            lines.append(row(key, metric, f"{score:.1f} %", f"{n[key]:,}", f"{se(score, n[key]):.1f}", f"{CHANCE.get(key, 25.0):.1f}", *cols(key, score), note))
    if "winogrande" in M:
        lines.append(row("winogrande", "acc", f"{M['winogrande']:.1f} %", f"{n['winogrande']:,}", f"{se(M['winogrande'], n['winogrande']):.1f}", "50.0", *cols("winogrande", M["winogrande"]), "pronoun resolution, partial evaluation"))
    if "lambada" in M:
        lines.append(row("lambada", "acc", f"{M['lambada']:.1f} %", f"{n['lambada']:,}", f"{se(M['lambada'], n['lambada']):.1f}", f"{CHANCE['lambada']:.1f}", *cols("lambada", M["lambada"]), f"perplexity {M['lambada_ppl']:.2f} ({R1['label']} {ref(R1, 'lambada_ppl')}, {R2['label']} {ref(R2, 'lambada_ppl')})"))
    if "triviaqa" in M:
        lines.append(row("triviaqa", "correct", f"{M['triviaqa']:.1f} %", f"{n['triviaqa']:,}", f"{se(M['triviaqa'], n['triviaqa']):.1f}", f"{CHANCE['triviaqa']:.1f}", *cols("triviaqa", M["triviaqa"]), f"answer contained in the reply; {'chat prompt, greedy' if chat else '5-shot Q/A'}; exact match {M['triviaqa_em']:.1f} %"))
    if "gsm8k" in M:
        lines.append(row("gsm8k", "acc", f"{M['gsm8k']:.1f} %", f"{n['gsm8k']:,}", f"{se(M['gsm8k'], n['gsm8k']):.1f}", "0.0", *cols("gsm8k", M["gsm8k"]), f"zero-shot chat, greedy; last number of the reply; avg reply {M['gsm8k_reply_tokens']:.0f} tokens"))
    if "wikitext_ppl" in M:
        lines.append(row("wikitext", "perplexity", f"{M['wikitext_ppl']:.2f}", f"{n['wikitext']:,}", "-", "-", *cols("wikitext", M["wikitext_ppl"], ppl=True), "lower is better; n = tokens; WikiText-103 test; same tokenizer only; compare same-recipe models"))
    for key, note in (("fineweb_edu", "in the andres-350M-2 pretraining recipe"), ("pg19", "PG-19 books: in no andres recipe"), ("c4", "C4 web text: in no andres recipe")):
        if key + "_ppl" in M:
            lines.append(row(key, "perplexity", f"{M[key + '_ppl']:.2f}", f"{n[key]:,}", "-", "-", *cols(key, M[key + "_ppl"], ppl=True), f"lower is better; n = tokens; {note}"))
    print("\n" + "=" * w + f"\n Benchmark results: {model_name}  [{path.name}]\n" + "=" * w)
    print(f" Size class {cls} ({E['n_params'] / 1e6:.1f}M params). References: " + " | ".join(
        f"{r['label']} ({r.get('params_M', 0):,.0f}M, {'measured ' + r['measured'] if r.get('measured') else 'not measured yet'}{'; * published: ' + r['published_source'] if r.get('published') else ''})" for r in (R1, R2)))
    print("\n".join(lines))
    if E["examples"]:
        print("-" * w + "\n Samples:\n   " + "\n   ".join(E["examples"]))
    print(f" Elapsed: {E['elapsed']:.0f}s{'  (quick mode: subsampled)' if a.quick else ''}\n" + "=" * w, flush=True)
    if a.output_to_file and a.output_to_file.lower() != "none":
        out = Path(a.output_to_file) if a.output_to_file != "auto" else Path(a.models_base_dir) / model_name / f"{model_name.replace('-', '_')}_benchmark.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps({"kind": "benchmark", "model": model_name, "weights": a.weights, "weights_file": str(path), "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"), "quick": a.quick,
                                   "chat_prompts": chat, "elapsed_sec": round(E["elapsed"]), "metrics": M, "n": n, "items": E["items"]}, indent=1), encoding="utf-8")
        print(f"[Output] Results written to {out}  (compare with: python gpttests/compare_models.py <this file> <another model's file>)")
    return 0


def evaluate(model_name: str, models_base_dir: str, weights: str, device: torch.device, sets: Any = ALL_SETS, quick: bool = False, trivia_n: int = 1000, trivia_mode: str = "auto") -> Dict[str, Any]:
    """Runs the requested benchmark sets on one model (also used by prepare_references.py): metrics (the keys the JSON output uses),
    per-item correctness strings for paired tests, item counts, sample lines, plus what the table needs (parameter count, tokenizer, weights path)."""
    t0 = time.time()
    model, path = load_model(model_name, models_base_dir, weights, device)
    cfg = load_model_config(ModelArgs(model_name=model_name, models_base_dir=models_base_dir)) or {}
    tokenizer = get_tokenizer(cfg, ModelArgs(model_name=model_name, models_base_dir=models_base_dir))
    print(f"[Benchmark] {model_name}: weights {path.name} ({'bf16' if device.type == 'cuda' else 'fp32'} on {device}) | evaluation sets from {CACHE_DIR}", flush=True)
    data = load_data(quick, trivia_n, sets=list(sets))
    sc = Scorer(model, tokenizer, device)
    chat = (weights != "trn") if trivia_mode == "auto" else (trivia_mode == "chat")
    M: Dict[str, Any] = {}      # metric -> value
    items: Dict[str, str] = {}  # metric -> per-item correctness string, for paired tests between models
    n: Dict[str, int] = {}
    examples: List[str] = []
    for key in ("hellaswag", "arc_easy", "arc_challenge", "sciq"):
        if key in sets:
            acc, acc_norm, hits, hits_norm = sc.multiple_choice(data[key], details=True)
            M[key], M[key + "_norm"], n[key] = acc, acc_norm, len(hits)
            items[key], items[key + "_norm"] = "".join(map(str, hits)), "".join(map(str, hits_norm))
    if "winogrande" in sets:
        M["winogrande"], hits = sc.winogrande(data["winogrande"]); n["winogrande"] = len(hits); items["winogrande"] = "".join(map(str, hits))
    if "lambada" in sets:
        M["lambada"], M["lambada_ppl"], hits = sc.lambada(data["lambada"], details=True); n["lambada"] = len(hits); items["lambada"] = "".join(map(str, hits))
    if "triviaqa" in sets:
        M["triviaqa"], M["triviaqa_em"], ex, hits = sc.triviaqa(data["triviaqa"], chat, details=True); n["triviaqa"] = len(hits); items["triviaqa"] = "".join(map(str, hits)); examples += ex
    if "gsm8k" in sets and chat:
        M["gsm8k"], hits, M["gsm8k_reply_tokens"], ex = sc.gsm8k(data["gsm8k"]); n["gsm8k"] = len(hits); items["gsm8k"] = "".join(map(str, hits)); examples += ex
    if "wikitext" in sets:
        M["wikitext_ppl"], n["wikitext"] = sc.perplexity(data["wikitext"], 100 if quick else None)
    for key in ("fineweb_edu", "pg19", "c4"):
        if key in sets:
            M[key + "_ppl"], n[key] = sc.perplexity_docs(data[key], 100 if quick else (400 if key == "fineweb_edu" else 300))
    return {"metrics": M, "items": items, "n": n, "examples": examples, "chat": chat, "path": path,
            "n_params": sum(p.numel() for p in model.parameters()), "tokenizer": cfg.get("tokenizer", "gpt2"), "elapsed": time.time() - t0}


if __name__ == "__main__":
    p = argparse.ArgumentParser(add_help=False)
    p.add_argument("--model_name", required=True)
    known, rest = p.parse_known_args()
    sys.exit(run_benchmark(known.model_name, argv=rest))
