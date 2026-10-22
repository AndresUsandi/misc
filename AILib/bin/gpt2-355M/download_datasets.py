#!/usr/bin/env python3
import os, subprocess, sys

MODEL = "gpt2-355M"
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

def banner(text):
    print("\n" + "=" * 60 + f"\n{text}\n" + "=" * 60, flush=True)

def run(args):
    if subprocess.call([sys.executable, "download_dataset.py", "--model_name", MODEL, *args.split()]):
        banner("[FAIL] Dataset download encountered an error.")
        sys.exit(1)

banner(f"Downloading Datasets for Model: {MODEL}")

banner("[1/2] Fine-Tuning Datasets (Tuning)")
run("--purpose tune --dataset dailydialog personachat sharegpt")

banner("[2/2] Optimization Datasets (Optimizing)")
run("--purpose optimize --dataset truthy_dpo helpsteer3_pref helpsteer2_pref deita_dpo gutenberg_dpo")

banner(f"[SUCCESS] All datasets for {MODEL} downloaded!")
