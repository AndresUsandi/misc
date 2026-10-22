#!/usr/bin/env python3
import os, subprocess, sys

MODEL = "gpt2-355Mv3"
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

def banner(text):
    print("\n" + "=" * 60 + f"\n{text}\n" + "=" * 60, flush=True)

def run(args):
    if subprocess.call([sys.executable, "download_dataset.py", "--model_name", MODEL, *args.split()]):
        banner("[FAIL] Dataset download encountered an error.")
        sys.exit(1)

banner(f"Downloading Datasets (v3: continued pretraining + v2 SFT mix) for Model: {MODEL}")

banner("[1/3] Continued-Pretraining Datasets (Training)")
# ~2.7B tokens on top of GPT-2 355M's own weights (the Training stage starts from gpt2-355Mv3.pth): ~21% replay of WebText-like text so the
# model keeps what it knows, ~79% fact-dense text it never saw. Passes per set are in gpt2-355Mv3.options-train.json (num_epochs_dataset_specific).
#   openwebtext         --limit 500000  ~560M tokens  replay: the public clone of GPT-2's own training data (anchors the old knowledge)
#   fineweb_edu         --limit 900000  ~930M tokens  educational web pages, the SmolLM pretraining backbone
#   wikipedia           --limit 150000  ~650M tokens  the head of the dump = the big core articles (~4,900 tokens each: history, science, people, places)
#   wikipedia_simple    (all, x3)       ~190M tokens  the same core facts restated in plain language
#   cosmopedia_wikihow  (all)           ~165M tokens  how-to articles, the register of assistant answers
#   cosmopedia_openstax (all)           ~130M tokens  textbook STEM basics
#   cosmopedia_khan     (all, x2)        ~40M tokens  beginner-level explanations
#   cosmopedia_stanford --limit 100000   ~95M tokens  synthetic textbook chapters across all subjects
run("--purpose train --dataset openwebtext --limit 500000")
run("--purpose train --dataset fineweb_edu --limit 900000")
run("--purpose train --dataset wikipedia --limit 150000")
run("--purpose train --dataset cosmopedia_stanford --limit 100000")
run("--purpose train --dataset wikipedia_simple cosmopedia_wikihow cosmopedia_openstax cosmopedia_khan")

banner("[2/3] Fine-Tuning Datasets (Tuning) - identical to gpt2-355Mv2")
run("--purpose tune --dataset smol_smoltalk alpaca_gpt4 no_robots oasst2 everyday_conversations")

banner("[3/3] Optimization Datasets (Optimizing) - identical to gpt2-355Mv2")
run("--purpose optimize --dataset ultrafeedback dpo_mix capybara_dpo helpsteer2_pref truthy_dpo")

banner(f"[SUCCESS] All v3 datasets for {MODEL} downloaded!")
