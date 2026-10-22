#!/usr/bin/env python3
import os, subprocess, sys

MODEL = "andres-350M-2-fp8v3f"
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

def banner(text):
    print("\n" + "=" * 60 + f"\n{text}\n" + "=" * 60, flush=True)

def run(args):
    if subprocess.call([sys.executable, "download_dataset.py", "--model_name", MODEL, *args.split()]):
        banner("[FAIL] Dataset download encountered an error.")
        sys.exit(1)

banner(f"Downloading Datasets for Model: {MODEL}")
print("""andres-350M-2-fp8v3's SFT weights + the v3e DPO recipe (designed from v3's own weaknesses) with three mechanisms that keep the DPO from
damaging v3's brittle skills (math, fact retrieval): beta 1.0, the embeddings and transformer blocks 0-11 frozen, and v3's math fine-tuning
data replayed with the SFT loss during the DPO (the tuning sets below are downloaded for that replay); half the learning rate (2e-6):
  pretraining ~20B unique tokens (~32B seen with the per-dataset epochs of options-train.json): FineWeb-Edu 10B sample,
  English Wikipedia, Simple Wikipedia, Cosmopedia textbooks/how-to (stanford, wikihow, openstax, khanacademy);
  modern fiction ~12% of what is seen: WritingPrompts, BookCorpus novels, Cosmopedia stories (capped at 1.5M stories)
  fine-tuning: the v2b recipe (smol-smoltalk and the small sets x2, magpie-ultra x1 capped at 200k, UltraChat x0.5, Capybara x2,
  Opus WritingPrompts x2) + gsm8k x3, MetaMathQA x3 (100k cap), NuminaMath-CoT x1 (20k cap); passes in options-tune.json
  DPO (1 epoch; passes in options-optimize.json), one set per measured weakness; TruthfulQA pairs dropped (they taught 'I have no comment'):
    following the brief (v3's worst head-to-head category, creative 25-56): Tulu 3 instruction-following preference pairs x1
      (IFEval-style constraints: paragraphs / sentences / words / sections / endings / keywords; answers over ~400 tokens dropped)
    editing requests echoed with new errors: CoEdIT grammar-correction pairs x1 (corrected sentence vs the input handed back; 6,000)
    fabricated specifics on factual questions: truthy-dpo x1, OpenHermesPreferences misconception x1
      (length-neutral correctness pairs; NO OffsetBias - its long elaborate rejected answers are the suspected anti-derivation signal)
    keeping the math: MetaMath_DPO_FewShot x1 (4,000 correctness-only pairs, equal length)""")

banner("[1/3] Pretraining Datasets (Training)")
run("--dataset cosmopedia_khan cosmopedia_openstax cosmopedia_stanford cosmopedia_wikihow fineweb_edu wikipedia wikipedia_simple writingprompts bookcorpus")
run("--dataset cosmopedia_stories --limit 1500000")

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
