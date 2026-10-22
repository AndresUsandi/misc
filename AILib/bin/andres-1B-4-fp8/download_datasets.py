#!/usr/bin/env python3
import os, subprocess, sys

MODEL = "andres-1B-4-fp8"
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

def banner(text):
    print("\n" + "=" * 60 + f"\n{text}\n" + "=" * 60, flush=True)

def run(args):
    if subprocess.call([sys.executable, "download_dataset.py", "--model_name", MODEL, *args.split()]):
        banner("[FAIL] Dataset download encountered an error.")
        sys.exit(1)

banner(f"Downloading Datasets for Model: {MODEL}")
print("""andres-1B-4-fp8 = andres-1B-3-fp8 + the rest of what is worth reading: engineering, more code, the modern informal web, a broad SFT mix.
  pretraining +5.7B unique (~47B unique, ~62B seen): LibreTexts engineering textbooks (~0.6B), MIT OCW lecture transcripts x2, ChemPile
    education x2, FineFineWeb aerospace, The Stack smol-xl (87 languages, ~2.5B, not capped: its files stream language by language),
    OpenWebText capped at 2M documents (~2.2B: the colloquial register FineWeb-Edu's classifier removes). Left out as poor value per token
    for a 1B chat model: patents, arXiv, peS2o papers, NRC documents, the Verilog corpus, DeepMind's synthetic arithmetic.
  fine-tuning + OpenHermes 2.5 (~466M tokens, the broad GPT-4 mix), Evol-Instruct code 80k, CodeFeedback 156k, MathInstruct, and the science /
    engineering QA sets (medicine, earth science, astronomy, climate, materials; FE exam, electrical, electronics, mechanical, civil, chemical,
    structural engineering), downloaded last in their own section: their sources are untested here, and a failure there blocks nothing else.
    Sources listed twice in the registry (climate_qa / environmental_eng_qa, geogpt_cot / geotechnical_eng_qa, matscibench / materials_eng_bench,
    bioinstruct / biomedical_eng_qa, geogpt_ocean / naval_marine_qa) are taken once.
  DPO + HelpSteer3 preference pairs (2025, multi-turn, STEM and code), SmolTalk DPO, Argilla dpo-mix-7k""")

banner("[1/4] Pretraining Datasets (Training)")
run("--dataset cosmopedia_khan cosmopedia_openstax cosmopedia_stanford cosmopedia_wikihow fineweb_edu wikipedia wikipedia_simple writingprompts bookcorpus")
run("--dataset cosmopedia_stories --limit 1500000")
run("--dataset finewiki_core finewiki_simple wiki_to_rcqa gutenberg_clean_en")
run("--dataset nemotron_synth_qa --limit 3000000")
run("--dataset dclm_edu --limit 3000000")
run("--dataset cosmopedia_v2 --limit 7000000")
run("--dataset cosmopedia_math stack_smol_python openstax_textbooks libretexts_science science_theory_textbooks")
run("--dataset open_web_math --limit 1200000")
run("--dataset libretexts_engineering mit_ocw_engineering chempile_education aerospace_fineweb stack_smol_xl")
run("--dataset openwebtext --limit 2000000")

banner("[2/4] Fine-Tuning Datasets (Tuning)")
run("--dataset capybara dolly everyday_conversations gsm8k no_robots oasst2 opus_writingprompts smol_smoltalk ultrachat_200k")
run("--dataset smoltalk_magpie_ultra --limit 200000")
run("--dataset metamath_qa --limit 100000")
run("--dataset numinamath_cot --limit 20000")
run("--dataset tulu_3_sft --limit 200000")
run("--dataset camel_math camel_physics camel_chemistry camel_biology python_instructions_18k mbpp magicoder_75k")
run("--dataset openhermes evol_code_80k code_feedback_156k math_instruct")

banner("[3/4] Optimization Datasets (Optimizing)")
run("--dataset tulu_if_dpo truthy_dpo openhermes_misconception_dpo")
run("--dataset coedit_gec_dpo --limit 6000")
run("--dataset metamath_dpo --limit 4000")
run("--dataset helpsteer2_pref gutenberg_dpo")
run("--dataset capybara_dpo offsetbias_dpo")
run("--dataset helpsteer3_pref smoltalk_dpo dpo_mix")

banner("[4/4] Science and Engineering QA Sets (Tuning; untested sources, last so a failure here blocks nothing else)")
run("--dataset medqa pubmedqa geogpt_cot arxiv_astro_qa usaaao_qa nasa_smd_qa climate_qa matscibench")
run("--dataset fe_exam_qa electrical_eng_qa electronics_ir_qa mech_qa civil_eng_qa chem_eng_qa sfem_structural buildeng_structural")

banner(f"[SUCCESS] All datasets for {MODEL} downloaded!")
