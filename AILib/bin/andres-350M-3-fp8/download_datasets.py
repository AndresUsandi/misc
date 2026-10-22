#!/usr/bin/env python3
import os, subprocess, sys

MODEL = "andres-350M-4-fp8"
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

def banner(text):
    print("\n" + "=" * 60 + f"\n{text}\n" + "=" * 60, flush=True)

def run(args):
    if subprocess.call([sys.executable, "download_dataset.py", "--model_name", MODEL, *args.split()]):
        banner("[FAIL] Dataset download encountered an error.")
        sys.exit(1)

banner(f"Downloading Datasets for Model: {MODEL}")
print("""andres-350M-4-fp8 (formerly andres-350M-2-fp8vNext). Same architecture and pretraining hyper-parameters as andres-350M-2-fp8, different data:
  the pretraining-budget experiment - grow the budget so knowledge AND fiction both improve on andres-350M-2-fp8 (~47B tokens seen
  with the per-dataset passes of options-train.json, vs 28B; ~140 GB of text on disk):
  knowledge ~37B seen: FineWeb-Edu 100BT sample capped at 19.5M documents (~20B fresh tokens, replaces the 10B sample x1),
  English Wikipedia x2, Simple Wikipedia x4, Cosmopedia v2 capped at 7M documents (~5B), Cosmopedia v1 stanford x2,
  wikihow x3, openstax x4, khanacademy x4;
  fiction ~10B seen (21%, was 12%): BookCorpus x2 (as andres-350M-1-fp8 saw it), clean Project Gutenberg books x1,
  Cosmopedia stories capped at 3M stories, WritingPrompts x4
  fine-tuning (updated 2026-10-19 to andres-350M-r1's = andres-350M-2-fp8v3's): the v2b recipe (smol-smoltalk and the small sets x2,
  magpie-ultra x1 capped at 200k, UltraChat x0.5, Capybara x2, Opus WritingPrompts x2) + gsm8k x3, MetaMathQA x3 (100k cap),
  NuminaMath-CoT x1 (20k cap); passes in options-tune.json
  preference optimization (updated 2026-10-19 to andres-350M-r1's = andres-350M-2-fp8v3f's): Tulu 3 instruction-following pairs x1,
  CoEdIT grammar pairs x1 (6,000), MetaMath correctness pairs x1 (4,000), truthy-dpo x1, OpenHermesPreferences misconception x1; beta 1.0,
  the embeddings and transformer blocks 0-11 frozen, the math tuning sets replayed with the SFT loss during the DPO, LR 2e-6; passes in
  options-optimize.json. andres-350M-4-fp8 therefore differs from andres-350M-r1 only by its pretraining""")

banner("[1/3] Pretraining Datasets (Training)")
run("--dataset cosmopedia_khan cosmopedia_openstax cosmopedia_stanford cosmopedia_wikihow wikipedia wikipedia_simple writingprompts bookcorpus gutenberg_clean_en")
run("--dataset fineweb_edu_100bt --limit 19500000")
run("--dataset cosmopedia_v2 --limit 7000000")
run("--dataset cosmopedia_stories --limit 3000000")

banner("[2/3] Fine-Tuning Datasets (Tuning)")
run("--dataset capybara dolly everyday_conversations gsm8k no_robots oasst2 opus_writingprompts smol_smoltalk ultrachat_200k")
run("--dataset smoltalk_magpie_ultra --limit 200000")
run("--dataset metamath_qa --limit 100000")
run("--dataset numinamath_cot --limit 20000")

banner("[3/3] Optimization Datasets (Optimizing)")
run("--dataset tulu_if_dpo truthy_dpo openhermes_misconception_dpo")
run("--dataset coedit_gec_dpo --limit 6000")
run("--dataset metamath_dpo --limit 4000")

banner(f"[SUCCESS] All datasets for {MODEL} downloaded!")
