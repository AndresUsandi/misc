#!/usr/bin/env python3
import os, subprocess, sys

MODEL = "andres-150M-2"
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

def banner(text):
    print("\n" + "=" * 60 + f"\n{text}\n" + "=" * 60, flush=True)

def run(args):
    if subprocess.call([sys.executable, "download_dataset.py", "--model_name", MODEL, *args.split()]):
        banner("[FAIL] Dataset download encountered an error.")
        sys.exit(1)

banner(f"Downloading Datasets for Model: {MODEL}")

banner("[1/3] Pretraining Datasets (Training)")
run("--dataset bookcorpus cosmopedia dailydialog dialogsum personachat tinystories wikipedia writingprompts")

banner("[2/3] Fine-Tuning Datasets (Tuning)")
run("--dataset alpaca_gpt4 capybara deita_10k_sft no_robots slim_orca ultrachat_200k")

banner("[3/3] Optimization Datasets (Optimizing)")
run("--dataset dpo_mix")

banner(f"[SUCCESS] All datasets for {MODEL} downloaded!")
