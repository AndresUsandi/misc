#!/usr/bin/env python3
import os, subprocess, sys

MODEL = "andres-350M-2-fp8v2"
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
  v2 SFT experiment - long-form multi-turn and creative sets on top of the andres-350M-2-fp8 mix: SmolTalk magpie-ultra
  (capped at 200k conversations), UltraChat 200k, Capybara, Opus WritingPrompts; per-dataset passes in options-tune.json
  preference optimization: UltraFeedback, Argilla DPO mix, Orca DPO pairs""")

banner("[1/3] Pretraining Datasets (Training)")
run("--dataset cosmopedia_khan cosmopedia_openstax cosmopedia_stanford cosmopedia_wikihow fineweb_edu wikipedia wikipedia_simple writingprompts bookcorpus")
run("--dataset cosmopedia_stories --limit 1500000")

banner("[2/3] Fine-Tuning Datasets (Tuning)")
run("--dataset capybara dolly everyday_conversations no_robots oasst2 opus_writingprompts smol_smoltalk ultrachat_200k")
run("--dataset smoltalk_magpie_ultra --limit 200000")

banner("[3/3] Optimization Datasets (Optimizing)")
run("--dataset deita_dpo dpo_mix ultrafeedback")

banner(f"[SUCCESS] All datasets for {MODEL} downloaded!")
