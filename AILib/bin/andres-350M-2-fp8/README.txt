andres-350M-2-fp8
=================
Same as andres-350M-2 but trained in fp8 precision; everything else (including datasets) is identical.
Second recipe of the lineage: same architecture and hyper-parameters as andres-350M-1-fp8, new pretraining AND fine-tuning data.
Its pretrained checkpoint (.chk.trn) is the base that andres-350M-2-fp8v2, v2b, v2c and v3 fine-tune from.

RECIPE
  Pretraining: FineWeb-Edu 10BT x1, Wikipedia x3, Simple Wikipedia x4, Cosmopedia v1 stanford / wikihow x3, openstax / khanacademy x4,
               WritingPrompts x4, BookCorpus x1, Cosmopedia stories (1.5M cap) x1 (~20B unique tokens; fiction ~12% of tokens seen).
               28.2B tokens seen, 127.9 h. Loss spikes around 2-3B tokens, recovered.
  SFT:         smol_smoltalk, everyday_conversations, no_robots, dolly, oasst2; 2 epochs. 676M tokens, 3,002 updates, 4.5 h.
  DPO:         none. Served with the system prompt "Answer in complete sentences." (adopted 2026-10-12: removed one-word answers and
               most repetition loops, +4 suite turns, no effect on benchmarks).

PURPOSE
  Test whether an education-heavy pretraining mix (FineWeb-Edu, Cosmopedia textbooks) and the SmolLM2-360M SFT recipe beat the
  Wikipedia/BookCorpus/dialogue recipe of andres-350M-1-fp8.

RESULTS vs andres-350M-1-fp8 (2026-10-11 .. 2026-10-14)
  Benchmarks:  HellaSwag 33.4 -> 40.1  ARC-Easy 49.2 -> 57.5  ARC-Challenge 24.2 -> 28.6  SciQ 71.6 -> 80.5  TriviaQA 14.8 -> 17.5
               (all highly significant, McNemar p <= 0.003); LAMBADA 45.3 -> 42.0 (the only regression); Winogrande unchanged (chance).
               The gap is already present in the pretrained-only checkpoints, so it comes from the pretraining recipe.
  Perplexity:  PG-19 40.3 -> 32.5 (-19%), C4 36.9 -> 29.5 (-20%): a better general language model, not just better at its own data.
  Chat:        factual 43.0% -> 66.8% judge passes (273 -> 424 of 635; core answer wrong 30% -> 19%, added false claims 27% -> 14%);
               creative 27 -> 26 of 50 (draw); six-turn story 9 -> 6 of 30 (slightly worse); loops 5 -> 1 of 100; replies 129 -> 63 tokens.
  Head-to-head (40 prompts x 2 seeds, both A/B orders): 36-25-19 (p = 0.03), decided by explanations / how-to (13-3-0).
  Caveat:      the new base also saw 2.2x the pretraining tokens (28.2B vs 12.7B), so "better data" and "more data" are not separated here;
               andres-350M-2-fp8v5 keeps a checkpoint at the matching budget to settle it.

KNOWN ISSUES
  Novel-style completion below andres-350M-1-fp8 (fiction share 37% -> 12%); weak multi-turn storytelling (0/5 on the story-continuation
  turns); adds a date to "who wrote Romeo and Juliet" (1605 / 1607) in 4 of 5 samples.

STATUS
  Most accurate factual chat model of the lineage (66.8%). Superseded as the creative/multi-turn model by andres-350M-2-fp8v2b.
