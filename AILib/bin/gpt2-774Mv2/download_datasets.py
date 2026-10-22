#!/usr/bin/env python3
import os, subprocess, sys

MODEL = "gpt2-774Mv2"
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

def banner(text):
    print("\n" + "=" * 60 + f"\n{text}\n" + "=" * 60, flush=True)

def run(args):
    if subprocess.call([sys.executable, "download_dataset.py", "--model_name", MODEL, *args.split()]):
        banner("[FAIL] Dataset download encountered an error.")
        sys.exit(1)

banner(f"Downloading Datasets (v2: continued pretraining + gpt2-774M SFT/DPO mix) for Model: {MODEL}")

banner("[1/3] Continued-Pretraining Datasets (Training)")
# ~5.1B tokens seen on top of OpenAI's GPT-2 Large weights (the Training stage starts from gpt2-774Mv2.pth); ~3.5-4 h of downloading.
# Passes per set are in gpt2-774Mv2.options-train.json (num_epochs_dataset_specific); GPT-2 tokens measured on samples of each set.
#   finewiki_core      (all, x2)        ~0.94B tokens  core Wikipedia articles, tables kept, infobox facts under the title (scans ~38 GB, ~2 h)
#   finewiki_simple    (all)            ~0.19B tokens  the same facts in Simple English
#   wiki_to_rcqa       --limit 1450000  ~0.30B tokens  Wikipedia passages followed by questions and answers about them
#   nemotron_synth_qa  --limit 510000   ~0.25B tokens  web pages followed by questions and answers about them
#   dclm_edu           --limit 790000   ~1.20B tokens  educational web pages (score 3+), the SmolLM2-360M web backbone
#   fineweb_edu        --limit 725000   ~0.75B tokens  educational web pages from another crawl and classifier
#   cosmopedia_v2      --limit 350000   ~0.25B tokens  synthetic textbooks and explainers
#   openwebtext        --limit 265000   ~0.30B tokens  replay of GPT-2's own training data, so it keeps what it already knows
run("--purpose train --dataset finewiki_core finewiki_simple")
run("--purpose train --dataset wiki_to_rcqa --limit 1450000")
run("--purpose train --dataset nemotron_synth_qa --limit 510000")
run("--purpose train --dataset dclm_edu --limit 790000")
run("--purpose train --dataset fineweb_edu --limit 725000")
run("--purpose train --dataset cosmopedia_v2 --limit 350000")
run("--purpose train --dataset openwebtext --limit 265000")

banner("[2/3] Fine-Tuning Datasets (Tuning) - identical to gpt2-774M")
run("--purpose tune --dataset smol_smoltalk alpaca_gpt4 no_robots oasst2 everyday_conversations")

banner("[3/3] Optimization Datasets (Optimizing) - identical to gpt2-774M")
run("--purpose optimize --dataset truthy_dpo helpsteer3_pref helpsteer2_pref deita_dpo gutenberg_dpo")

banner(f"[SUCCESS] All v2 datasets for {MODEL} downloaded!")
