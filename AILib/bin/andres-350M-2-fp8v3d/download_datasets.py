#!/usr/bin/env python3
import os, subprocess, sys

MODEL = "andres-350M-2-fp8v3d"
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

def banner(text):
    print("\n" + "=" * 60 + f"\n{text}\n" + "=" * 60, flush=True)

def run(args):
    if subprocess.call([sys.executable, "download_dataset.py", "--model_name", MODEL, *args.split()]):
        banner("[FAIL] Dataset download encountered an error.")
        sys.exit(1)

banner(f"Downloading Datasets for Model: {MODEL}")
print("""andres-350M-2-fp8v3's SFT weights + the andres-350M-2-fp8v2e DPO recipe WITH math preference pairs in the mix (v3b, the same recipe
without them, cost GSM8K 13.1 -> 8.0% and did not reduce the added-claim rate):
  pretraining ~20B unique tokens (~32B seen with the per-dataset epochs of options-train.json): FineWeb-Edu 10B sample,
  English Wikipedia, Simple Wikipedia, Cosmopedia textbooks/how-to (stanford, wikihow, openstax, khanacademy);
  modern fiction ~12% of what is seen: WritingPrompts, BookCorpus novels, Cosmopedia stories (capped at 1.5M stories)
  fine-tuning: the v2b recipe (smol-smoltalk and the small sets x2, magpie-ultra x1 capped at 200k, UltraChat x0.5, Capybara x2,
  Opus WritingPrompts x2) + gsm8k x3, MetaMathQA x3 (100k cap), NuminaMath-CoT x1 (20k cap); passes in options-tune.json
  DPO (1 epoch): OffsetBias x1.5, OpenHermesPreferences misconception x1, TruthfulQA pairs x1.5, truthy-dpo x1.5
  + MetaMath_DPO_FewShot x1 (8,000 pairs: the correct worked solution vs the same solution with one corrupted number, equal length,
  so the preference is about arithmetic correctness only and the SFT anchor replays correct derivations); passes in options-optimize.json""")

banner("[1/3] Pretraining Datasets (Training)")
run("--dataset cosmopedia_khan cosmopedia_openstax cosmopedia_stanford cosmopedia_wikihow fineweb_edu wikipedia wikipedia_simple writingprompts bookcorpus")
run("--dataset cosmopedia_stories --limit 1500000")

banner("[2/3] Fine-Tuning Datasets (Tuning)")
run("--dataset capybara dolly everyday_conversations gsm8k no_robots oasst2 opus_writingprompts smol_smoltalk ultrachat_200k")
run("--dataset smoltalk_magpie_ultra --limit 200000")
run("--dataset metamath_qa --limit 100000")
run("--dataset numinamath_cot --limit 20000")

banner("[3/3] Optimization Datasets (Optimizing)")
run("--dataset offsetbias_dpo openhermes_misconception_dpo truthfulqa_dpo truthy_dpo")
run("--dataset metamath_dpo --limit 8000")

banner(f"[SUCCESS] All datasets for {MODEL} downloaded!")
