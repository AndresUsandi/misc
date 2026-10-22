# Copyright (c) Sebastian Raschka under Apache License 2.0 (see LICENSE.txt).
"""
Compares two or more models from the JSON files their tests wrote with --output_to_file:

    python gpttests/benchmark/benchcore.py --model_name <model> --weights pth --output_to_file
    python gpttests/data/testcore.py --model_name <model> --output_to_file
    python gpttests/compare_models.py <file> <file> [<file> ...] [--reference <model>] [--html <report.html>] [--judge_gpu N] [--pairs a:b,...]

Pass any mix of benchmark and data files; files are grouped by model name, so a model may contribute one of each. The report has:
  benchmarks   every metric both files share, best value marked, and for accuracies an exact McNemar p-value against the reference model
               (default: the first model given) computed from the per-item correctness strings - the right test for paired results.
  chat quality the 20-turn suite (judge passes, mean score, story turns, loops, one-word answers) and the 635-sample extended factual suite
               (passes with standard error, core-answer-wrong vs right-but-added-claim failure profile, reply length).
  head-to-head when the data files carry the 40-prompt replies and --judge_gpu is given: the Gemma judge compares every pair of models
               (or only --pairs a:b,c:d), both A/B orders, with a two-sided sign test and a per-category breakdown; reply lengths by category.
Prints Markdown to the console; --html also writes a standalone HTML page. In both, the reference model's numbers are uncoloured and every
other model's number is green when it beats the reference and red when it falls short, with the direction decided per measurement
(accuracies and judge passes: higher is better; perplexities, loops, one-word answers, core-wrong and added-claim shares: lower is better;
reply lengths and p-values carry no colour; head-to-head cells are coloured only where a model faces the reference, by wins against losses).
"""
import argparse
import html
import json
import math
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

ACC = [("hellaswag_norm", "HellaSwag acc_norm"), ("arc_easy", "ARC-Easy acc"), ("arc_challenge_norm", "ARC-Challenge acc_norm"), ("sciq_norm", "SciQ acc_norm"),
       ("winogrande", "Winogrande acc"), ("lambada", "LAMBADA acc"), ("triviaqa", "TriviaQA answer-contained"), ("triviaqa_em", "TriviaQA exact match"), ("gsm8k", "GSM8K zero-shot acc")]
PPL = [("lambada_ppl", "LAMBADA perplexity"), ("wikitext_ppl", "WikiText-103 perplexity"), ("fineweb_edu_ppl", "FineWeb-Edu perplexity"), ("pg19_ppl", "PG-19 perplexity"), ("c4_ppl", "C4 perplexity")]
ITEM_KEY = {"triviaqa_em": None}  # metrics without a per-item string


def mcnemar(a: str, b: str) -> float:
    """Exact two-sided McNemar test on the items the two models disagree on ('1'/'0' strings of equal length)."""
    x = sum(1 for p, q in zip(a, b) if p == "1" and q == "0"); y = sum(1 for p, q in zip(a, b) if p == "0" and q == "1"); n = x + y
    return min(1.0, 2 * sum(math.comb(n, k) for k in range(0, min(x, y) + 1)) / 2 ** n) if n else 1.0


UP, DOWN = "\x1fg", "\x1fr"  # cell markers: better / worse than the reference model (rendered as green / red)


def tint(text: str, value: Optional[float], ref_value: Optional[float], higher: Optional[bool]) -> str:
    """text, marked green when value is better than ref_value and red when worse (higher=True: more is better; False: less is better;
    None or missing values or a tie: no colour)."""
    if higher is None or value is None or ref_value is None or value == ref_value:
        return text
    mark = UP if (value > ref_value) == higher else DOWN
    return f"**{mark}{text[2:-2]}**" if text.startswith("**") and text.endswith("**") else mark + text  # keep the best-value '**' outermost


def load(paths: List[str]) -> Dict[str, Dict[str, Any]]:
    """{model: {"benchmark": ..., "data": ...}} in order of first appearance."""
    models: Dict[str, Dict[str, Any]] = {}
    for p in paths:
        d = json.loads(Path(p).read_text(encoding="utf-8"))
        models.setdefault(d["model"], {})[d["kind"]] = d
    return models


class Report:
    """Collects tables as (title, headers, rows, note) and renders them as Markdown or HTML."""

    def __init__(self) -> None:
        self.parts: List[Any] = []

    def table(self, title: str, headers: List[str], rows: List[List[str]], note: str = "") -> None:
        self.parts.append((title, headers, rows, note))

    @staticmethod
    def split(c: Any):
        """(text, best, tint) of a cell: '**' wraps the best value, a leading UP / DOWN marker the colour."""
        s = str(c); best = s.startswith("**") and s.endswith("**") and len(s) > 4
        s = s[2:-2] if best else s
        col = "g" if s.startswith(UP) else "r" if s.startswith(DOWN) else None
        return (s[2:] if col else s), best, col

    def markdown(self) -> str:
        out = []
        colour = {"g": "#3fb950", "r": "#f85149"}  # readable on the dark preview and on white
        def cell(c):
            text, best, col = self.split(c)
            text = f'<span style="color:{colour[col]}">{text}</span>' if col else text
            return f"**{text}**" if best else text
        for title, headers, rows, note in self.parts:
            out.append(f"\n### {title}\n")
            out.append("| " + " | ".join(headers) + " |")
            out.append("|" + "|".join("---" if i == 0 else "---:" for i in range(len(headers))) + "|")
            out += ["| " + " | ".join(cell(c) for c in r) + " |" for r in rows]
            if note:
                out.append(f"\n_{note}_")
        return "\n".join(out)

    def html(self, title: str) -> str:
        css = ("body{font:14px/1.5 -apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;color:#1b1f23;max-width:1240px;margin:32px auto;padding:0 20px}"
               "h1{font-size:24px}h2{font-size:17px;margin:28px 0 8px;border-bottom:1px solid #e1e4e8;padding-bottom:4px}table{border-collapse:collapse;width:100%;font-size:12.5px;margin:8px 0}"
               "th,td{border:1px solid #e1e4e8;padding:5px 7px;text-align:right;white-space:nowrap}th:first-child,td:first-child{text-align:left;white-space:normal}th{background:#f6f8fa}"
               "td.best{background:#f0fff4;font-weight:600}td.g{color:#1a7f37}td.r{color:#cf222e}p.note{color:#57606a;font-size:12px}")
        body = [f"<h1>{html.escape(title)}</h1>"]
        def cell(c):
            text, best, col = self.split(c)
            cls = " ".join(x for x in (("best" if best else ""), (col or "")) if x)
            return f"<td class=\"{cls}\">{html.escape(text)}</td>" if cls else f"<td>{html.escape(text)}</td>"
        for t, headers, rows, note in self.parts:
            body.append(f"<h2>{html.escape(t)}</h2><table><tr>" + "".join(f"<th>{html.escape(h)}</th>" for h in headers) + "</tr>" + "".join("<tr>" + "".join(cell(c) for c in r) + "</tr>" for r in rows) + "</table>" + (f"<p class=note>{html.escape(note)}</p>" if note else ""))
        return f"<!doctype html><html><head><meta charset=utf-8><title>{html.escape(title)}</title><style>{css}</style></head><body>{''.join(body)}</body></html>"


def best_mark(values: Dict[str, Optional[float]], higher: bool) -> Optional[str]:
    v = {m: x for m, x in values.items() if x is not None}
    return (max if higher else min)(v, key=v.get) if len(v) > 1 else None


def benchmark_tables(models: Dict[str, Dict[str, Any]], ref: str, rep: Report) -> None:
    B = {m: d["benchmark"] for m, d in models.items() if "benchmark" in d}
    if len(B) < 2:
        return
    names = list(B)
    rows = []
    for key, label in ACC:
        vals = {m: B[m]["metrics"].get(key) for m in names}
        if sum(v is not None for v in vals.values()) < 2:
            continue
        best = best_mark(vals, True)
        cells = [f"**{vals[m]:.1f}%**" if m == best else (f"{vals[m]:.1f}%" if vals[m] is not None else "-") for m in names]
        cells = [c if m == ref else tint(c, vals[m], vals.get(ref), True) for m, c in zip(names, cells)]
        ps = []
        for m in [x for x in names if x != ref]:
            if vals[m] is None or vals.get(ref) is None or key not in B[m]["items"] or key not in B[ref]["items"]:
                ps.append("-")
            else:
                ps.append(f"{mcnemar(B[m]['items'][key], B[ref]['items'][key]):.2g}" if len(B[m]["items"][key]) == len(B[ref]["items"][key]) else "n differs")
        rows.append([label] + cells + ps)
    for key, label in PPL:
        vals = {m: B[m]["metrics"].get(key) for m in names}
        if sum(v is not None for v in vals.values()) < 2:
            continue
        best = best_mark(vals, False)
        cells = [f"**{vals[m]:.2f}**" if m == best else (f"{vals[m]:.2f}" if vals[m] is not None else "-") for m in names]
        rows.append([label + " (lower is better)"] + [c if m == ref else tint(c, vals[m], vals.get(ref), False) for m, c in zip(names, cells)] + ["" for _ in names if _ != ref])
    weights = ", ".join(f"{m}: {B[m]['weights_file'].split(chr(92))[-1].split('/')[-1]}" for m in names)
    rep.table("Benchmarks", ["benchmark"] + names + [f"p: {m} vs {ref}" for m in names if m != ref], rows,
              f"Best value per row marked. p = exact McNemar test on the items the two models disagree on (paired; needs the same evaluation set size). Weights: {weights}.")


def data_tables(models: Dict[str, Dict[str, Any]], ref: str, rep: Report) -> None:
    D = {m: d["data"] for m, d in models.items() if "data" in d}
    if len(D) < 2:
        return
    names = list(D)
    S = {m: D[m]["summary"] for m in names}
    def row(label: str, part: str, fmt, higher: Optional[bool]):
        vals = {m: (fmt(S[m][part]) if S[m].get(part, {}).get("n") else None) for m in names}
        nums = {m: (v[0] if isinstance(v, tuple) else None) for m, v in vals.items()}
        best = best_mark(nums, higher) if higher is not None else None
        return [label] + [(tint(f"**{v[1]}**" if m == best else v[1], nums[m], nums.get(ref), None if m == ref else higher)) if v else "-" for m, v in vals.items()]
    pct = lambda s: (s["judge_pass_pct"], f"{s['judge_pass']}/{s['n']} ({s['judge_pass_pct']:.1f}% +-{s['se']})")
    passes = lambda s: (s["judge_pass"], f"{s['judge_pass']}/{s['n']} ({s['judge_mean']})")
    share = lambda k: (lambda s: (100 * s[k] / s["n"], f"{100 * s[k] / s['n']:.1f}%"))
    count = lambda k: (lambda s: (s[k], str(s[k])))
    rows = [row("factual turns, judge passes (mean score 1-5)", "factual", passes, True), row("creative turns, judge passes (mean score 1-5)", "creative", passes, True),
            row("all turns, judge passes", "base", passes, True), row("multi-turn story turns, judge passes", "story", passes, True),
            row("harness turns passed", "base", lambda s: (s["turns_passed"], f"{s['turns_passed']}/{s['turns']}"), True),
            row("repetition loops / truncations", "base", count("loops_or_truncations"), False), row("one-word answers", "base", count("one_word"), False),
            ["average reply tokens, factual / creative"] + [f"{S[m]['factual']['avg_tokens']:.0f} / {S[m]['creative']['avg_tokens']:.0f}" if S[m].get("factual", {}).get("n") else "-" for m in names]]
    samples = ", ".join(sorted({str(D[m]["settings"]["samples"]) for m in names}))
    rep.table(f"Chat quality: the 20-turn suite ({samples} seeded sample(s) per turn)", ["measurement"] + names, [r for r in rows if r])
    if all(S[m].get("factual_extended", {}).get("n") for m in names):
        rows = [row("factual, all questions: judge passes", "factual_all", pct, True), row("  single-turn questions", "single_turn", pct, True), row("  pronoun follow-ups in the extended threads", "pronoun_followups", pct, True),
                row("  the original 10 factual turns", "factual", pct, True), row("  mean judge score (1-5)", "factual_all", lambda s: (s["judge_mean"], str(s["judge_mean"])), True),
                row("  failure: core answer wrong", "factual_all", share("core_wrong"), False), row("  failure: core right, an added claim rejected", "factual_all", share("right_but_judge_fail"), False),
                row("  average factual reply tokens", "factual_all", lambda s: (s["avg_tokens"], str(s["avg_tokens"])), None)]
        rep.table("Chat quality: the extended factual suite (127 questions x 5 seeds)", ["measurement"] + names, rows,
                  "+- is one standard error of the percentage. 'Added claim rejected': the expected answer is present but the judge failed the reply (an invented date, place or detail).")

def head_to_head_tables(models: Dict[str, Dict[str, Any]], ref: str, judge_gpu: Optional[int], pairs: Optional[List[str]], rep: Report) -> None:
    from gpttests.data.headtohead import CATEGORIES, PROMPTS, avg_tokens
    H = {m: d["data"]["head_to_head"]["replies"] for m, d in models.items() if d.get("data", {}).get("head_to_head")}
    if len(H) < 2:
        return
    names = list(H)
    rep.table("Reply length on the 40 head-to-head prompts (average tokens)", ["category"] + names,
              [[c] + [f"{avg_tokens(H[m], c):.0f}" for m in names] for c in CATEGORIES] + [["all"] + [f"{avg_tokens(H[m]):.0f}" for m in names]])
    if judge_gpu is None:
        rep.table("Head-to-head", ["note"], [["replies are present for " + ", ".join(names) + "; add --judge_gpu N to have the judge compare them"]])
        return
    from gpttests.data.headtohead import PairwiseJudge
    judge = PairwiseJudge(judge_gpu)
    wanted = [tuple(p.split(":")) for p in pairs] if pairs else [(a, b) for i, a in enumerate(names) for b in names[i + 1:]]
    results = {}
    for a, b in wanted:
        if a in H and b in H:
            print(f"[Head-to-head] judging {a} vs {b} ...", flush=True)
            results[(a, b)] = judge.compare(a, b, H[a], H[b])
    def record(a: str, b: str):
        """(a's wins, ties, b's wins, p) from whichever orientation was judged, or None."""
        if (a, b) in results:
            r = results[(a, b)]["overall"]; return r["a_wins"], r["ties"], r["b_wins"], r["sign_test_p"]
        if (b, a) in results:
            r = results[(b, a)]["overall"]; return r["b_wins"], r["ties"], r["a_wins"], r["sign_test_p"]
        return None
    matrix = []
    for a in names:
        line = [a]
        for b in names:
            rec = record(a, b)
            text = "-" if a == b else (f"{rec[0]}-{rec[1]}-{rec[2]} (p {rec[3]:.2g})" if rec else "not judged")
            line.append(tint(text, rec[0], rec[2], True) if rec and b == ref and a != ref else text)  # a model's record against the reference: more wins than losses = green
        matrix.append(line)
    rep.table("Head-to-head: row wins - ties - column wins (80 pairs; p = two-sided sign test)", ["model"] + names, matrix,
              f"{len(PROMPTS)} prompts x 2 seeds, judged in both A/B orders; a win needs the same verdict in both orders. Empty replies lose automatically.")
    for (a, b), r in results.items():
        rows = []
        for c, t in r["by_category"].items():
            aw, bw = str(t["a_wins"]), str(t["b_wins"])
            if b == ref: aw = tint(aw, t["a_wins"], t["b_wins"], True)   # the non-reference model's wins against the reference's
            elif a == ref: bw = tint(bw, t["b_wins"], t["a_wins"], True)
            rows.append([c, aw, str(t["ties"]), bw, f"{t['sign_test_p']:.2g}"])
        rep.table(f"Head-to-head by category: {a} vs {b}", ["category", f"{a} wins", "ties", f"{b} wins", "p"], rows)


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("files", nargs="+", help="Result files written with --output_to_file (benchmark and/or data), two or more models.")
    p.add_argument("--reference", default=None, help="Model the benchmark p-values and the green/red colouring are computed against (default: the first model given).")
    p.add_argument("--html", default=None, help="Also write the report as a standalone HTML page to this path.")
    p.add_argument("--judge_gpu", type=int, default=None, help="Run the head-to-head judge on this CUDA device (needs the data files' replies; verdicts are cached).")
    p.add_argument("--pairs", default=None, help="Only judge these pairs, e.g. modelA:modelB,modelA:modelC (default: every pair).")
    a = p.parse_args(argv)
    models = load(a.files)
    if len(models) < 2:
        print("Need result files from at least two different models."); return 1
    ref = a.reference or next(iter(models))
    if ref not in models:
        print(f"--reference {ref} is not among the models given: {', '.join(models)}"); return 1
    rep = Report()
    benchmark_tables(models, ref, rep)
    data_tables(models, ref, rep)
    head_to_head_tables(models, ref, a.judge_gpu, a.pairs.split(",") if a.pairs else None, rep)
    title = "Model comparison: " + " vs ".join(models)
    print(f"# {title}\n" + rep.markdown())
    if a.html:
        Path(a.html).write_text(rep.html(title), encoding="utf-8")
        print(f"\n[Output] HTML report written to {a.html}")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
