# Copyright (c) Sebastian Raschka under Apache License 2.0 (see LICENSE.txt).
# Head-to-head material shared by the data test (which generates the replies and stores them in its --output_to_file) and
# gpttests/compare_models.py (which has the Gemma judge compare two models' replies, both A/B orders, and runs a sign test).
#
# 40 fixed prompts in six categories, two seeds each = 80 pairs per model pair. A win needs the same verdict in both orders; anything
# else is a tie, so position bias cannot manufacture a winner. Verdicts are cached on disk by content, so re-comparing is free.

import hashlib
import json
import math
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

PROMPTS: List[Tuple[str, str]] = [
    ("factual", "What is the capital of Australia?"), ("factual", "Who painted the Mona Lisa?"), ("factual", "What is the largest planet in our solar system?"),
    ("factual", "How many continents are there? Please name them."), ("factual", "What language is spoken in Brazil?"), ("factual", "Who was the first president of the United States?"),
    ("factual", "What is the boiling point of water in Celsius?"), ("factual", "What is photosynthesis?"), ("factual", "Which ocean is the largest?"), ("factual", "Who wrote the novel Pride and Prejudice?"),
    ("explain", "Explain in simple terms how a rainbow forms."), ("explain", "Give me three tips for falling asleep faster."), ("explain", "How do I boil an egg?"),
    ("explain", "Explain the difference between weather and climate."), ("explain", "Why is the sky blue?"), ("explain", "What are some good ways to save money each month?"),
    ("explain", "How does a refrigerator keep food cold?"), ("explain", "Explain what a noun is and give two examples."),
    ("reasoning", "If I have 3 apples and eat one, then buy 4 more, how many apples do I have?"), ("reasoning", "Which is heavier, a kilogram of feathers or a kilogram of iron? Explain."),
    ("reasoning", "Tom is taller than Sam. Sam is taller than Ann. Who is the shortest?"), ("reasoning", "What comes next in the sequence 2, 4, 6, 8?"),
    ("reasoning", "I put a glass of water in the freezer overnight. What will I find in the morning and why?"), ("reasoning", "Is a tomato a fruit or a vegetable? Explain briefly."),
    ("creative", "Write a short poem about autumn leaves."), ("creative", "Write a two-sentence horror story."), ("creative", "Write a short story about a robot who learns to paint."),
    ("creative", "Describe a sunset over the mountains in one paragraph."), ("creative", "Write a limerick about a cat who loves pizza."), ("creative", "Write a short dialogue between a customer and a barista."),
    ("creative", "Invent a new holiday and describe how people celebrate it."), ("creative", "Write a short thank-you note to a teacher."),
    ("rewrite", "Summarize this in one sentence: The city council met on Tuesday to discuss the new park proposal. After three hours of debate, they voted 7 to 2 in favor of building the park, which will include a playground, a dog run, and a community garden. Construction is expected to begin next spring."),
    ("rewrite", "Rewrite this sentence to be more formal: 'Hey, can you send me that report real quick?'"), ("rewrite", "Fix the grammar in this sentence: 'Me and him goes to the store yesterday and buyed some apple.'"),
    ("rewrite", "Turn this shopping list into one sentence: milk, eggs, bread, butter."),
    ("math", "What is 15 + 27?"), ("math", "What is 12 times 8?"), ("math", "If a shirt costs $20 and is 25% off, what is the sale price?"), ("math", "What is half of 90?"),
]
CATEGORIES = list(dict.fromkeys(c for c, _ in PROMPTS))
SEEDS = [1234, 1235]

JUDGE_SYSTEM = ("You are a strict, impartial judge comparing two answers written by two small language models to the same user prompt. "
                "Judge correctness first (a false statement, an invented fact or wrong arithmetic is a serious flaw), then whether the answer actually does what "
                "was asked, then coherence and fluency (repetition loops, restarts, drifting off topic, cut-off endings are flaws). Length by itself is not a virtue; "
                "a short correct answer beats a long answer with one error. Reply with JSON only.")
JUDGE_SCHEMA = {"type": "object", "properties": {"winner": {"type": "string", "enum": ["A", "B", "tie"]}, "reason": {"type": "string"}}, "required": ["winner", "reason"]}


def generate_replies(ctx: Dict[str, Any], seeds: List[int] = SEEDS) -> Dict[str, Dict[str, Any]]:
    """Every prompt x seed through the normal inference path (the model's own options-infer.json settings), fresh conversation each time.
    Returns {"<prompt index>|<seed>": {"resp", "tokens", "truncated"}}."""
    from gptinfer.session import run_generation
    out: Dict[str, Dict[str, Any]] = {}
    for i, (_, prompt) in enumerate(PROMPTS):
        for s in seeds:
            resp, st = run_generation(ctx=ctx, conversation_messages=[], user_input=prompt, stream=False, seed=s)
            out[f"{i}|{s}"] = {"resp": resp, "tokens": st["tokens"], "truncated": st["tokens"] >= st.get("allowed_new_tokens", 10 ** 9)}
    return out


class PairwiseJudge:
    """Gemma judge for two replies to one prompt, asked in both A/B orders; verdicts cached on disk by content hash."""

    def __init__(self, gpu_index: int):
        import torch  # noqa: F401  (must precede llama_cpp: the CUDA wheel resolves its DLLs from torch\lib)
        from llama_cpp import Llama, LLAMA_SPLIT_MODE_NONE
        from gpttests.data.modelrefs import JUDGE_DIR, JUDGE_FILENAME
        self.cache_path: Path = JUDGE_DIR / "pairwise_cache.json"
        self.cache: Dict[str, Any] = json.loads(self.cache_path.read_text(encoding="utf-8")) if self.cache_path.exists() else {}
        self.llm = Llama(model_path=str(JUDGE_DIR / JUDGE_FILENAME), n_gpu_layers=-1, main_gpu=gpu_index, split_mode=LLAMA_SPLIT_MODE_NONE, n_ctx=8192, seed=0, verbose=False)

    def ask(self, prompt: str, ra: str, rb: str) -> Dict[str, Any]:
        if not ra.strip() or not rb.strip():  # an empty reply loses without asking (the judge is unreliable on empties)
            return {"winner": "tie" if ra.strip() == rb.strip() else ("B" if not ra.strip() else "A"), "reason": "empty response loses automatically"}
        key = hashlib.sha256(json.dumps([prompt, ra, rb]).encode("utf-8")).hexdigest()
        if key not in self.cache:
            user = f"PROMPT:\n{prompt}\n\nRESPONSE A:\n{ra}\n\nRESPONSE B:\n{rb}\n\nReturn JSON: {{\"winner\": \"A\" | \"B\" | \"tie\", \"reason\": \"one short sentence\"}}"
            messages = [{"role": "system", "content": JUDGE_SYSTEM}, {"role": "user", "content": user}]
            verdict = None
            for max_tokens in (200, 800):  # the reason can run past the limit and cut the JSON: retry once with room
                try:
                    verdict = json.loads(self.llm.create_chat_completion(messages=messages, temperature=0.0, max_tokens=max_tokens, response_format={"type": "json_object", "schema": JUDGE_SCHEMA})["choices"][0]["message"]["content"])
                    break
                except json.JSONDecodeError:
                    continue
            self.cache[key] = verdict or {"winner": "tie", "reason": "judge reply cut off twice"}
            self.cache_path.parent.mkdir(parents=True, exist_ok=True)
            self.cache_path.write_text(json.dumps(self.cache), encoding="utf-8")
        return self.cache[key]

    def compare(self, a: str, b: str, replies_a: Dict[str, Dict[str, Any]], replies_b: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Judges every prompt x seed both models answered. Returns the per-pair rows and the win/tie/loss tallies (overall and per category)."""
        rows = []
        for i, (cat, prompt) in enumerate(PROMPTS):
            for key in sorted(k for k in replies_a if k.startswith(f"{i}|") and k in replies_b):
                ra, rb = replies_a[key]["resp"], replies_b[key]["resp"]
                v1, v2 = self.ask(prompt, ra, rb), self.ask(prompt, rb, ra)
                p1 = {"A": a, "B": b, "tie": "tie"}[v1["winner"]]
                p2 = {"A": b, "B": a, "tie": "tie"}[v2["winner"]]
                rows.append({"i": i, "cat": cat, "key": key, "final": p1 if p1 == p2 else "tie", "order1": p1, "order2": p2, "reason1": v1["reason"], "reason2": v2["reason"]})
        return {"a": a, "b": b, "overall": tally(rows, a, b), "by_category": {c: tally([r for r in rows if r["cat"] == c], a, b) for c in CATEGORIES}, "rows": rows}


def tally(rows: List[Dict[str, Any]], a: str, b: str) -> Dict[str, Any]:
    """Wins of a, ties, wins of b and the two-sided sign-test p-value on the decided pairs."""
    wa = sum(r["final"] == a for r in rows); wb = sum(r["final"] == b for r in rows); n = wa + wb
    p = min(1.0, 2 * sum(math.comb(n, k) for k in range(0, min(wa, wb) + 1)) / 2 ** n) if n else 1.0
    return {"n": len(rows), "a_wins": wa, "ties": len(rows) - n, "b_wins": wb, "sign_test_p": p}


def avg_tokens(replies: Dict[str, Dict[str, Any]], category: Optional[str] = None) -> float:
    """Average reply length in tokens over the prompts of one category (or all)."""
    t = [v["tokens"] for k, v in replies.items() if category is None or PROMPTS[int(k.split("|")[0])][0] == category]
    return sum(t) / len(t) if t else float("nan")
