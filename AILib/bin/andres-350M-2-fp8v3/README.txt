andres-350M-2-fp8v3
===================
SFT experiment (DPO to follow): the andres-350M-2-fp8v2b recipe plus reasoning / arithmetic data.

RECIPE
  Pretraining: andres-350M-2-fp8's checkpoint, unchanged (.chk.trn verified bit-identical to andres-350M-2-fp8's).
  SFT:         andres-350M-2-fp8v2b's sets and passes (long-form sets at one pass, smol_smoltalk and the small sets at two) + gsm8k x3,
               metamath_qa (100k cap) x3, numinamath_cot (20k cap) x1 - about 7% of the 1.12B tokens seen. num_epochs 1.
               5,007 updates, 5 h 57 m; final val loss 1.293 (response tokens; v2b 1.326), val-train gap +0.27; weights moved 10.6% from the
               base (v2b 10.2%); v3 is 5.4% from v2b, about as far as v2b is from andres-350M-2-fp8. Served .pth = the SFT checkpoint.
  DPO:         not yet run. Take the configuration from andres-350M-2-fp8v2d (2026-10-16: its recipe - OffsetBias, OpenHermes misconceptions,
               TruthfulQA pairs, truthy; anchor 0.2, beta 0.3, LR 4e-6 - cut v2b's added-claim failures from 21.4% to 13.9% without hurting
               creative quality; a lighter dose, 1 epoch or LR 3e-6, is advised to limit perplexity drift).
  Served with "Answer in complete sentences."

PURPOSE
  Does a small share of step-by-step math improve arithmetic and remove the "formula babble" answers without disturbing anything else?
  (Apples to apples against the other SFT-only models: andres-350M-1-fp8, andres-350M-2-fp8, andres-350M-2-fp8v2, andres-350M-2-fp8v2b.)

RESULTS (2026-10-16; full report: C:\Development\andres-350M-dataset-recipes.html)
  Math: GSM8K test, zero-shot chat, 1,319 problems          13.1%   (v2b 2.5%, andres-350M-2-fp8 2.6%, v2 2.3%, andres-350M-1-fp8 1.6%; p = 1e-26 vs v2b)
        head-to-head arithmetic prompts                        6-2-0 vs andres-350M-1-fp8, 4-3-1 vs andres-350M-2-fp8, 2-3-3 vs v2b (4 simple sums; GSM8K is the real measure)
  Factual chat (the unexpected part): the math data undid most of v2b's factual regression.
        extended factual suite, judge passes /635              65.4%   (v2b 61.3%, andres-350M-2-fp8 66.8%, v2 61.7%, andres-350M-1-fp8 43.0%)
        core answer wrong                                      15.9%   (lowest of all models; v2b 17.5%, andres-350M-2-fp8 18.9%)
        right answer + rejected added claim                    18.9%   (v2b 21.4%, andres-350M-2-fp8 14.3%)
        factual reply length (head-to-head prompts)            23 tok  (v2b 28, andres-350M-2-fp8 29) - the tersest in the family
        20-turn suite, factual half                            39/50   (best ever recorded; andres-350M-2-fp8 36, v2b 24); all 100 samples 67 (best)
        pronoun follow-ups /45                                 23      (v2b 24)
  Creative: 28/50 on the suite (v2b 31, within the +-7 noise), six-turn story 12/30 (v2b 13), but the judge prefers the others' creative
        replies head-to-head: 3-6-7 vs v2b, 1-8-7 vs andres-350M-2-fp8, 1-8-7 vs andres-350M-1-fp8. v3's weakest category. Creative replies
        are longer (196 tokens vs v2b's 147).
  Benchmarks: a point or two below v2b on the knowledge/commonsense rows, statistically detectable: SciQ 78.5 (v2b 79.9, p 0.016),
        LAMBADA 41.6 (42.5, p 0.008), ARC-Challenge 27.2 (28.7, p 0.05), HellaSwag 39.5 (39.8; 40.1 for andres-350M-2-fp8, p 0.002).
        ARC-Easy 56.7, TriviaQA 17.1, Winogrande 52.9 and the perplexities (WikiText 23.1, PG-19 33.0, C4 29.9) are within noise of v2b.
  Head-to-head overall (80 pairs): 20-38-22 vs v2b, 22-36-22 vs andres-350M-2-fp8, 20-40-20 vs v2, 34-27-19 vs andres-350M-1-fp8 (p 0.053).
  Verdict: as an SFT model, v3 is the best balance the lineage has produced - v2b's creative gains (within noise), andres-350M-2-fp8's
        factual precision, five times the arithmetic - at the cost of ~1.5 points on SciQ/LAMBADA and a weaker creative preference.
  Why math data helps factual chat (hypothesis that fits the numbers): MetaMath/GSM8K answers are verifiable and end decisively
        ("The answer is: 540"); 7% of the SFT tokens in that style taught the model to stop when the answer is given - shorter factual
        replies, fewer appended claims. It is the lever the DPO attempts were reaching for, obtained with instruction data.

KNOWN ISSUES
  One-word answers on the 20-turn suite rose from 2 to 6 of 100 (terseness overshooting); creative preference lost head-to-head.
  LAMBADA remains below andres-350M-1-fp8 (41.6 vs 45.3) like every andres-350M-2 model - a pretraining-data matter (andres-350M-2-fp8vNext).

STATUS
  SFT trained and evaluated. The v2e DPO recipe was run on these weights as andres-350M-2-fp8v3b (2026-10-17): it cost GSM8K 13.1 -> 8.0%
  and TriviaQA -2.3 without reducing the added-claim rate (18.9 -> 18.3%); see v3b's README. A second DPO run with math preference pairs
  (v3d) lost the math the same way. A scratch experiment (not a model of the lineage; kept outside bin/, report section 1.6) added
  0.3 x v2e's DPO weight delta to these weights and measured factual 70.9% / GSM8K 13.2%: evidence that the factual behaviour is
  compatible with v3's weights. The trained recipe designed from v3's own weaknesses, andres-350M-2-fp8v3e (2026-10-18), moved what it
  aimed at (creative head-to-head 8-6-2 vs v3, added claims 18.9 -> 13.7%) but raised core-wrong to 20.3% and cost GSM8K 13.1 -> 8.2%:
  on these weights every ~0.2% DPO step so far had cost the math, whatever the data - until andres-350M-2-fp8v3f (2026-10-18): the v3e
  recipe with beta 1.0, the lower half frozen and this model's math SFT data replayed during the DPO kept the math (GSM8K 12.3%, p 0.31)
  and the benchmarks, cut added claims to 15.0%, raised the factual suite to 67.9% and won creative 8-7-1 against these weights. v3f is
  the model to serve from this line; v3 is its base and must be kept.
