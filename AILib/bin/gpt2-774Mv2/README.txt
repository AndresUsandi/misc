gpt2-774Mv2
===========
gpt2-774M plus a continued-pretraining stage in front of it: OpenAI's GPT-2 Large weights (gpt2-774Mv2.pth) first read ~5.1B tokens of
fact-dense text, then get the exact gpt2-774M SFT and DPO recipes, so gpt2-774M (SFT only) vs gpt2-774Mv2 (pretraining + SFT) is an
apples-to-apples comparison.

RECIPE
  Pretraining: continued from OpenAI's GPT-2 774M weights (the Training stage loads the .pth when no .trn.chk exists). ~5.1B tokens:
               Wikipedia 40% (finewiki_core x2 = the ~174K articles with page id < 400K, tables kept, infobox facts written under
               the title; finewiki_simple), knowledge as Q&A 11% (wiki_to_rcqa, nemotron_synth_qa: a passage, then questions and
               answers about it), educational web 38% (dclm_edu score 3+, fineweb_edu), cosmopedia_v2 5%, openwebtext 6% (replay of
               GPT-2's own data, against forgetting).
               Peak LR 1e-4 (torchao AdamW8bit, fp8), 10K micro-step warmup (~310 updates), cosine to 10%, weight decay 0.1,
               524K tokens per update (16 x 32 x 1024), ~9.7K updates. RTX 5060 Ti 16 GB: ~9 days at ~6.5K tok/s (the rate of the
               gpt2-774M SFT run: same model, precision, optimizer and batch).
  SFT:         gpt2-774M.options-tune.json unchanged (smol_smoltalk x1, alpaca_gpt4 x2, no_robots / oasst2 x4, everyday_conversations x6).
  DPO:         gpt2-774M.options-optimize.json unchanged (truthy_dpo helpsteer3_pref helpsteer2_pref deita_dpo gutenberg_dpo).

WHY THESE SOURCES
  A fact sticks when it is seen several times in different forms: core facts are read twice in Wikipedia, again in plain words and
  again as questions. Wiki-to-RCQA and Nemotron synthetic QA beat top-quality web text on QA tasks in the Olmo 3 midtraining ablations;
  DCLM-Edu (score 3+) beat FineWeb-Edu and DCLM on MMLU/ARC in the SmolLM2 360M ablation; FineWiki keeps the tables that
  wikimedia/wikipedia drops.

PURPOSE
  Test whether more reading fixes the factual failures of gpt2-774M (TriviaQA 17.8%; Gagarin as the first man on the Moon in ~1 of 4
  samples). Same-harness references: GPT-2 Large 14.0 TriviaQA / 53.2 ARC-Easy / 80.1 SciQ, Qwen3-0.6B-Base 24.5 / 65.4 / 93.5.
  Benchmark the pretraining checkpoint (weights "trn") around 1.5B tokens (~day 3) to confirm the trend before spending the rest.
