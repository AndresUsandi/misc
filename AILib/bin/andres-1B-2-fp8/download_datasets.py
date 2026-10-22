#!/usr/bin/env python3
import os, subprocess, sys

MODEL = "andres-1B-2-fp8"
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

def banner(text):
    print("\n" + "=" * 60 + f"\n{text}\n" + "=" * 60, flush=True)

def run(args):
    if subprocess.call([sys.executable, "download_dataset.py", "--model_name", MODEL, *args.split()]):
        banner("[FAIL] Dataset download encountered an error.")
        sys.exit(1)

banner(f"Downloading Datasets for Model: {MODEL}")
print("""andres-1B-2-fp8 = andres-1B-1-fp8 + knowledge in more forms and more unique text (the andres-150M-3 / gpt2-774Mv2 lessons):
  pretraining +16B unique (~35B unique, ~50B seen): FineWiki core articles (tables kept, infobox facts under the title) x2, FineWiki Simple x2,
    Wiki-to-RCQA (a passage, then questions and answers about it) x2, Nemotron synthetic QA capped at 3M documents (~1.5B), DCLM-Edu score 3+
    capped at 3M pages (~4.5B, a second educational crawl next to FineWeb-Edu), Cosmopedia v2 capped at 7M documents (~5B), clean Project
    Gutenberg (~3.1B: keeps fiction and formal prose near 14% of what is seen; PG-19 stops being a neutral perplexity text, use C4)
  fine-tuning + Tulu 3 SFT mixture capped at 200k conversations (~245M tokens: real user prompts, IFEval-style constraints, refusals)
  DPO + HelpSteer2 preference pairs (human-rated correctness / coherence / verbosity), Gutenberg DPO (human chapters over LLM chapters)""")

banner("[1/3] Pretraining Datasets (Training)")
run("--dataset cosmopedia_khan cosmopedia_openstax cosmopedia_stanford cosmopedia_wikihow fineweb_edu wikipedia wikipedia_simple writingprompts bookcorpus")
run("--dataset cosmopedia_stories --limit 1500000")
run("--dataset finewiki_core finewiki_simple wiki_to_rcqa gutenberg_clean_en")
run("--dataset nemotron_synth_qa --limit 3000000")
run("--dataset dclm_edu --limit 3000000")
run("--dataset cosmopedia_v2 --limit 7000000")

banner("[2/3] Fine-Tuning Datasets (Tuning)")
run("--dataset capybara dolly everyday_conversations gsm8k no_robots oasst2 opus_writingprompts smol_smoltalk ultrachat_200k")
run("--dataset smoltalk_magpie_ultra --limit 200000")
run("--dataset metamath_qa --limit 100000")
run("--dataset numinamath_cot --limit 20000")
run("--dataset tulu_3_sft --limit 200000")

banner("[3/3] Optimization Datasets (Optimizing)")
run("--dataset tulu_if_dpo truthy_dpo openhermes_misconception_dpo")
run("--dataset coedit_gec_dpo --limit 6000")
run("--dataset metamath_dpo --limit 4000")
run("--dataset helpsteer2_pref gutenberg_dpo")

banner(f"[SUCCESS] All datasets for {MODEL} downloaded!")
