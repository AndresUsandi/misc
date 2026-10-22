andres-350M-3  -  A/B twin of andres-350M-2 trained with the hybrid Muon optimizer (never trained)
===================================================================================================
WHAT IT IS (reconstructed 2026-10-19 from the files; the folder had no README)
  andres-350M-3 is andres-350M-2 with one change: the optimizer. Compared key by key, its model-params.json, options-infer.json and the
  data lists of download_datasets.py are identical to andres-350M-2's, and the only differing keys in the three stage options are
      options-train.json      use_muon: true, muon_lr: 0.003     (AdamW LR 3e-4 kept for the 1-D / norm / embedding parameters)
      options-tune.json       use_muon: true, muon_lr: 0.0006
      options-optimize.json   use_muon: true, muon_lr: 0.00002
  "Hybrid Muon" = CustomMuon (orthogonalised momentum updates, Newton-Schulz) for the 2-D weight matrices and fused AdamW for
  everything else (see gpttrain/optimizer.py, create_hybrid_optimizers). The download script's own description says why: "to decide
  whether Muon can carry the next model size" - an optimizer experiment at 350M before committing to it for a bigger model.
  andres-350M-3-fp8 is the same twin of andres-350M-2-fp8 (FP8 precision, batch 16 x 16, 2 epochs, warm-up 2,000, max_autotune), i.e.
  the pair that corresponds to the lineage's actual reference run.

RECIPE (= andres-350M-2's original one, before the v2 / v3 data experiments)
  pretraining   FineWeb-Edu 10BT x1, Wikipedia x3, Simple Wikipedia x4, Cosmopedia v1 stanford/wikihow x3, openstax/khanacademy x4,
                WritingPrompts x4, BookCorpus x1, Cosmopedia stories x1 (1.5M cap); ~20B unique tokens. andres-350M-3: fp16, batch 8 x 32,
                1 epoch, warm-up 4,000 (andres-350M-2's settings); andres-350M-3-fp8: fp8, batch 16 x 16, 2 epochs, warm-up 2,000.
  fine-tuning   smol-smoltalk, everyday conversations, No Robots, Dolly, OpenAssistant 2; 2 epochs.
  DPO           deita_dpo, dpo_mix, ultrafeedback; 2 epochs, beta 0.1, plain DPO (no anchor) - the pre-2026-10-14 configuration.

HOW TO USE IT, IF IT IS EVER RUN
  The comparison target is its twin, stage by stage: .chk.trn vs andres-350M-2's .chk.trn (benchmarks and perplexities), .chk.sft vs
  andres-350M-2's SFT, then the chat suites. Keep the twin a twin: do not port the newer SFT / DPO recipes into this folder, or the
  comparison stops isolating the optimizer. The SFT and DPO stages here are the old recipes (the DPO one predates the SFT anchor and
  the anti-elaboration data and is known to collapse small models: andres-350M-2-fp8v2c, 2026-10-14); for a modern comparison the
  pretraining stage alone (.chk.trn) is the informative one.
  NOTE: andres-350M-3-fp8's options-infer.json has no system_prompt, while andres-350M-2-fp8's has "Answer in complete sentences."
  (adopted 2026-10-12, after this folder was made). Set the same prompt before measuring, or the twins are not measured alike.

STATUS
  Configured 2026-10-05 / 10-08 (options) and 10-13 (download script); no data downloaded, no checkpoints, never trained. Superseded as a
  model recipe by the andres-350M-2-fp8 line (v2e, v3, v3f and the release andres-350M-r1); still valid as the Muon experiment.
