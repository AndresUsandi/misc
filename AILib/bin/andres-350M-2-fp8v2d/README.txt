andres-350M-2-fp8v2d
====================
DPO experiment on andres-350M-2-fp8v2b, successor of the closed andres-350M-2-fp8v2c experiment: the same model and training setup,
with preference data chosen for the one behaviour we want to change instead of the general-purpose sets.

RECIPE
  Pretraining: andres-350M-2-fp8's checkpoint, unchanged (copy its .chk.trn in as andres-350M-2-fp8v2d.chk.trn).
  SFT:         andres-350M-2-fp8v2b's SFT checkpoint (copy v2b's .pth / .chk.sft in as andres-350M-2-fp8v2d.chk.sft; no SFT is run here).
               options-tune.json holds v2b's recipe so the folder documents the SFT the model carries.
  DPO:         offsetbias_dpo x3 (8,497 pairs), openhermes_misconception_dpo x2 (428), truthfulqa_dpo x3 (817), truthy_dpo x3 (1,016)
               -> ~31,800 pair-passes, ~880 updates at 36 pairs per update, ~50 min.
               batch 12 x 3, 2 epochs, LR 4e-6 (min 4e-7, 10% warm-up), beta 0.3, dpo_sft_weight 0.2 (the SFT term on the chosen answer
               that stops the plain-DPO collapse of v2c's first attempt), eval every 20 updates on 160 pairs, checkpoint every 60 updates
               with every other one archived, a sample reply printed at every evaluation.
  Served with "Answer in complete sentences."

WHY THESE DATASETS
  v2c's two attempts showed that the problem is what the pairs teach, not how many there are. Its sets (Orca pairs, DPO mix, Capybara,
  truthy) contain no short factual questions at all, and their chosen answers are 130-480-token elaborations; the second v2c attempt
  faithfully learned to elaborate (factual replies 28 -> 82 tokens, added-claim failures 21% -> 30%). A survey of ~15 Hugging Face
  preference sets (2026-10-15) found the same bias everywhere judged preference data exists - Tulu 3, OLMo 2 1B mix, HelpSteer3, Nectar,
  Arena, DPO-HelpSteer, UltraFeedback even when paired by its truthfulness rating: the LONGER answer is the chosen one in 56-80% of
  pairs; OpenHermesPreferences' trivia category prefers the answer with added background in 72% of pairs. The sets used here are the ones
  that point the other way:
    offsetbias_dpo              NCSOFT/offsetbias: counter-examples to judge biases; chosen = the plain correct answer, rejected = longer
                                and flawed in 97% of pairs ("There are 1024 gigabytes in one terabyte." beats a 600-token essay)
    openhermes_misconception_dpo short factual questions built on a myth or false premise; chosen/rejected of similar length
    truthfulqa_dpo              TruthfulQA as pairs; short, length-neutral (rules TruthfulQA out as an evaluation for this lineage)
    truthy_dpo                  misconception correction and AI self-awareness; short chosen answers
  The ~11,000 distinct pairs are few, but they are the cleanest signal available without building data.

PURPOSE / WHAT A SUCCESS LOOKS LIKE (extended factual suite, 635 samples, +-2 points)
  v2b: 61.3% judge passes, core answer wrong 17.5%, right-but-added-claim 21.4%, factual replies ~28 tokens on the head-to-head prompts.
  Success = the added-claim share falling toward andres-350M-2-fp8's 14% with core-wrong staying ~17% and replies NOT growing;
  creative staying >= 30/50 (v2b 31); benchmarks within noise of v2b (the v2c attempt-2 config kept them there).
  Watch during the run: the sample reply at every evaluation, "Chosen vs ref" near zero (clearly positive = the SFT term is doing SFT),
  margin growing together with accuracy.

RESULTS (2026-10-16; full report: C:\Development\andres-350M-dataset-recipes.html)
  The run: 574 updates (859 token-budgeted steps per epoch: a batch holds 12 pairs at 1,024 tokens and proportionally more when they are
  shorter, ~18 on average; only 4.6% of OffsetBias was dropped for length), 33 min,
  final val margin +5.6 (train +12.8), val pair accuracy 77%, Chosen vs ref -0.1 train / +0.03 val (the anchor held without doing SFT),
  weights moved 0.28% from v2b's. Served .pth = the DPO checkpoint; .chk.sft verified bit-identical to v2b's.
  SUCCESS on the target behaviour, the first DPO run that moved it:
    extended factual suite, judge passes /635          66.9%   best of all seven models (andres-350M-2-fp8 66.8%, v2b 61.3%, v3 65.4%)
      right answer + rejected added claim              13.9%   lowest of all (v2b 21.4%, andres-350M-2-fp8 14.3%, v3 18.9%)
      core answer wrong                                19.4%   (v2b 17.5%; inside the +-1.6 noise)
      pronoun follow-ups /45                           24      (v2b 24)
      average factual reply                            21 tok  (v2b 34 on the suite; 22 vs 28 on the head-to-head prompts) - tersest in the family
    20-turn suite: factual 32/50 (v2b 24), creative 33/50 (best recorded; v2b 31), six-turn story 16/30 (best recorded; v2b 13), all 65
    creative replies 80 tokens on the suite (v2b 157), 130 on the head-to-head prompts (v2b 147)
  Head-to-head (80 pairs): 17-37-26 vs v2b (p 0.22; the judge prefers v2b's longer worked answers on reasoning 1-6-5 and arithmetic 0-4-4),
    19-40-21 vs andres-350M-2-fp8, 21-36-23 vs v2c, 21-36-23 vs v3, 32-29-19 vs andres-350M-1-fp8 - a dead heat with the family.
  Costs: one-word answers 8/100 (v2b 2); TriviaQA 14.9 (v2b 16.7), LAMBADA 41.3 (42.5), ARC-Easy 56.0 (56.7); GSM8K 2.5 (unchanged);
    SciQ 80.1, HellaSwag 39.4, Winogrande 51.6 unchanged; and a visible language-model drift on plain text: WikiText perplexity 26.5
    (v2b 22.6), PG-19 45.7 (33.0), C4 35.5 (29.7). The model now finds long natural text less likely - the flip side of learning to stop.
    Nothing like v2c's first attempt (perplexity x800); a lighter dose (1 epoch or LR 3e-6) should trim it.

WHAT THIS SETTLES
  The DPO stage is not broken and the anchor is not the problem: with pairs that encode the behaviour (plain correct beats longer flawed)
  and an anchor light enough (0.2) for the preference term to lead, DPO removed a third of the added-claim failures in 33 minutes, without
  touching creative quality. The two v2c attempts failed on data (general-purpose pairs teach elaboration), not on the method.

NEXT
  (2026-10-16, later the same day) andres-350M-2-fp8v2e ran this recipe at half the dose (one epoch, passes halved) and scored 70.7% on the
  factual suite with fewer wrong core answers - the second epoch here was not needed for the gain; see v2e's README (and its note on why
  the perplexity drift is not reduced by the shorter run). v3b uses v2e's dose.
  Run this recipe on andres-350M-2-fp8v3's SFT weights (the better base: same factual-precision target, five times the arithmetic), ideally
  with one epoch or LR 3e-6 to trim the perplexity drift. Scale-up candidate if more signal is wanted: the gated
  vector-institute/Factuality_Alignment set (45k pairs of "response vs the same response with a false claim inserted"; needs an HF login).

STATUS
  Trained and evaluated. The best factual model of the lineage; v3 remains the best all-rounder (math). Recipe ready to port to v3.
