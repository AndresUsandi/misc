andres-350M-4-fp8  -  the pretraining-budget experiment: a new, larger pretraining under the lineage's best SFT and DPO
=======================================================================================================================
Formerly named andres-350M-2-fp8vNext (and before that planned as "v5"). The purpose is unchanged: a whole new pretraining run, with the
SFT and DPO stages fixed to the best known recipes, so that its result against the release andres-350M-r1 measures the pretraining alone.
2026-10-19: the SFT and DPO were brought up to andres-350M-r1's (= andres-350M-2-fp8v3's SFT and andres-350M-2-fp8v3f's DPO); they had
been the older v2b SFT and v2c DPO. The pretraining recipe is untouched.

PRETRAINING (unchanged; options-train.json, same hyper-parameters as andres-350M-2-fp8: FP8, batch 16 x 16, LR 3e-4, 2 epochs)
  ~47B tokens seen (andres-350M-2-fp8: ~32B seen, ~20B unique). Knowledge ~37B: FineWeb-Edu 100BT sample capped at 19.5M documents x1
  (~20B fresh tokens, replacing the 10B sample), Wikipedia x2, Simple Wikipedia x4, Cosmopedia v2 capped at 7M documents x1 (~5B),
  Cosmopedia v1 stanford x2, wikihow x3, openstax x4, khanacademy x4. Fiction ~10B (21% of what is seen, was 12%): BookCorpus x2,
  clean Project Gutenberg x1, Cosmopedia stories capped at 3M x1, WritingPrompts x4.
  checkpoint_keep_n 300 keeps an archived checkpoint every ~12.3B tokens (three in total, ~13 GB); the first one sits near
  andres-350M-1-fp8's budget (12.7B) and answers how much of andres-350M-2-fp8's gain over andres-350M-1-fp8 was data and how much tokens.
  Expect ~8-9 days on the 2x RTX 5070 Ti and ~140 GB of text on disk.

FINE-TUNING (options-tune.json = andres-350M-r1's = andres-350M-2-fp8v3's)
  smol-smoltalk, Dolly, everyday conversations, No Robots, OpenAssistant 2, Capybara, Opus WritingPrompts x2; SmolTalk magpie-ultra x1
  (200k cap); UltraChat x0.5; gsm8k x3, MetaMathQA x3 (100k cap), NuminaMath-CoT x1 (20k cap); 1 epoch, LR 6e-5. On the andres-350M-2-fp8
  base this recipe (v3) gave GSM8K 13.1% (v2b 2.5%), extended factual 65.4% (v2b 61.3%), core-wrong 15.9% (lowest), at a cost of ~1.5
  points on SciQ / LAMBADA and the creative head-to-head.

DPO (options-optimize.json = andres-350M-r1's = andres-350M-2-fp8v3f's)
  Tulu 3 instruction-following pairs x1 (9,598; answers over ~400 tokens dropped), CoEdIT grammar pairs x1 (6,000), MetaMath correctness
  pairs x1 (4,000), truthy x1, OpenHermes misconception x1; beta 1.0, LR 2e-6, dpo_sft_weight 0.2, dpo_freeze_below_layer 12 (embeddings
  and blocks 0-11 frozen), dpo_replay_datasets gsm8k metamath_qa numinamath_cot (the SFT sets above, replayed with the SFT loss at full
  weight, 4 sequences per micro-step), archives every 40 updates. On v3 this was the only DPO of five that kept the math (12.3% vs 13.1,
  p 0.31) and the benchmarks while cutting added claims 18.9 -> 15.0%, raising the factual suite 65.4 -> 67.9% and winning the creative
  head-to-head 8-7-1 against its base; the unconstrained variants cost ~40% of GSM8K whatever their data.
  Why start here rather than with the v2e recipe (the best factual chat model, 70.7%): v2e's recipe is unconstrained and OffsetBias-heavy
  and cost the math on every base that had any; this base will have math from the SFT. If the new pretraining turns out less fragile
  (GSM8K on the DPO archives flat), the leash can be loosened: LR 4e-6 first, then blocks 8-11 trainable.

COMPARISONS
  andres-350M-4-fp8 vs andres-350M-r1: only the pretraining differs (same SFT, same DPO) - the difference is the new base.
  .chk.trn vs andres-350M-2-fp8's .chk.trn (and the first archive vs andres-350M-1-fp8's budget): the pretraining effect before any tuning.
  .chk.sft vs andres-350M-r1's .chk.sft (and v3's .pth): the base's effect on the SFT.
  Note: Gutenberg is now training data, so PG-19 is no longer a neutral perplexity text for this model; use C4.
  Served with "Answer in complete sentences." (options-infer.json, as the family).

STATUS
  Configured; the old andres-350M-2-fp8v5.* weight files have been removed. Not yet downloaded or trained. download_datasets.py now writes
  under this folder's name (it still said andres-350M-2-fp8vNext until 2026-10-19).
