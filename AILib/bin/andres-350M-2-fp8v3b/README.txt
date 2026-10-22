andres-350M-2-fp8v3b
====================
The best pieces of the lineage combined: andres-350M-2-fp8's pretraining, andres-350M-2-fp8v3's SFT (the v2b recipe plus math data) and
andres-350M-2-fp8v2d's DPO recipe (preference sets that point away from elaboration, with a 0.2 anchor). In theory the best model so far.

RECIPE
  Pretraining: andres-350M-2-fp8's checkpoint, unchanged (copy v3's .chk.trn in as andres-350M-2-fp8v3b.chk.trn; it is bit-identical to it).
  SFT:         andres-350M-2-fp8v3's SFT checkpoint (copy v3's .pth / .chk.sft in as andres-350M-2-fp8v3b.chk.sft; no SFT is run here).
               options-tune.json is v3's: v2b's sets and passes + gsm8k x3, metamath_qa (100k cap) x3, numinamath_cot (20k cap) x1.
  DPO:         andres-350M-2-fp8v2e's configuration (switched from v2d's on 2026-10-16: the half dose scored 70.7% vs 66.9% on the factual suite),
               so that v3b vs v2e isolates the SFT base: offsetbias_dpo x1.5, openhermes_misconception_dpo x1, truthfulqa_dpo x1.5,
               truthy_dpo x1.5 over 1 epoch (passes are totals over the run); batch 12 x 3 (token-budgeted), LR 4e-6, beta 0.3,
               dpo_sft_weight 0.2, over-long pairs truncated instead of dropped, eval every 20 updates on 160 pairs, checkpoint every 60
               updates (every other one archived), a sample reply at every evaluation. On v2e this was 304 updates, 21 min.
  Served with "Answer in complete sentences."

WHAT TO EXPECT (from v3 and v2d, both measured 2026-10-16)
  v3 brought: GSM8K 13.1% (v2b 2.5%), extended factual 65.4% (v2b 61.3%), core-wrong 15.9% (lowest), terse factual replies (23 tok).
  v2e's DPO brought, on v2b's weights: extended factual 61.3% -> 70.7% (best of the lineage), added-claim failures 21.4% -> 12.8% (lowest),
  core-wrong 17.5% -> 16.5%, pronoun follow-ups 24 -> 33/45, creative 31 -> 32/50, replies shorter everywhere; costs: TriviaQA -1.8, one-word
  answers 2 -> 6/100, plain-text perplexity up (WikiText 22.6 -> 30.9; cosmetic for a chat model, see v2e's README).
  Success for v3b = v3's math (GSM8K ~13%) and core accuracy with v2e's added-claim rate (~13%), creative >= 30/50, benchmarks within a
  point or two of v3. Watch during the run: the sample reply, "Chosen vs ref" near zero, margin growing with accuracy.

HOW TO EVALUATE (the repo tooling, 2026-10-16)
  python gpttests/benchmark/benchcore.py --model_name andres-350M-2-fp8v3b --weights pth      -> bin/andres-350M-2-fp8v3b/andres_350M_2_fp8v3b_benchmark.json
  python gpttests/data/testcore.py --model_name andres-350M-2-fp8v3b                           -> bin/andres-350M-2-fp8v3b/andres_350M_2_fp8v3b_data.json
  python gpttests/compare_models.py <those two> <v3's two> <v2d's two> --judge_gpu 1 --html report.html

RESULTS (2026-10-17; full report: C:\Development\andres-350M-dataset-recipes.html, section 1.5)
  The run: 304 updates, 20 min (08:54-09:14); final margin train +1.9 / val +1.0 (v2e +3.6 / +2.0), val pair accuracy 79.9% (v2e 78.8%),
  Chosen vs ref -0.07 train / 0.00 val; weights moved 0.210% from v3's (v2e 0.209% from v2b's). Verified: .chk.sft == v3's .pth,
  .pth == .chk.dpo. The training curve overlaps v2e's until the last 60 updates (73% val accuracy at update 60 in both runs).
  THE RECIPE DID NOT TRANSFER. Against its own base andres-350M-2-fp8v3:
    GSM8K zero-shot                               13.1% -> 8.0%    113 problems lost, 45 gained, p = 6e-8 (the reason v3 exists); along the run:
                                                                   12.4% at update 60, 11.1% at 180, 8.0% at 304 - most of the loss comes late, as the margin grows
    TriviaQA                                      17.1  -> 14.8    p = 0.012
    20-turn suite, factual /50                    39    -> 30      the Apollo and Shakespeare threads: "Apollo 11" for the rocket, "made in the
                                                                   United Kingdom", "early 16th century", "founded by Shakespeare" - wrong specifics
                                                                   added, the opposite of the intent; creative 28 -> 27, story 12 -> 10
    extended factual suite /635                   65.4% -> 66.5%   inside the +-1.9 noise
      right answer + rejected added claim         18.9% -> 18.3%   unchanged (v2e cut v2b's from 21.4% to 12.8%)
      core answer wrong                           15.9% -> 15.3%   lowest of the lineage
      pronoun follow-ups /45                      23    -> 26
      average factual reply                       33.5  -> 22.4 tokens (shortest of the lineage; 59 tokens on the head-to-head prompts, v3 87)
    ARC-Challenge 27.2 -> 29.9 (p 0.0003); HellaSwag 39.5 -> 39.0, SciQ 78.5 -> 78.4, LAMBADA 41.6 -> 41.2, Winogrande 52.9 -> 52.6 (all noise)
    plain-text perplexity: WikiText 23.05 -> 33.75, PG-19 33.0 -> 54.9, C4 29.9 -> 38.4 (the same drift v2e showed; see v2e's README)
    loops 2 -> 0, one-word answers 6 -> 5 (of 100)
  Head-to-head (80 pairs): 19-35-26 vs v3 (p 0.37), 18-41-21 vs v2e (math 5-1-2 for v3b, rewrite 1-2-5), 19-43-18 vs v2d, 18-39-23 vs v2b,
    17-41-22 vs andres-350M-2-fp8, 29-29-22 vs andres-350M-1-fp8 (p 0.40; v3 and v2e both beat it clearly).
  Why (the reading that fits the numbers): v3's math SFT had already taught "answer and stop" - its added-claim rate was 18.9%, not v2b's
    21.4% - so the anti-elaboration pairs found less to fix in the factual answers and spent their pressure where v3 still differed most
    from the short chosen answers: the worked, multi-step reply. The pairs reward the short plain answer whether or not the long one was
    needed, and GSM8K needs the long one; in 304 updates the model saw no math at all (the anchor only sees the short chosen answers).
  Verdict: the gains of v3 (math, core accuracy) and v2e (claim-free short answers) do not stack by running one recipe after the other.
    v3 remains the best all-rounder, v2e the best factual chat model; v3b is not better than either and is not the model to serve.
  If the stack is worth another try, it is a data change, not a dose change: add preference pairs that also reward a correct derivation
    over a wrong or truncated one (math preference sets exist on the Hub), or give the DPO anchor math SFT examples so the model keeps
    seeing worked solutions while it learns to drop invented claims.

STATUS
  Trained and evaluated 2026-10-17. Not a success (see RESULTS); kept for the record. Archived checkpoints (3 x 4.2 GB) and the .tmp can go.
  Follow-ups the same day: v3d (math pairs in the mix) failed the same way; a scratch experiment (v3 + 0.3 x v2e's weight delta, no
  training; report section 1.6, not a model) showed the factual behaviour itself is compatible with v3's weights; v3e is the trained
  recipe designed from v3's own weaknesses.
