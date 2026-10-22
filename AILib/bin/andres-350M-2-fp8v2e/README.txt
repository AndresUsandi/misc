andres-350M-2-fp8v2e
====================
andres-350M-2-fp8v2d's DPO recipe at half the dose: one epoch, each pair seen at most 1.5 times (v2d: two epochs, 3 times), on the same
andres-350M-2-fp8v2b SFT weights. The question it answers: how much of v2d's gain survives when the pass that mostly memorised is removed,
and how much of its perplexity drift goes with it.

RECIPE
  Pretraining: andres-350M-2-fp8's checkpoint, unchanged (copy v2d's .chk.trn in as andres-350M-2-fp8v2e.chk.trn).
  SFT:         andres-350M-2-fp8v2b's SFT checkpoint (copy v2d's .chk.sft in as andres-350M-2-fp8v2e.chk.sft; verified bit-identical to v2b's .pth).
  DPO:         offsetbias_dpo x1.5, openhermes_misconception_dpo x1, truthfulqa_dpo x1.5, truthy_dpo x1.5 (passes are totals over the run;
               v2d had x3 / x2 / x3 / x3 over 2 epochs, i.e. the same per-epoch mix) -> ~15,800 pair-passes, ~290 updates, ~17 min.
               Everything else as v2d: batch 12 x 3 (token-budgeted: 12 pairs' worth of 1,024-token sequences per micro-step, ~18 pairs on
               average), LR 4e-6 (cosine to 4e-7, 10% warm-up), beta 0.3, dpo_sft_weight 0.2, eval every 20 updates on 160 pairs,
               checkpoint every 60 updates (every other one archived), a sample reply at every evaluation.
               New: dpo_truncate_long_pairs true - pairs whose answer runs past the 1,024-token context are kept with the answer cut (prompt +
               head of the answer, end marker restored) instead of dropped. On this data it recovers 335 OffsetBias pairs (4% - a small effect;
               the model's context window caps max_length, so a larger window is not an option).
  Served with "Answer in complete sentences."

WHY ONE VARIABLE
  v2d's log: training pair accuracy 96% against 77% on validation, the margin three times larger on training pairs - the second pass over the
  same ~10k pairs was memorisation, and the plain-text perplexity rose 15-40% (WikiText 22.6 -> 26.5, PG-19 33 -> 46). Halving the dose by
  removing that pass is the cleanest test. If the drift persists at this dose, the next knob is the learning rate (3e-6); if the gain
  shrinks too much, v2d's dose was right and the drift is the price.

WHAT TO MEASURE (against v2d and v2b; extended factual suite, 635 samples, +-2 points)
  v2b: 61.3% judge passes, added-claim 21.4%, core-wrong 17.5%, creative 31/50, WikiText perplexity 22.6, TriviaQA 16.7, LAMBADA 42.5.
  v2d: 66.9%, added-claim 13.9%, core-wrong 19.4%, creative 33/50, WikiText 26.5, TriviaQA 14.9, LAMBADA 41.3, one-word answers 8/100.
  Success = most of v2d's added-claim improvement (<= ~16%) with perplexity, TriviaQA and LAMBADA closer to v2b's.
  python gpttests/benchmark/test_andres_350M_2_fp8v2e.py --device cuda:0 ; python gpttests/data/test_andres_350M_2_fp8v2e.py --judge_gpu 1 --single_gpu true --gpu_index 1
  python gpttests/compare_models.py <v2b, v2d, v2e benchmark+data files> --reference andres-350M-2-fp8v2d --judge_gpu 1 --html report.html

RESULTS (2026-10-16; full report: C:\Development\andres-350M-dataset-recipes.html)
  The run: 304 updates (910 token-budgeted steps), 21 min; final margin train +3.6 / val +2.0 (v2d +12.8 / +5.6), val pair accuracy 79%,
  Chosen vs ref -0.16 train / -0.03 val; weights moved 0.21% from v2b's (v2d 0.28%). Served .pth = the DPO checkpoint.
  THE BEST FACTUAL CHAT MODEL OF THE LINEAGE:
    extended factual suite, judge passes /635          70.7%   (v2d 66.9%, andres-350M-2-fp8 66.8%, v3 65.4%, v2b 61.3%)
      right answer + rejected added claim              12.8%   lowest of all (v2d 13.9%, v2b 21.4%)
      core answer wrong                                16.5%   (v2d 19.4%, v2b 17.5%) - back at the SFT level
      pronoun follow-ups /45                           33      best ever (v2d 24, v2b 24, andres-350M-2-fp8 26)
      average factual reply                            19 tok  (v2d 21, v2b 34)
    20-turn suite: factual 32/50, creative 32/50 (v2d 33, v2b 31), six-turn story 14/30, all 64, loops 0, one-word answers 6/100 (v2d 8)
  Head-to-head (80 pairs): 16-46-18 vs v2d, 16-41-23 vs v2b (p 0.34; arithmetic 0-4-4, the judge prefers v2b's worked answers), 21-37-22 vs v3
    (creative 8-5-3 for v2e), 18-41-21 vs andres-350M-2-fp8, 33-29-18 vs andres-350M-1-fp8 (p 0.049).
  Benchmarks: within noise of v2b everywhere except TriviaQA 14.9 (v2b 16.7, p 0.036); LAMBADA 43.1 fully recovered (v2d 41.3, p 5e-8),
    SciQ 80.7, ARC-Easy 56.1, HellaSwag 39.4, GSM8K 1.9 (noise).
  The surprise: the half dose did NOT reduce the plain-text perplexity drift, it increased it: WikiText 30.9 (v2d 26.5, v2b 22.6), PG-19 51.8
    (v2d 45.7), C4 37.5. Inside the run the drift grows steadily (WikiText 24.1 at update 60, 27.4 at 180, 30.9 at 304), and v2d - whose
    first epoch is exactly this run - ended LOWER after its second epoch. So the second pass was not the damage: once the preference loss
    saturates, the anchor term (SFT on the short chosen answers) is what keeps pulling, and it drags the language model back toward fluent
    text (v2d's Chosen vs ref rose from -0.26 to -0.10 during that epoch). The drift is the price of the preference step itself, paid early;
    it does not touch the chat measurements or the knowledge benchmarks, so for a chat model it is cosmetic. A longer low-LR tail or a
    slightly heavier anchor would repay some of it if it ever matters.
  Verdict: one pass is enough for the preference gain, and better for accuracy; the second pass only buys a little fluency repair.
    andres-350M-2-fp8v3b ran this exact dose on v3's SFT weights on 2026-10-17 and it did not transfer (added claims unchanged, GSM8K
    13.1 -> 8.0%); see v3b's README. The 'cosmetic' call on the perplexity drift was measured on 2026-10-17: 67-78% of the extra loss
    is on ordinary mid-sentence words, not at sentence boundaries and not on numbers or names; the model's next-token entropy fell 20%
    while its loss rose (more opinionated); on the factual suite it gives the identical answer across the 5 seeds for 27% of questions
    (v2b 11%) with creative variety unchanged. It is a real cost only for predicting someone else's text or for calibrated probabilities.

STATUS
  Trained and evaluated. Best factual chat model of the lineage; v3 remains the best all-rounder (math). The recipe did not transfer to v3
  by training (v3b, v3d). A scratch weight-transplant experiment (2026-10-17, report section 1.6; not a model) showed this model's DPO
  delta carries its factual behaviour onto v3's weights, which is why v3e was designed from v3's own weaknesses instead.
