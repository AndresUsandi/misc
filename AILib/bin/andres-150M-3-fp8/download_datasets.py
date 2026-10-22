#!/usr/bin/env python3
import os, subprocess, sys

MODEL = "andres-150M-3"
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

def banner(text):
    print("\n" + "=" * 60 + f"\n{text}\n" + "=" * 60, flush=True)

def run(args):
    if subprocess.call([sys.executable, "download_dataset.py", "--model_name", MODEL, *args.split()]):
        banner("[FAIL] Dataset download encountered an error.")
        sys.exit(1)

banner(f"Downloading Datasets for Model: {MODEL}")
print("""Third 150M recipe: the andres-350M-2-fp8 lineage's lessons applied to a 151M model (24 layers x 640, qk_norm, tied embeddings: the
same depth as the 350M at the parameter count of andres-150M-1/2, whose 8 x 1024 shape is the worst region of the MobileLLM depth study).
  pretraining ~31B tokens seen from ~24B unique (per-dataset passes in options-train.json; ~75 GB of text + ~45 GB of token caches):
    educational web 39%: FineWeb-Edu 10B sample x1, DCLM-Edu score 3+ capped at 1.3M pages (~2B, the SmolLM2 web backbone)
    core knowledge, repeated in several forms 25%: FineWiki core articles (page id < 400K, infobox facts under the title) x4,
      FineWiki Simple x4, Wiki-to-RCQA (Wikipedia passages followed by questions and answers) x2, Nemotron synthetic QA capped at 2M (~1B);
      a 150M model only keeps facts it meets many times, so the full Wikipedia x3 of the 350M recipe (13B tokens, mostly long tail) is
      replaced by the ~165K core articles seen 4 times plus the same facts restated plainly and as Q&A
    synthetic textbooks 19%: Cosmopedia v2 capped at 7M documents (~5B; supersedes v1 stanford/openstax/khan), v1 wikihow x3 (the register
      of assistant answers), openstax x2, khanacademy x4
    modern fiction 17% (the 350M-2 recipes lost LAMBADA / novel completion at 12%): BookCorpus x2, Cosmopedia stories capped at 1.5M x1,
      WritingPrompts x3
  fine-tuning: the andres-350M-2-fp8v3 recipe scaled for the smaller model (long-form at a lighter dose, competition math dropped):
    smol-smoltalk and the small human-written sets x2, Capybara x2, Opus WritingPrompts x2, SmolTalk magpie-ultra capped at 100k x1,
    UltraChat 200k x0.5, GSM8K x3, MetaMathQA capped at 100k x3; passes in options-tune.json
  preference optimization: the andres-350M-2-fp8v3d configuration (anti-elaboration pairs + MetaMath pairs so worked derivations survive):
    OffsetBias, OpenHermes misconceptions, TruthfulQA pairs, truthy-dpo, MetaMath DPO capped at 8000; passes in options-optimize.json""")

banner("[1/3] Pretraining Datasets (Training)")
# GPT-2 tokens per set (registry estimates): fineweb_edu ~10B, dclm_edu ~2B at 1.3M kept pages (~1.5K tokens each), finewiki_core ~0.94B,
# finewiki_simple ~0.19B, wiki_to_rcqa ~1.1B (all of part 1), nemotron_synth_qa ~1B at 2M, cosmopedia_v2 ~5B at 7M, wikihow ~0.19B,
# openstax ~0.13B, khan ~0.02B, bookcorpus ~1.63B, cosmopedia_stories ~1.3B at 1.5M, writingprompts ~0.21B
run("--dataset fineweb_edu finewiki_core finewiki_simple wiki_to_rcqa cosmopedia_wikihow cosmopedia_openstax cosmopedia_khan bookcorpus writingprompts")
run("--dataset dclm_edu --limit 1300000")
run("--dataset nemotron_synth_qa --limit 2000000")
run("--dataset cosmopedia_v2 --limit 7000000")
run("--dataset cosmopedia_stories --limit 1500000")

banner("[2/3] Fine-Tuning Datasets (Tuning)")
run("--dataset capybara dolly everyday_conversations gsm8k no_robots oasst2 opus_writingprompts smol_smoltalk ultrachat_200k")
run("--dataset smoltalk_magpie_ultra --limit 100000")
run("--dataset metamath_qa --limit 100000")

banner("[3/3] Optimization Datasets (Optimizing)")
run("--dataset offsetbias_dpo openhermes_misconception_dpo truthfulqa_dpo truthy_dpo")
run("--dataset metamath_dpo --limit 8000")

banner(f"[SUCCESS] All datasets for {MODEL} downloaded!")
