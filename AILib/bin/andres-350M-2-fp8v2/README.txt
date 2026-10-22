andres-350M-2-fp8v2
===================
SFT data experiment on the andres-350M-2-fp8 pretrained checkpoint (bit-identical .chk.trn). Same SFT hyper-parameters; the mix adds
long-form multi-turn and creative sets.

RECIPE
  Pretraining: andres-350M-2-fp8's checkpoint, unchanged.
  SFT:         andres-350M-2-fp8's sets (smol_smoltalk, everyday_conversations, no_robots, dolly, oasst2) + smoltalk_magpie_ultra (200k cap),
               ultrachat_200k, capybara, opus_writingprompts. 2 epochs with per-set passes: magpie-ultra x2, ultrachat x1, capybara x2, opus x3,
               the rest x2. smol_smoltalk ~46% of tokens seen, long-form sets ~50%. 1.39B tokens, 6,134 updates, 9.4 h; val-train gap +0.24.
  DPO:         none. Served with "Answer in complete sentences."

PURPOSE
  Fix andres-350M-2-fp8's weak multi-turn story coherence and terse style with long-form conversational data, without losing its factual edge.

RESULTS vs andres-350M-2-fp8 (2026-10-12 .. 2026-10-14)
  Benchmarks:  knowledge unchanged (every difference within noise: HellaSwag 40.0, ARC-Easy 56.7, ARC-Challenge 27.9, SciQ 79.2, TriviaQA 16.8);
               LAMBADA 42.0 -> 40.3 (p = 4e-5) and all perplexities +3-12%: the heavier SFT pulled it further from a general language model.
  Chat:        creative 26 -> 30 of 50 (mean 3.26 -> 3.64); six-turn story 6 -> 13 of 30; arithmetic head-to-head 3-0 over andres-350M-2-fp8.
               factual 66.8% -> 61.7% judge passes (424 -> 392 of 635): the core answer is wrong LESS often (18.9% -> 16.4%) but a right answer
               with an added false claim rose from 14.3% to 22.4% (e.g. "born in Stratford-upon-Avon, England, on June 19, 1464" in 5/5 samples).
  Length:      creative replies 80 -> 183 tokens; length words ignored ("two-sentence horror story" -> 28 sentences, "limerick" -> a 20-sentence story).
  Head-to-head: vs andres-350M-2-fp8 18-43-19 (dead heat; andres-350M-2-fp8 takes creative 8-4 on the constraint prompts);
               vs andres-350M-1-fp8 37-26-17 (p = 0.009).

VERDICT
  The long-form data did its job (multi-turn coherence, story shape, worked arithmetic) but taught the model to elaborate, and at 350M
  elaboration means invented specifics. Corrected by andres-350M-2-fp8v2b (same sets, one pass over the long-form ones).

STATUS
  Superseded by andres-350M-2-fp8v2b.
