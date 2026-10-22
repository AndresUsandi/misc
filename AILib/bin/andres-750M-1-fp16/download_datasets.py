#!/usr/bin/env python3
import os, subprocess, sys

MODEL = "andres-750M-1-muon"
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

def banner(text):
    print("\n" + "=" * 60 + f"\n{text}\n" + "=" * 60, flush=True)

def run(args):
    if subprocess.call([sys.executable, "download_dataset.py", "--model_name", MODEL, *args.split()]):
        banner("[FAIL] Dataset download encountered an error.")
        sys.exit(1)

banner(f"Downloading Datasets for Model: {MODEL}")
print("""The andres2s recipe scaled for a 650M-760M model with a 2k context: ~41B unique tokens, ~50B seen with the per-dataset
epochs of options-train.json. Pretraining: FineWeb-Edu 100B sample capped at 18M documents (~18.6B, replaces the 10B
sample), English Wikipedia (x4), Simple Wikipedia, Cosmopedia v1 textbooks/how-to (stanford, wikihow, openstax,
khanacademy), Cosmopedia v2 capped at 7M documents (~5B); modern fiction ~10% of what is seen: WritingPrompts (x4),
BookCorpus novels, Cosmopedia stories capped at 3M stories (~2.6B).
  fine-tuning: smol-smoltalk, SmolTalk magpie-ultra capped at 200K long multi-turn conversations, Opus WritingPrompts
  stories, everyday conversations, No Robots, Dolly, OpenAssistant 2
  preference optimization: UltraFeedback, Argilla DPO mix, Orca DPO pairs, SmolTalk DPO
Disk: ~110 GB of text plus ~80 GB of token caches built on first use.""")

banner("[1/3] Pretraining Datasets (Training)")
run("--dataset wikipedia wikipedia_simple cosmopedia_stanford cosmopedia_wikihow cosmopedia_openstax cosmopedia_khan writingprompts bookcorpus")
run("--dataset fineweb_edu_100bt --limit 18000000")
run("--dataset cosmopedia_v2 --limit 7000000")
run("--dataset cosmopedia_stories --limit 3000000")

banner("[2/3] Fine-Tuning Datasets (Tuning)")
run("--dataset smol_smoltalk opus_writingprompts everyday_conversations no_robots dolly oasst2")
run("--dataset smoltalk_magpie_ultra --limit 200000")

banner("[3/3] Optimization Datasets (Optimizing)")
run("--dataset ultrafeedback dpo_mix deita_dpo smoltalk_dpo")

banner(f"[SUCCESS] All datasets for {MODEL} downloaded!")
