#!/usr/bin/env python3
import os, subprocess, sys

MODEL = "andres-350M-2-fp8v2d"
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

def banner(text):
    print("\n" + "=" * 60 + f"\n{text}\n" + "=" * 60, flush=True)

def run(args):
    if subprocess.call([sys.executable, "download_dataset.py", "--model_name", MODEL, *args.split()]):
        banner("[FAIL] Dataset download encountered an error.")
        sys.exit(1)

banner(f"Downloading Datasets for Model: {MODEL}")
print("""Same architecture and training options as andres-350M-1-fp8, different data:
  pretraining ~20B unique tokens (~32B seen with the per-dataset epochs of options-train.json): FineWeb-Edu 10B sample,
  English Wikipedia, Simple Wikipedia, Cosmopedia textbooks/how-to (stanford, wikihow, openstax, khanacademy);
  modern fiction ~12% of what is seen: WritingPrompts, BookCorpus novels, Cosmopedia stories (capped at 1.5M stories)
  fine-tuning: the andres-350M-2-fp8v2b recipe (smol-smoltalk and the small sets x2, magpie-ultra x1 capped at 200k,
  UltraChat x0.5, Capybara x2, Opus WritingPrompts x2; passes in options-tune.json)
  v2d DPO experiment - preference sets that point AWAY from elaboration (a survey of ~15 Hugging Face preference sets on
  2026-10-15 found that judged preference data prefers the longer answer in 56-80% of pairs, which is what the v2c attempts
  learned): OffsetBias (the plain correct answer beats a longer flawed one in 97% of pairs), the misconception category of
  OpenHermesPreferences, TruthfulQA pairs, truthy-dpo. Per-dataset passes in options-optimize.json""")

banner("[1/3] Pretraining Datasets (Training)")
run("--dataset cosmopedia_khan cosmopedia_openstax cosmopedia_stanford cosmopedia_wikihow fineweb_edu wikipedia wikipedia_simple writingprompts bookcorpus")
run("--dataset cosmopedia_stories --limit 1500000")

banner("[2/3] Fine-Tuning Datasets (Tuning)")
run("--dataset capybara dolly everyday_conversations no_robots oasst2 opus_writingprompts smol_smoltalk ultrachat_200k")
run("--dataset smoltalk_magpie_ultra --limit 200000")

banner("[3/3] Optimization Datasets (Optimizing)")
run("--dataset offsetbias_dpo openhermes_misconception_dpo truthfulqa_dpo truthy_dpo")

banner(f"[SUCCESS] All datasets for {MODEL} downloaded!")
