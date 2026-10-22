#!/usr/bin/env python3
import os, subprocess, sys

MODEL = "andres-1B-1-fp8"
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

def banner(text):
    print("\n" + "=" * 60 + f"\n{text}\n" + "=" * 60, flush=True)

def run(args):
    if subprocess.call([sys.executable, "download_dataset.py", "--model_name", MODEL, *args.split()]):
        banner("[FAIL] Dataset download encountered an error.")
        sys.exit(1)

banner(f"Downloading Datasets for Model: {MODEL}")
print("""andres-1B-1-fp8: the andres-350M-r1 recipe on a 913M-parameter model (16 layers x 2048, 16 heads of 128, 2k context), data unchanged, so
the difference to andres-350M-r1 is the model size alone. Pretraining ~19B unique tokens, ~32B seen (per-dataset passes in options-train.json);
fine-tuning and DPO exactly r1's. andres-1B-2/3/4-fp8 each add datasets on top of the previous one (strict supersets, same caps and passes).""")

banner("[1/3] Pretraining Datasets (Training)")
run("--dataset cosmopedia_khan cosmopedia_openstax cosmopedia_stanford cosmopedia_wikihow fineweb_edu wikipedia wikipedia_simple writingprompts bookcorpus")
run("--dataset cosmopedia_stories --limit 1500000")

banner("[2/3] Fine-Tuning Datasets (Tuning)")
run("--dataset capybara dolly everyday_conversations gsm8k no_robots oasst2 opus_writingprompts smol_smoltalk ultrachat_200k")
run("--dataset smoltalk_magpie_ultra --limit 200000")
run("--dataset metamath_qa --limit 100000")
run("--dataset numinamath_cot --limit 20000")

banner("[3/3] Optimization Datasets (Optimizing)")
run("--dataset tulu_if_dpo truthy_dpo openhermes_misconception_dpo")
run("--dataset coedit_gec_dpo --limit 6000")
run("--dataset metamath_dpo --limit 4000")

banner(f"[SUCCESS] All datasets for {MODEL} downloaded!")
