#!/usr/bin/env python3
import os, subprocess, sys

MODEL = "gpt2-355Mv2"
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

def banner(text):
    print("\n" + "=" * 60 + f"\n{text}\n" + "=" * 60, flush=True)

def run(args):
    if subprocess.call([sys.executable, "download_dataset.py", "--model_name", MODEL, *args.split()]):
        banner("[FAIL] Dataset download encountered an error.")
        sys.exit(1)

banner(f"Downloading Datasets (v2 mix) for Model: {MODEL}")

banner("[1/2] Fine-Tuning Datasets (Tuning)")
# Passes per dataset are set in gpt2-355Mv2.options-tune.json (num_epochs_dataset_specific): smol_smoltalk x2 (~368M tokens/pass, the backbone,
# the SmolLM2-360M recipe), alpaca_gpt4 x3 (simple single-turn tasks), no_robots / oasst2 x6 (human-written), everyday_conversations x6 (short casual chat).
# Dropped: dailydialog (pre-tokenized " , " / " ." spacing in 100% of samples, median 12-token replies), capybara (math/code/philosophy-heavy
# reasoning, 37% of conversations split at 1024 tokens), opus_writingprompts (97% of stories exceed 1024 tokens), sharegpt, personachat.
run("--purpose tune --dataset smol_smoltalk alpaca_gpt4 no_robots oasst2 everyday_conversations")

banner("[2/2] Optimization Datasets (Optimizing)")
run("--purpose optimize --dataset ultrafeedback dpo_mix capybara_dpo helpsteer2_pref truthy_dpo")

banner(f"[SUCCESS] All v2 datasets for {MODEL} downloaded!")
