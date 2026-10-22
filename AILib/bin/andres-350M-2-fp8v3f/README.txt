andres-350M-2-fp8v3f  -  the v3e DPO recipe on v3's SFT weights, with three mechanisms that keep the DPO from breaking v3's brittle skills
===================================================================================================================================
Created 2026-10-18 after four DPO runs on v3 (v3b, v3d, v3e, and a scratch transplant of v2e's weight delta) all cost ~40% of GSM8K
with weight moves of ~0.2%, in four different directions, and v3e's archives showed brittle facts flipping ("the capital of Egypt is
Thebes" 5/5) after 40 updates and 0.07% of movement. The data lessons of v3e are kept (its ingredients did what they were chosen for);
what changes is HOW the weights are allowed to move.

THE THREE MECHANISMS (all new code paths default to off; nothing else in the repo changes behaviour)
  1. beta 1.0 (was 0.3)       DPO's built-in leash to the reference model: the optimum sits closer to the reference for the same
                              preference signal, and pairs saturate at a smaller log-ratio change.                      options-optimize.json
  2. freeze the lower half    --dpo_freeze_below_layer 12: the token / position embeddings (and the tied output head) and transformer
                              blocks 0-11 stay at their SFT values; blocks 12-23 and the final norm train. Fact retrieval and arithmetic
                              are thought to live in the lower / middle layers; style, format and "when to stop" in the upper ones.
                              Implemented in gpttrain/optimizer.py (freeze_lower_layers), called from train.py before the optimizer is
                              built; the data-parallel compute copies mirror the flags. On the tiny test model, 4 of 8 blocks frozen: the
                              frozen tensors were bit-identical after the DPO, the trainable ones moved.
  3. replay v3's math SFT     --dpo_replay_datasets gsm8k metamath_qa numinamath_cot, --dpo_replay_weight 1.0, --dpo_replay_batch_size 4:
     data during the DPO      in every micro-step, 4 sequences of v3's own math fine-tuning data (the same sets and caps v3's SFT used,
                              downloaded under data/Tuning) are scored with the ordinary SFT loss at full weight and their gradients
                              join the preference gradients. The textbook anti-forgetting remedy, aimed at exactly what breaks; the 0.2 x
                              NLL anchor on the chosen answers only protects what the pairs contain. Implemented in train.py (the replay
                              loader) and gpttrain/optimize/optimizing.py (next_replay_batch, the loss, the "[Replay]" telemetry line).
  Plus half the learning rate (2e-6, min 2e-7): with Adam the step size is the learning rate, not the gradient, so beta alone does not
  shrink the move; half the step on half the parameters aims at a total move near the 0.06-0.1% the transplant sweep showed to be safe.

THE DATA (v3e's, minus TruthfulQA; passes in options-optimize.json)
  tulu_if_dpo x1 (9,598 Tulu 3 instruction-following pairs; brief-following), coedit_gec_dpo x1 (6,000 grammar-correction pairs; editing),
  metamath_dpo x1 (4,000 correctness-only math pairs), truthy_dpo x1 (1,016), openhermes_misconception_dpo x1 (428).
  TruthfulQA pairs are out: at x2 in v3e they taught "I have no comment" and "the exact date is not known" on ordinary questions (13 such
  replies in the suite; 0 in v3); truthy and misconception go from x2 to x1 for the same reason.
  ~21,000 pair-passes, ~6.5M preference tokens plus ~1,200 replayed math sequences per 300 updates; expected ~270 updates / ~20 min.

WEIGHTS: .chk.trn and .chk.sft copied from andres-350M-2-fp8v3e (= v3's, verified bit-identical there).   Launch: python train.py --model_name andres-350M-2-fp8v3f --training_process Optimizing

SUCCESS = v3's math kept (GSM8K within ~2 points of 13.1%) and core-wrong not above v3's 15.9%, with the v3e gains: creative head-to-head
  vs v3 won (v3e 8-6-2), creative replies well under v3's 212 tokens, added claims under 18.9% (v3e 13.7%), rewrite pairs won.
  Watch during the run: "[Replay] SFT loss" (should stay flat or fall; a rise means the DPO is fighting the math), "Chosen vs ref" near
  zero, the sample reply, and the archives every 40 updates (GSM8K on each, as for v3e).
  Failure modes to recognise: math kept but no chat movement (the leash is too tight: raise the LR to 4e-6 or unfreeze blocks 8-11);
  math lost anyway (the damage is not in the lower layers: freeze more, or the DPO on v3 is not worth its cost and v2e / v3 stay the
  two specialists).

RELATED
  v3e: the same data at beta 0.3 / LR 4e-6 / all layers / no replay: creative 8-6-2 vs v3, added claims 13.7%, but core-wrong 20.3% and
  GSM8K 8.2%. The scratch transplant (report section 1.6): v3 + 0.3 x v2e's delta kept the math at a 0.06% move.

RESULTS (2026-10-18, 07:40-08:02; full report: C:\Development\andres-350M-dataset-recipes.html, section 1.8)
  The run: 273 updates (818 steps), 6.7M preference tokens, 18 min; 57% of the parameters frozen (203.7M of 354.8M); final margin train
  +0.09 / val +0.06 (beta 1.0: a tiny log-ratio change), val pair accuracy 78%, Chosen vs ref +0.04 / +0.03; the replayed math SFT loss
  stayed between 0.46 and 0.51 from the first interval to the last (the DPO never fought the math). Weights moved 0.066% from v3's
  (v3e 0.235%), all of it in the upper half (0.098% of that half's norm; the frozen half is bit-identical); direction 35% aligned with v3e's.
  THE FIRST DPO ON V3 THAT IMPROVES IT WITHOUT TAKING ANYTHING AWAY. Against andres-350M-2-fp8v3:
   kept    GSM8K 13.1 -> 12.3%  (p 0.31; v3b / v3d / v3e: 8.0 / 7.4 / 8.2); along the run 12.6 / 13.3 / 12.9 / 12.3% at updates 40 / 120 / 200 / 273
           (v3e: 10.6 / 11.5 / 8.9 / 7.6)      TriviaQA 17.1 -> 16.4 (p 0.3)
           WikiText 23.05 -> 22.95, PG-19 33.0 -> 33.1, C4 29.9 -> 29.9 (no drift at all)      hedging replies 0 -> 0 (v3e 13)
           LAMBADA 41.6 -> 42.0 (p 0.03), SciQ 78.5 -> 79.4 (p 0.035), ARC-Challenge 27.2 -> 28.0 (p 0.035), HellaSwag 39.5 -> 39.6, ARC-E 56.7 -> 56.9
   gained  extended factual suite 65.4% -> 67.9% (single-turn questions 65.4 -> 69.8%; paired McNemar p 0.13)
           right answer + rejected added claim 18.9% -> 15.0%      pronoun follow-ups 23 -> 24/45      factual replies 33.5 -> 23.2 tokens
           creative head-to-head vs v3 8-7-1 (sign test p 0.04; v3 had lost creative 25-56 against the field); creative replies 212 -> 165 tokens
           rewrite head-to-head vs v3 1-7-0; repetition loops 2 -> 0; 20-turn creative 28 -> 30 (the "one paragraph, busy morning market" turn 2 -> 5)
   costs   core answer wrong 15.9% -> 17.2% (inside noise)      one-word answers 6 -> 8 (of 100; "Italy")
           20-turn factual 39 -> 30: the Apollo thread ("the rocket" -> "the Apollo 11 rocket" 5/5; "in what country was the rocket made" 5 -> 2)
           - every DPO on v3 so far, constrained or not, flips this fact; the rest of the 20 turns are equal or better.
  Head-to-head (80 pairs): 14-56-10 vs v3 (math 0-8-0, rewrite 1-7-0, creative 8-7-1, explain 2-10-4), 22-43-15 vs v2e (explain 8-6-2, math
    4-2-2), 21-42-17 vs v3e (explain 10-3-3), 19-41-20 vs v2b, 35-28-17 over andres-350M-1-fp8 (p 0.018); replies 54 tokens on average.
  Verdict: andres-350M-2-fp8v3f replaces v3 as the best trained all-rounder of the lineage; andres-350M-2-fp8v2e remains the best factual
    chat model (70.7% / 12.8% added claims, no math). The gain is smaller than v3e's on the targeted behaviours because the leash is tight;
    v3e's extra three-quarters of weight movement bought nothing that survived its costs.
  If more is wanted, in this order: LR back to 4e-6 (the replay and the freeze did the protecting; the LR halving may be redundant), then
    unfreeze blocks 8-11; keep the archives every 40 updates and the Apollo thread as tripwires.

STATUS
  Trained and evaluated 2026-10-18. The model to serve from the v3 line. The four archives (4 x 4.2 GB) and the .tmp can go; .chk.trn /
  .chk.sft are copies of v3's.
