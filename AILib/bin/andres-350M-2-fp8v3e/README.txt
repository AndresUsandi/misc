andres-350M-2-fp8v3e  -  andres-350M-2-fp8v3's SFT weights + a DPO recipe designed from v3's own weaknesses
==========================================================================================================
Created 2026-10-17 (late) after three attempts to give v3 the v2b-era DPO recipe failed (v3b: as is; v3d: with math pairs added; both
cost 40% of the math and fixed nothing), while a scratch weight-transplant experiment (v3 + 0.3 x v2e's delta; not a model, report section 1.6)
showed the factual gain itself is compatible with v3's weights. v3e starts from the other end: what does v3 actually get wrong, and which preference data targets that.

WHAT V3 GETS WRONG (720 head-to-head verdicts against the other trained models + the 635-sample quality suite, 2026-10-17)
  head-to-head record by category:   explain 56-26 won   math 29-14   rewrite 19-13   reasoning 26-22   factual 37-37   CREATIVE 25-56 lost
  1. Following the brief (creative/constrained writing) - the one category v3 clearly loses. Its creative replies are the longest in the
     family (196 tokens; andres-350M-2-fp8 80, v2b 147, v2e 123) and the judge's reasons are "short poem" -> long poem, "short story" ->
     a dialogue, "one paragraph" -> several, "busy morning market" -> a sunset, stories that drift off the subject. Constraint/format
     failures 17 and off-topic 7 of its 56 creative losses; 5 of its 22 creative quality-suite failures are the same thing.
  2. Fabricated specifics on factual questions: 167 of its 220 factual quality-suite failures are an invented date, place or number
     ("Romeo and Juliet ... written in 1605", "the Pacific covers 2.5% of the surface"); head-to-head it also loses factual pairs for
     wrong facts ("four continents", "Brazil is multilingual"). Added-claim rate 18.9%, core-wrong 15.9%.
  3. Editing requests: asked to fix grammar it hands the sentence back with new errors ("Me and him go to the store yesterday and buyer
     some apple") - 10 of its 13 rewrite losses.
  Not weaknesses (keep): explain (wins 2:1), math (GSM8K 13.1%, wins 2:1), reasoning; replies to plain questions already short (23 tok).
  Not addressed here (no suitable preference data found): pronoun tracking in multi-turn threads (23/45), six-turn story coherence (12/30).

THE RECIPE (options-optimize.json; one set per weakness, all length-balanced; NO OffsetBias)
  weakness                      dataset (registry key)                                   pairs   passes  what the pair teaches
  following the brief           allenai/tulu-3-pref-personas-instruction-following        9,598    x1    the answer that respects the stated
                                (tulu_if_dpo; answers over ~400 tokens dropped, 19,890 -> 9,598)        paragraph / sentence / word / section /
                                                                                                        ending / keyword constraints beats the one
                                                                                                        that ignores them; 42% writing prompts;
                                                                                                        chosen shorter in 56% (no length bias)
  editing                       grammarly/coedit, grammar-correction rows (coedit_gec_dpo) 6,000    x1    the corrected sentence beats the input
                                                                                                        handed back unchanged (equal length)
  fabricated specifics          jondurbin/truthy-dpo (truthy_dpo)                         1,016    x2    the true, plain answer beats the
                                wassname/truthful_qa_preferences (truthfulqa_dpo)           817    x2    plausible falsehood; short answers on
                                argilla/OpenHermesPreferences 'misconception'               428    x2    both sides (no length bias)
                                (openhermes_misconception_dpo)
  keeping the math              abacusai/MetaMath_DPO_FewShot (metamath_dpo, --limit 4000) 4,000    x1    the correct worked solution beats the
                                                                                                        same solution with one wrong number
  ~24,100 pair-passes, ~7M tokens, expected ~300 updates / ~20 min (token-budgeted batches: 12 x 3 x 1,024 tokens per update).
  Hyper-parameters as v2e/v3b/v3d (the settings known not to collapse): 1 epoch, LR 4e-6 (min 4e-7, 10% warm-up), beta 0.3,
  dpo_sft_weight 0.2, over-long pairs truncated, eval every 20 updates on 160 pairs, compile, FP8. One change: save_interval 40
  (archives every 80 updates instead of 120) so the dose can be chosen after the fact - see WHY THE ARCHIVES MATTER.
  What was deliberately left out, and why:
    NCSOFT/offsetbias (80% of the v2e/v3b/v3d pair-passes): its rejected answers are long, elaborate, worked-looking; the three
      DPO deltas that carried it all pointed the same way (cosine 0.86 / 0.57 with v2e's) and all cost ~40% of GSM8K. v3e tests whether
      a recipe without it leaves the math alone.
    pminervini/HaluEval qa: chosen answers are bare noun phrases ("President Richard Nixon") - it would push v3 toward one-word answers
      (already 6/100) and against the "Answer in complete sentences" prompt.
    the Gutenberg DPO sets and SLoonker/RL-Claude-Creative-Writing-DPO: chosen answers of 1,000-2,600 tokens; they do not fit the context
      and reward length. codelion/ifeval-high-quality-dpo: chosen longer in 92% of pairs. stindardlogic/*: ~3% unique prompts.
    CarperAI/openai_summarize_comparisons (Reddit TL;DR, length-neutral, human-labelled): sound but off-domain; an option for a later
      run aimed at concision.

WEIGHTS TO COPY BEFORE LAUNCH (same as for v3b / v3d)
  bin/andres-350M-2-fp8v3/andres-350M-2-fp8v3.chk.trn  -> bin/andres-350M-2-fp8v3e/andres-350M-2-fp8v3e.chk.trn
  bin/andres-350M-2-fp8v3/andres-350M-2-fp8v3.pth      -> bin/andres-350M-2-fp8v3e/andres-350M-2-fp8v3e.chk.sft
  Then: python optimize.py --model_name andres-350M-2-fp8v3e
  (DPO data is already downloaded under data/Optimizing; download_datasets.py re-creates it.)

SUCCESS = v3's math kept (GSM8K within ~2 points of 13.1%) AND a measurable move on the targeted weaknesses: creative head-to-head
  against v3 and v2b no longer lost (v3 lost creative 25-56 overall), creative replies nearer 120 than 200 tokens, rewrite pairs won,
  added claims below 18.9%; extended factual at or above 65.4%, one-word answers not above 6/100, TriviaQA within a point.
  Watch during the run: the sample reply (the first entry is a Tulu constraint prompt - check it respects the constraint), "Chosen vs ref"
  near zero, validation pair accuracy rising (the CoEdIT and MetaMath pairs are easy; expect it above v3b's 80%).

WHY THE ARCHIVES MATTER (the step-size lesson of 2026-10-17)
  Every DPO delta of ~0.2% applied to v3 so far cost ~40% of GSM8K, in proportion to the size of the step (v3b's archives: 12.4 / 11.1 /
  8.0% at updates 60 / 180 / 304; the scratch transplant: 13.2 / 11.4 / 8.0% at 0.3x / 0.5x / 1.0x). Whether that was the OffsetBias direction
  or any DPO step at all is exactly what v3e decides. Either way, evaluate GSM8K on each archive (python %TEMP%\ailib_cmp\gsm8k_eval.py
  --model v3e --path <archive> --tag v3e_uNNN, or the repo benchmark with --weights) before trusting the final weights, and if the final
  weights have lost math, the best archive is the model to keep (a shorter run reproduces it by training). The archives are 4.2 GB each;
  delete them once that is decided.

RELATED
  The scratch transplant experiment (report section 1.6) showed v2e's factual behaviour is compatible with v3's weights (70.9% factual
  with the math intact at 0.3 x the delta); v3e is the attempt to get there by training, aimed at the weaknesses that experiment left
  untouched (brief-following, editing).

RESULTS (2026-10-18, 00:34-00:54; full report: C:\Development\andres-350M-dataset-recipes.html, section 1.7)
  The run: 304 updates, 7.2M tokens, 20 min; final margin train +1.20 / val +1.17 (no train-val gap: no memorisation), val pair accuracy
  79.7%, Chosen vs ref +0.07 / +0.10; weights moved 0.235% from v3's, in a direction only 17% aligned with v2e's delta and 18% with v3b's
  (40% with v3d's, which shares the math pairs) - a genuinely different DPO.
  THE TARGETED BEHAVIOURS MOVED; CORE ACCURACY AND MATH PAID FOR THEM. Against andres-350M-2-fp8v3:
    following the brief    creative head-to-head vs v3 8-6-2 (v3 had lost creative 25-56 against the field); creative replies 103 tokens
                           on the 20-turn suite (v3 212), 126 on the head-to-head prompts (v3 196); 20-turn creative 29 -> 29 (passes), story 12 -> 9
    editing                rewrite head-to-head 2-5-1 vs v3, 4-3-1 vs v3b and v3d
    fabricated specifics   added-claim failures 18.9% -> 13.7% (v2e 12.8%) - the first trained run on v3 to move this
    core answer wrong      15.9% -> 20.3%  (!)  two new failure kinds, both traceable to the data: TruthfulQA-style hedging on plain
                           questions ("There is no fixed number of hours in a day", "I have no comment" - TruthfulQA's canonical safe
                           answer, verbatim; with OffsetBias gone, the x2 TruthfulQA / truthy / misconception sets became the loudest
                           voice on short questions) and confident wrong entities in the new, shorter answers ("Apollo 11" as the rocket,
                           Congo as Africa's longest river, Mercury as the red planet, Leonardo for The Starry Night, harpsichord for 88 keys)
    extended factual suite 65.4% -> 66.0% (net flat), pronoun follow-ups 23 -> 27/45, factual replies 33.5 -> 19.1 tokens
    20-turn suite: factual 39 -> 35, all 67 -> 64, loops 2 -> 3, one-word 6 -> 5
    GSM8K                  13.1% -> 8.2% (p 3e-7); along the run: 10.6% at update 40 (p 0.004, still in warm-up), 11.5 at 120, 8.9 at 200,
                           7.6 at 280 - the loss begins within the first 40 updates, so no dose of this run keeps the math
    TriviaQA 17.1 -> 15.0 (p 0.038), LAMBADA 41.6 -> 42.7 (p 0.002), HellaSwag 39.3, ARC-Easy 56.9, SciQ 78.1, Winogrande 52.1 (noise)
    WikiText 23.05 -> 24.38, PG-19 33.0 -> 34.2, C4 29.9 -> 30.9: the smallest drift of any DPO on v3 (v3b 33.8 / 54.9; v3d 29.9 / 50.8) -
                           dropping OffsetBias did fix the drift, not the math
  Head-to-head (80 pairs): 20-41-19 vs v3 (creative 8-6-2, explain 2-6-8), 20-33-27 vs v2e, 20-35-25 vs v2b, 18-44-18 vs v3b, 21-39-20 vs
    v3d, 37-29-14 over andres-350M-1-fp8 (p 0.002, the family's strongest); replies 51 tokens on average, the shortest of the family.
  The archives on the chat suite (2026-10-18 05:10-05:40, run from a scratch copy outside bin/, deleted afterwards):
    update   moved    GSM8K   extended factual   added claims   core wrong   hedging replies   creative tokens   pronoun /45
      40     0.071%   10.6%       67.9%             12.4%         19.7%           0                 186              21
     120     0.167%   11.5%       65.8%             15.3%         19.1%           7                 136              22
     304     0.235%    8.2%       66.0%             13.7%         20.3%          13                 103              27
    (v3: 13.1% / 65.4% / 18.9% / 15.9% / 0 / 212 / 23.) The added-claim gain is there after 40 updates; so is the core-wrong rise - and at
    update 40 it is all wrong entities ("The capital of Egypt is Thebes" 5/5, "Apollo 11" as the rocket 5/5, "Earth is the closest planet
    to the Sun"), not hedging; the hedging arrives between updates 40 and 120 and grows with the TruthfulQA passes. The brief-following
    effect (creative length) builds over the whole run. So there is no dose of this run that has the gains without the core-wrong cost:
    a trained DPO's early steps are mostly gradient noise, and 0.07% of noise already flips brittle facts that the finished, averaged
    v2e delta at 0.06% left alone.
  What this settles:
    1. On v3, a DPO step of ~0.2% costs ~40% of GSM8K whatever the data: four runs, four directions (v3b, v3d, v3e, and the transplanted
       v2e delta), one outcome; and this run shows the loss starts in the first 40 updates. The math is a fragile skill at 350M; it survives
       only perturbations of ~0.06% or less. A DPO that keeps it would need a much smaller step (LR ~1e-6, or ~60 updates), with whatever
       chat effect that leaves.
    2. The Tulu instruction-following pairs work for brief-following (creative 8-6-2 vs v3, creative length halved) and the length-neutral
       correctness pairs do reduce added claims on v3 - these parts of the recipe are validated.
    3. TruthfulQA-style pairs at x2 without a "plain correct answer" counterweight teach hedging and "I have no comment" on ordinary questions;
       keep them at x1 or drop TruthfulQA, and watch core-wrong, not only added claims.
  Verdict: a different trade-off, not a better model: v3 stays the best trained all-rounder, v2e the best factual chat model. Not a model to
    serve; its recipe minus the hedging sets, at a quarter of the step, is the natural next attempt if the v3 line continues.

STATUS
  Trained and evaluated 2026-10-18. Not a net improvement over v3 (see RESULTS); kept for the record. The four archives (4 x 4.2 GB), the
  .tmp and the .chk.dpo can go; .chk.trn / .chk.sft are copies of v3's.
