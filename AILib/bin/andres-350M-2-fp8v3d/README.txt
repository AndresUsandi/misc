andres-350M-2-fp8v3d  -  andres-350M-2-fp8v3's SFT weights + the v2e DPO recipe WITH math preference pairs in the mix
=====================================================================================================================
Created 2026-10-17 after andres-350M-2-fp8v3b (the v2e recipe on v3's weights) failed: it cost GSM8K 13.1 -> 8.0% and TriviaQA -2.3
without reducing the added-claim rate (18.9 -> 18.3%), and its "added claims" turned out to be a new kind - calculation-shaped fragments
appended to factual answers ("60/60 = 2.5 hours in an hour") - while GSM8K derivations went wrong. Reading: the anti-elaboration pairs
reward the short plain answer whether or not the long one was needed, and in 304 updates the model saw no math at all, so the "show the
working" habit from v3's math SFT was neither kept nor removed but scrambled. See v3b's README and the report, section 1.5.

WHAT CHANGES (one variable against v3b): the preference data
  v3b's four anti-elaboration sets, same passes (offsetbias x1.5, OpenHermes misconception x1, TruthfulQA pairs x1.5, truthy x1.5)
  + metamath_dpo x1: 8,000 pairs from abacusai/MetaMath_DPO_FewShot (new registry entry; python download_dataset.py --model_name
    andres-350M-2-fp8v3d --purpose optimize --dataset metamath_dpo --limit 8000). Each pair is a MetaMath word problem with the correct
    worked solution as chosen and the SAME solution with one corrupted number as rejected: identical length, identical style to v3's SFT
    math data ("The answer is: N"), so the preference is about arithmetic correctness and nothing else, and the SFT anchor (0.2 x the
    loss on the chosen answer) replays ~8k correct derivations during the run. The few-shot examples of the source prompt are stripped;
    the target question is the user turn.
  Roughly a third of the pair-passes are now math (8k of ~24k), so the model keeps seeing "a derivation belongs here and must be right"
  while the other two thirds keep teaching "no invented extras on a factual question".
  Everything else is v3b's: 1 epoch, LR 4e-6 (min 4e-7, 10% warm-up), beta 0.3, dpo_sft_weight 0.2, batch 12 x 3 (token-budgeted),
  over-long pairs truncated, eval every 20 updates on 160 pairs, checkpoint every 60 updates (every other one archived), compile, FP8.
  Expected ~430 updates (~28 min) instead of 304.

WEIGHTS TO COPY BEFORE LAUNCH (same as for v3b)
  bin/andres-350M-2-fp8v3/andres-350M-2-fp8v3.chk.trn  -> bin/andres-350M-2-fp8v3d/andres-350M-2-fp8v3d.chk.trn
  bin/andres-350M-2-fp8v3/andres-350M-2-fp8v3.pth      -> bin/andres-350M-2-fp8v3d/andres-350M-2-fp8v3d.chk.sft
  (v3b's .chk.sft is bit-identical to v3's .pth, so copying v3b's .chk.trn / .chk.sft works too.)
  Then: python optimize.py --model_name andres-350M-2-fp8v3d

SUCCESS = v3's math kept (GSM8K within ~2 points of 13.1%) with the factual gains v2e got on v2b (added claims well under 18.9%,
  extended factual above 65.4%), creative >= 28/50, no calculation fragments in factual answers. Watch during the run: the sample reply,
  "Chosen vs ref" near zero, validation pair accuracy (the math pairs are easier for v3, so expect it higher than v3b's 80%).
  Failure modes to recognise: GSM8K still down (the anti-elaboration pairs dominate: raise metamath_dpo to x2) or added claims unchanged
  with math intact (then the factual gain genuinely does not exist on this base by training).

RELATED
  The scratch weight-transplant experiment (v3 + v2e's DPO delta, no training; not a model) is recorded in the report, section 1.6.

RESULTS (2026-10-17, 17:55-18:24; full report: C:\Development\andres-350M-dataset-recipes.html)
  The run: 420 updates (1,260 steps), 10.2M tokens, 28 min; final margin train +6.3 / val +3.5 (the equal-length math pairs separate
  cleanly once learned), val pair accuracy 79.8%, Chosen vs ref -0.04 / -0.02; weights moved 0.27% from v3's (v3b 0.21%).
  THE MATH PAIRS DID NOT PROTECT THE MATH, AND THE FACTUAL GAIN STILL DID NOT APPEAR. Against andres-350M-2-fp8v3:
    GSM8K zero-shot                               13.1% -> 7.4%    122 problems lost, 47 gained, p = 7e-9 (v3b 8.0%; the scratch transplant of v2e's full delta: 8.0%)
    extended factual suite /635                   65.4% -> 65.8%   noise
      right answer + rejected added claim         18.9% -> 17.5%   (v3b 18.3%; the scratch transplant 15.0%; v2e 12.8%)
      core answer wrong                           15.9% -> 16.7%
      pronoun follow-ups /45                      23    -> 23
      average factual reply                       33.5  -> 21.0 tokens
    20-turn suite: factual 39 -> 32, creative 28 -> 29, story 12 -> 11, loops 2 -> 0, one-word 6 -> 7
    TriviaQA 17.1 -> 15.8 (p 0.17), LAMBADA 41.6 -> 41.6, SciQ 78.5 -> 79.6, ARC-Challenge 27.2 -> 29.3 (p 0.004), HellaSwag 39.5 -> 38.8 (p 0.006)
    WikiText 23.05 -> 29.87, PG-19 33.0 -> 50.8, C4 29.9 -> 36.6 (the usual DPO drift)
  Head-to-head (80 pairs): 24-31-25 vs v3, 20-37-23 vs v2e, 21-40-19 vs v3b, 19-37-24 vs v2b, 16-39-25 vs andres-350M-2-fp8,
    37-25-18 over andres-350M-1-fp8 (p 0.014).
  What the weight geometry says (float64, embeddings counted once): the delta this run learned points 57% along v2e's delta (v3b's 86%),
    and ALL the DPO deltas are exactly orthogonal to v3's math-SFT change (cos 0.001) - the DPO does not undo the math training, a
    0.2-0.3% move in any of these DPO directions simply breaks a fragile skill. Consistent with v3b's archives (GSM8K 12.4 / 11.1 / 8.0
    at updates 60 / 180 / 304) and with the transplant sweep (alpha 0.3 / 0.5 / 1.0, report section 1.6): the loss scales with the dose,
    whatever the data.
  Verdict: DPO trained on v3 - with or without math pairs - does not reproduce v2e's factual gain and costs ~40% of the math. Not a model
    to serve. The behaviour itself is portable through the weights (the scratch transplant experiment, report section 1.6); the trained
    recipe designed from v3's own weaknesses is andres-350M-2-fp8v3e.

STATUS
  Trained and evaluated 2026-10-17. Not a success; kept for the record. Archived checkpoints and the .tmp can go.
