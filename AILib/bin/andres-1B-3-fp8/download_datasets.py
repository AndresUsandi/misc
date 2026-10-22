#!/usr/bin/env python3
import os, subprocess, sys

MODEL = "andres-1B-3-fp8"
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

def banner(text):
    print("\n" + "=" * 60 + f"\n{text}\n" + "=" * 60, flush=True)

def run(args):
    if subprocess.call([sys.executable, "download_dataset.py", "--model_name", MODEL, *args.split()]):
        banner("[FAIL] Dataset download encountered an error.")
        sys.exit(1)

banner(f"Downloading Datasets for Model: {MODEL}")
print("""andres-1B-3-fp8 = andres-1B-2-fp8 + STEM foundations and code:
  pretraining +5.5B unique (~41B unique, ~56B seen): Cosmopedia auto-math courseware (~1.7B), OpenWebMath capped at 1.2M documents (~2.8B),
    The Stack smol Python x2 (~0.3B), OpenStax textbooks x3, LibreTexts science textbooks (~0.6B), science theory textbooks x2
  fine-tuning + CAMEL math / physics / chemistry / biology problem sets, Python instructions 18k x2, MBPP x2, Magicoder OSS-Instruct 75k
  DPO + Capybara multi-turn pairs, OffsetBias (the plain correct answer over the longer flawed one)""")

banner("[1/3] Pretraining Datasets (Training)")
run("--dataset cosmopedia_khan cosmopedia_openstax cosmopedia_stanford cosmopedia_wikihow fineweb_edu wikipedia wikipedia_simple writingprompts bookcorpus")
run("--dataset cosmopedia_stories --limit 1500000")
run("--dataset finewiki_core finewiki_simple wiki_to_rcqa gutenberg_clean_en")
run("--dataset nemotron_synth_qa --limit 3000000")
run("--dataset dclm_edu --limit 3000000")
run("--dataset cosmopedia_v2 --limit 7000000")
run("--dataset cosmopedia_math stack_smol_python openstax_textbooks libretexts_science science_theory_textbooks")
run("--dataset open_web_math --limit 1200000")

banner("[2/3] Fine-Tuning Datasets (Tuning)")
run("--dataset capybara dolly everyday_conversations gsm8k no_robots oasst2 opus_writingprompts smol_smoltalk ultrachat_200k")
run("--dataset smoltalk_magpie_ultra --limit 200000")
run("--dataset metamath_qa --limit 100000")
run("--dataset numinamath_cot --limit 20000")
run("--dataset tulu_3_sft --limit 200000")
run("--dataset camel_math camel_physics camel_chemistry camel_biology python_instructions_18k mbpp magicoder_75k")

banner("[3/3] Optimization Datasets (Optimizing)")
run("--dataset tulu_if_dpo truthy_dpo openhermes_misconception_dpo")
run("--dataset coedit_gec_dpo --limit 6000")
run("--dataset metamath_dpo --limit 4000")
run("--dataset helpsteer2_pref gutenberg_dpo")
run("--dataset capybara_dpo offsetbias_dpo")

banner(f"[SUCCESS] All datasets for {MODEL} downloaded!")
