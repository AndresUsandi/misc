#!/usr/bin/env python3
import os, subprocess, sys

MODEL = "andres-350M-2-fp8v3"
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
  fine-tuning: smol-smoltalk (SmolLM2-360M recipe), everyday conversations, No Robots, Dolly, OpenAssistant 2
  v3 SFT experiment - reasoning and arithmetic sets on top of the andres-350M-2-fp8v2b recipe (its sets and passes: long-form
  sets at one pass, smol-smoltalk at two), ~6% of the tokens seen: GSM8K, MetaMathQA (capped at 100k problems), NuminaMath-CoT
  (capped at 20k problems); per-dataset passes in options-tune.json
  preference optimization: the andres-350M-2-fp8v2c sets (Argilla Orca pairs, Argilla DPO mix, truthy-dpo, multi-turn Capybara
  pairs; UltraFeedback dropped), so v3 and v2c differ only by the math SFT data""")

banner("[1/3] Pretraining Datasets (Training)")
run("--dataset cosmopedia_khan cosmopedia_openstax cosmopedia_stanford cosmopedia_wikihow fineweb_edu wikipedia wikipedia_simple writingprompts bookcorpus")
run("--dataset cosmopedia_stories --limit 1500000")

banner("[2/3] Fine-Tuning Datasets (Tuning)")
run("--dataset capybara dolly everyday_conversations gsm8k no_robots oasst2 opus_writingprompts smol_smoltalk ultrachat_200k")
run("--dataset smoltalk_magpie_ultra --limit 200000")
run("--dataset metamath_qa --limit 100000")
run("--dataset numinamath_cot --limit 20000")

banner("[3/3] Optimization Datasets (Optimizing)")
run("--dataset capybara_dpo deita_dpo dpo_mix truthy_dpo")

banner(f"[SUCCESS] All datasets for {MODEL} downloaded!")
