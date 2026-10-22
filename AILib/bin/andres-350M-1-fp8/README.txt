andres-350M-1-fp8
=================
Same as andres-350M-1 but trained in fp8 precision; everything else (including datasets) is identical.
Baseline of the dataset-recipe lineage: andres-350M-1-fp8 -> andres-350M-2-fp8 -> andres-350M-2-fp8v2 -> andres-350M-2-fp8v2b -> (v3, v4, v5).
All models in the lineage share the architecture (24 layers, 1024 dim, 16 heads, context 1024, QK-norm, tied embeddings, 354.8M params)
and hyper-parameters; only the training data differs.

RECIPE
  Pretraining: Wikipedia 67%, BookCorpus 22%, TinyStories 7%, WritingPrompts, Cosmopedia-100k, DailyDialog / DialogSum / PersonaChat;
               2 passes over everything (~6.3B unique tokens). 12.7B tokens seen, 54.8 h. Fiction ~37% of tokens seen.
  SFT:         alpaca_gpt4, capybara, deita_10k_sft, no_robots, slim_orca, ultrachat_200k; 2 epochs. 896M tokens, 4,084 updates, 6.0 h.
  DPO:         none. Served without a system prompt.

MEASURED (2026-10-11 .. 2026-10-14; benchmarks on the SFT .pth, lm-eval-harness scoring; chat on the gpttests/data suite with the Gemma 4 judge)
  Benchmarks:  HellaSwag 33.4  ARC-Easy 49.2  ARC-Challenge 24.2  SciQ 71.6  Winogrande 51.0  LAMBADA 45.3  TriviaQA 14.8
  Perplexity:  PG-19 40.3 (neutral text)  C4 36.9  WikiText-103 32.2  LAMBADA 15.5
  Chat:        factual 273/635 judge passes (43.0%; core answer wrong 30%, right-but-added-false-claim 27%); creative 27/50 (mean 3.16);
               six-turn story 9/30; repetition loops 5/100; average reply 129 tokens (the longest in the lineage).

STRENGTHS / WEAKNESSES
  Best novel-style completion of the lineage (LAMBADA 45.3) and full-sentence answers. Weak knowledge, invents facts, rambles
  (explanations average 279 tokens), loops on long outputs. Loses the 40-prompt head-to-head to every andres-350M-2 model (19-25-36 and worse).

STATUS
  Reference point. Checkpoints still use the old .trn.chk / .sft.chk names, which the current resolve_path does not find; rename to
  .chk.trn / .chk.sft before running its benchmark or data tests.
