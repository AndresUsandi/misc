#!/usr/bin/env python3
import os, subprocess, sys

MODEL = "andres-350M-2-fp8v2c"
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
  v2c DPO experiment - small-model preference sets whose chosen answers are short and more often the shorter of the pair
  (Argilla Orca pairs, Argilla DPO mix, truthy-dpo, multi-turn Capybara pairs); UltraFeedback dropped: it was ~90% of the
  old mix and its chosen answers run long. Per-dataset passes in options-optimize.json""")

banner("[1/3] Pretraining Datasets (Training)")
run("--dataset cosmopedia_khan cosmopedia_openstax cosmopedia_stanford cosmopedia_wikihow fineweb_edu wikipedia wikipedia_simple writingprompts bookcorpus")
run("--dataset cosmopedia_stories --limit 1500000")

banner("[2/3] Fine-Tuning Datasets (Tuning)")
run("--dataset dolly everyday_conversations no_robots oasst2 smol_smoltalk")

banner("[3/3] Optimization Datasets (Optimizing)")
run("--dataset capybara_dpo deita_dpo dpo_mix truthy_dpo")

banner(f"[SUCCESS] All datasets for {MODEL} downloaded!")
