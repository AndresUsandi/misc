andres-350M-2-fp8v2b
====================
Correction of andres-350M-2-fp8v2: the same sets on the same andres-350M-2-fp8 pretrained checkpoint, but the long-form sets get a single pass.

RECIPE
  Pretraining: andres-350M-2-fp8's checkpoint, unchanged.
  SFT:         the andres-350M-2-fp8v2 sets; num_epochs 1 with per-set passes: smol_smoltalk and the small sets x2, smoltalk_magpie_ultra x1,
               ultrachat_200k x0.5 (a random half), capybara x2, opus_writingprompts x2. smol_smoltalk ~62% of tokens seen, long-form ~33%.
               1.04B tokens, 4,633 updates, 7.2 h; val-train gap +0.25.
  DPO:         none. Served with "Answer in complete sentences."

PURPOSE
  Keep andres-350M-2-fp8v2's multi-turn and creative gains while removing its side effects (elaboration, invented details, ignored length words).

RESULTS vs andres-350M-2-fp8v2 (2026-10-14)
  Benchmarks:  LAMBADA 40.3 -> 42.5 (p = 1e-10; back at andres-350M-2-fp8's 42.0); all perplexities back within 1-3% of andres-350M-2-fp8;
               knowledge unchanged (HellaSwag 39.8, ARC-Easy 56.7, ARC-Challenge 28.7, SciQ 79.9, TriviaQA 16.7). Statistically identical to
               andres-350M-2-fp8 on every benchmark.
  Chat:        creative 30 -> 31 of 50 (mean 3.64 -> 3.86, best of the lineage); six-turn story 13/30 (same); loops 1/100.
               factual 61.7% -> 61.3% (392 -> 389 of 635): unchanged. Core answer wrong 17.5% (andres-350M-2-fp8: 18.9%); right-but-added-false-
               claim 21.4% (andres-350M-2-fp8: 14.3%) - that 7-point habit is the whole remaining factual gap. Pronoun follow-ups 44% -> 53%.
  Length:      creative replies 183 -> 147 tokens (andres-350M-1-fp8: 149, andres-350M-2-fp8: 80); constraint prompts fixed ("two-sentence
               horror story" 28 -> 3 sentences, "limerick" 20 sentences -> 4 lines).
  Head-to-head: vs andres-350M-2-fp8v2 15-48-17 (tie; wins the constraint prompts 6-3), vs andres-350M-2-fp8 19-43-18 (tie),
               vs andres-350M-1-fp8 37-24-19 (p = 0.022; explanations 13-1-2, arithmetic 7-0-1; creative 3-6-7 and factual 6-7-7 are draws).

STANDING IN THE LINEAGE
  Best creative writer; equal to andres-350M-2-fp8 on every benchmark; 5.5 points behind it on factual chat (61.3% vs 66.8%), entirely from
  added false claims rather than wrong answers; the only measurement still behind andres-350M-1-fp8 is LAMBADA (42.5 vs 45.3).
  Weight-averaging with andres-350M-2-fp8 (50/50) gives 29 factual / 30 creative on the 50-sample suite - a tunable stop-gap.

STATUS
  Current base and still the best model of the lineage: DPO on its SFT checkpoint: andres-350M-2-fp8v2c (closed, two failed attempts) and andres-350M-2-fp8v2d (2026-10-16: added-claim failures 21.4% -> 13.9%, the best factual model of the lineage; see its README); andres-350M-2-fp8v3 uses its SFT recipe plus math data.
