andres-350M-2-fp8v2c
====================
DPO experiment on andres-350M-2-fp8v2b (formerly named andres-350M-2-fp8v4; renamed 2026-10-14): preference optimization with sets
suited to a small model, aimed at v2b's one weakness - correct factual answers with an invented extra claim attached.

RECIPE
  Pretraining: andres-350M-2-fp8's checkpoint, unchanged.
  SFT:         andres-350M-2-fp8v2b's SFT checkpoint, copied in as this model's .chk.sft (no SFT is run here; verified bit-identical to v2b's .pth).
  DPO:         see the attempts below; the options file holds the configuration of attempt 2, the model in this folder.
  Served with "Answer in complete sentences."

PURPOSE
  Recover andres-350M-2-fp8v2b's factual chat accuracy without losing its creative gains. v2b's core answers are right as often as
  andres-350M-2-fp8's (wrong 17.5% vs 18.9% of 635 samples), but 21.4% of its factual answers add a false claim to a correct answer vs
  14.3% for andres-350M-2-fp8. The target is v2b's creative quality with andres-350M-2-fp8's factual precision (~28-token answers).

ATTEMPT 1 (2026-10-14, plain DPO) - FAILED, discarded
  deita_dpo x2, dpo_mix x2, capybara_dpo x1, truthy_dpo x3; batch 2 x 16, beta 0.1, LR 2e-6, 2 epochs, 1,467 updates, 6 h 54 m.
  Collapsed into 2-4 token answers ("The capital of France") or nothing at all (270 of 685 quality-suite replies empty): extended factual
  12.6%, creative 1/50, TriviaQA 0.0%, WikiText perplexity 22.6 -> 18,450, lost every head-to-head 2-9-69 (vs v2b) to 3-18-59 (vs andres-350M-1-fp8).
  Mechanism: plain DPO only rewards a growing GAP between chosen and rejected, so it is also satisfied by making both answers less likely
  as long as the rejected one falls faster; with per-token-averaged log-probs (the end marker is a large share of a short answer) and sets
  that prefer the shorter answer 64-70% of the time, the cheapest gap is "stop after three words". Margin jumped at update ~170 while pair
  accuracy stayed ~60%; the run's own metrics (val loss 0.301, margin +16.7, 90% pair accuracy) looked excellent throughout.

FIXES MADE AFTER ATTEMPT 1 (in the repo)
  - gpttrain/optimize/dpo_loss.py: loss = DPO + dpo_sft_weight x NLL(chosen answer) (the SFT loss on the preferred answer; the RPO /
    Llama 3 "NLL on chosen" term). Keeps the chosen answers themselves likely, so the gap can only grow by pushing the rejected down.
    --dpo_sft_weight, default 0.5, 0 = plain DPO (documented in ARGUMENTS-TRAIN.md).
  - Log: "Chosen vs ref" column (policy minus reference log-prob of the chosen answers; falling below 0 = the collapse starting) and a
    real sample reply at every evaluation (the sample prompt used to be the first preference entry, 1,335 tokens, longer than the
    context, so it printed nothing).
  - Test harness: an empty reply is a judge FAIL (was a 5/5 pass) and a head-to-head loss (was often a tie).

ATTEMPT 2 (2026-10-15, DPO + 0.5 anchor) - INTACT BUT NO IMPROVEMENT; this is the .pth currently in the folder
  Same sets x1 / x1 / x1 / x3 (pairs over 1,024 tokens dropped: 23,700 pairs), batch 8 x 4, beta 0.3, LR 2e-6, 1 epoch, dpo_sft_weight 0.5,
  742 updates, 39 min. Log: Chosen vs ref +0.08 train / +0.11 val throughout (anchor held), margin +0.07 train / +0.34 val, val acc 87-90%,
  weights moved 0.15% from v2b's.
  Results (full report: C:\Development\andres-350M-dataset-recipes.html):
    benchmarks         all within noise of v2b: SciQ 79.1 (79.9), ARC-Easy 56.4 (56.7), HellaSwag 39.8 (39.8), LAMBADA 43.3 (42.5),
                       TriviaQA 17.2 (16.7), WikiText ppl 23.8 (22.6), PG-19 33.3 (33.0)
    head-to-head       23-34-23 vs v2b, 22-37-21 vs andres-350M-2-fp8, 20-36-24 vs v2, 35-30-15 vs andres-350M-1-fp8 (p 0.007)
    creative (20-turn) 30/50 (v2b 31); six-turn story 11/30 (13)
    extended factual   335/635 = 52.8%   (v2b 61.3%, andres-350M-2-fp8 66.8%)  <- WORSE
      core answer wrong        17.3%  (v2b 17.5%)   unchanged
      right + added claim      30.4%  (v2b 21.4%)   the habit got stronger
      avg factual reply        45.6 tokens (v2b 34.1); on the head-to-head prompts 82 tokens (v2b 28, andres-350M-2-fp8 29)
      pronoun follow-ups       11/45 (v2b 24/45)
  Why: the anchor term imitates the CHOSEN answers of the preference sets, and those are long (median ~480 tokens in capybara_dpo, ~310 in
  dpo_mix, ~130 in deita_dpo, ~70 in truthy_dpo) against ~28 tokens for a v2b factual reply. With the preference signal this small (margin
  +0.07; its pull is ~beta/2 = 0.15 per pair against the anchor's 0.5) the run was in effect a light SFT on long GPT-4-style answers.
  The safety device worked; the dose and the balance were wrong.

WHAT THE PREFERENCE SETS ACTUALLY CONTAIN (sampled 2026-10-15; the reason attempts 1 and 2 could not work)
  Not one pair in capybara_dpo / deita_dpo / dpo_mix / truthy_dpo is "plain correct answer beats correct answer with an invented extra":
  capybara = long multi-turn chats and code, deita = Orca instruction tasks, dpo_mix = essays and task prompts, truthy = misconceptions and
  AI self-awareness. Single short factual questions: 0% / 0% / 12% / 0%. A survey of ~15 Hugging Face preference sets found the same thing
  everywhere: judged preference data (GPT-4, PairRM, crowd workers) rewards elaboration - Tulu 3, OLMo 2 1B mix, HelpSteer3, Nectar, Arena,
  DPO-HelpSteer, UltraFeedback (even when paired by its truthfulness rating) all have the LONGER answer as chosen in 56-80% of pairs, and
  OpenHermesPreferences' trivia category prefers "Memorial Day. Established in the aftermath of the American Civil War..." over "Memorial
  Day." in 72% of pairs. The "hallucination-reduction-dpo-100k" style sets are templated (~3% distinct prompts). What points the right way
  is small: NCSOFT/offsetbias (8.5k pairs, chosen is the plain correct answer and the rejected one is longer and flawed in 97%),
  OpenHermesPreferences 'misconception' (428), TruthfulQA pairs (817), truthy_dpo (1,016).

ATTEMPT 3 -> moved to andres-350M-2-fp8v2d (2026-10-15)
  The next attempt (preference sets that point away from elaboration: OffsetBias, OpenHermes misconceptions, TruthfulQA pairs, truthy-dpo;
  anchor 0.2, beta 0.3, LR 4e-6, 2 epochs, batch 12 x 3) runs as a new experiment, andres-350M-2-fp8v2d. This folder's options file is
  the configuration that produced the .pth here (attempt 2) and stays as the record of a closed experiment.

STATUS
  CLOSED. Two attempts evaluated, neither an improvement over andres-350M-2-fp8v2b, which remains the best model of the lineage.
  andres-350M-2-fp8v2d (2026-10-16) then succeeded with preference sets that encode the behaviour (added-claim failures 21.4% -> 13.9%);
  andres-350M-2-fp8v3 and vNext should take their DPO configuration from there.
