gpt2-355Mv3
===========
gpt2-355Mv2 plus a continued-pretraining stage in front of it: the same GPT-2 355M weights (gpt2-355Mv3.pth) first read ~2.7B tokens of
fact-dense text, then get the exact v2 SFT and DPO recipes, so v2 (SFT only) vs v3 (pretraining + SFT) is an apples-to-apples comparison.

RECIPE
  Pretraining: continued from OpenAI's GPT-2 355M weights (the Training stage loads the .pth when no .trn.chk exists). ~2.7B tokens:
               openwebtext 21% (replay of GPT-2's own data distribution, against forgetting), fineweb_edu 34%, wikipedia 24% (the 150K
               core articles at the head of the dump), wikipedia_simple x3 7%, cosmopedia wikihow/openstax/khan/stanford 14%.
               Peak LR 1e-4 (AdamW) / 1e-3 (Muon): a third of the from-scratch andres runs, 20K micro-step warmup, cosine to 10%,
               weight decay 0.1, 262K tokens per update (4 x 64 x 1024), ~10.5K updates. Single 8 GB GPU: ~5.8 days at 5.5K tok/s.
  SFT:         gpt2-355Mv2.options-tune.json unchanged (smol_smoltalk x2, alpaca_gpt4 x3, no_robots / oasst2 / everyday_conversations x6).
  DPO:         gpt2-355Mv2.options-optimize.json unchanged (ultrafeedback dpo_mix capybara_dpo helpsteer2_pref truthy_dpo).

PURPOSE
  Test whether the factual failures of gpt2-355M (TriviaQA 11.6%, 0/45 on the factual chat turns) come from missing knowledge rather than
  from the fine-tuning, by adding knowledge without losing GPT-2's fluency.
