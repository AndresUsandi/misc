andres-350M-r1  -  the first RELEASE of the andres-350M (medium) family
========================================================================
Naming convention (2026-10-19): andres-[size]-[number] are the test families (andres-350M-1, andres-350M-2 and their v-variants);
andres-[size]-r[number] are the releases. r1 is the lineage's best measured recipe, run end to end from pretraining with nothing else
changed, so that the result can be compared with the test model it reproduces (andres-350M-2-fp8v3f).

THE RECIPE (every file in this folder is byte-for-byte andres-350M-2-fp8v3f's; verified 2026-10-19)
  pretraining   = andres-350M-2-fp8's      options-train.json (2 epochs, per-dataset passes: FineWeb-Edu x1, Wikipedia x3, Simple Wikipedia x4,
                                           Cosmopedia stanford/wikihow x3, openstax/khanacademy x4, WritingPrompts x4, BookCorpus x1, Cosmopedia
                                           stories x1 (1.5M cap); batch 16 x 16, LR 3e-4, FP8). ~20B unique tokens, ~32B seen; took 127.9 h.
  fine-tuning   = andres-350M-2-fp8v3's    options-tune.json (1 epoch: smol-smoltalk, dolly, everyday conversations, No Robots, OpenAssistant 2,
                                           Capybara, Opus WritingPrompts x2; magpie-ultra x1 (200k cap); UltraChat x0.5; gsm8k x3, MetaMathQA x3
                                           (100k cap), NuminaMath-CoT x1 (20k cap); LR 6e-5). 1.12B tokens, 5,007 updates; took 6.0 h.
  DPO           = andres-350M-2-fp8v3f's   options-optimize.json (Tulu 3 instruction-following pairs x1, CoEdIT grammar pairs x1, MetaMath
                                           correctness pairs x1, truthy x1, OpenHermes misconception x1; beta 1.0, LR 2e-6, dpo_sft_weight 0.2,
                                           dpo_freeze_below_layer 12, dpo_replay_datasets gsm8k metamath_qa numinamath_cot at weight 1.0,
                                           4 sequences per micro-step; archives every 40 updates). 273 updates; took 18 min.
  model-params.json and options-infer.json are the family's (354.8M parameters, 24 layers, context 1,024; "Answer in complete sentences.").
  download_datasets.py downloads all three stages' data with the same caps (the preference and math-tuning sets are small; the pretraining
  sets are tens of GB).

HOW TO RUN (in this order; each stage resumes from the previous one's checkpoint)
  python bin/andres-350M-r1/download_datasets.py
  python train.py --model_name andres-350M-r1 --training_process Training
  python train.py --model_name andres-350M-r1 --training_process Fine-Tuning
  python train.py --model_name andres-350M-r1 --training_process Optimizing
  Then the standard evaluation: python gpttests/benchmark/test_andres_350M_r1.py and python gpttests/data/test_andres_350M_r1.py
  (or C:\development\temp\run_all.cmd, which now includes r1), and gpttests/compare_models.py against andres-350M-2-fp8v3f.

WHAT TO EXPECT, AND WHAT WOULD BE A SIGNAL
  Reference numbers (andres-350M-2-fp8v3f, 2026-10-18): GSM8K 12.3%, extended factual suite 67.9% (added claims 15.0%, core-wrong 17.2%),
  20-turn creative 30/50, HellaSwag 39.6, ARC-Easy 56.9, SciQ 79.4, LAMBADA 42.0, TriviaQA 16.4, WikiText perplexity 22.95, PG-19 33.1;
  v3 (the SFT stage): GSM8K 13.1%, factual 65.4%, WikiText 23.05; andres-350M-2-fp8 (the pretrained stage, .chk.trn): see its README.
  Seed-level noise: the data order is seeded per epoch and replays identically, so the remaining nondeterminism is GPU arithmetic
  (bf16/FP8 reductions, torch.compile autotuning) compounding over 128 hours of pretraining. Expect benchmark differences of a few tenths
  of a point and chat-suite differences inside the +-1.9 / +-7 noise bands, with the 20-turn multi-turn threads (Apollo, Shakespeare) the
  most volatile items.
  Beyond that, three things could move the result and would deserve a look: (1) the training code has changed since andres-350M-2-fp8
  was pretrained (FP8 and test fixes, the DPO freeze / replay additions, which default off outside r1's DPO stage) - a pretraining-stage
  difference would show in .chk.trn's perplexities against andres-350M-2-fp8's; (2) the Hub sources are not pinned to revisions (the
  Wikipedia dumps are dated configs, FineWeb-Edu is a fixed sample, but any upstream edit to a dataset would change the data) - a
  dataset-size line in the download log that differs from andres-350M-2-fp8's is the tell; (3) the SFT stage's token count (1.12B) and the
  DPO's update count (273) should reproduce exactly; if they do not, the data differs.
  Compare stage by stage, not only at the end: .chk.trn vs andres-350M-2-fp8's .chk.trn (benchmarks), .chk.sft vs v3's .pth, .pth vs v3f's.

STATUS
  Folder created 2026-10-19 (configs, download script, test files). Nothing downloaded or trained yet.
