import sys
from pathlib import Path
from typing import Any, Dict

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dataset.cleanup import clean_chatml_entry


REGISTRY_TUNE_MATH: Dict[str, Dict[str, Any]] = {
    # --------------------------------------------------------------------------
    # 4. Mathematics Reasoning (Domain SFT)
    # --------------------------------------------------------------------------
    "metamath_qa": {
        "category": "Mathematics",
        "sub_category": "",
        "hf_path": "meta-math/MetaMathQA",
        "split": "train",
        "extracted_size": "~650 MB",
        "item_count": "~160M tokens (estimated)",
        "description": "GSM8K and MATH augmented through forward, backward, and re-phrased Chain-of-Thought solutions.",
        "cleaner": clean_chatml_entry,
    },
    "gsm8k": {
        "category": "Mathematics",
        "sub_category": "",
        "hf_path": "openai/gsm8k",
        "hf_name": "main",
        "split": "train",
        "extracted_size": "~12 MB",
        "item_count": "~3.0M tokens (estimated)",
        "description": "High-quality grade-school multi-step arithmetic reasoning word problems with step-by-step solutions.",
        "cleaner": clean_chatml_entry,
    },
    "math_olympiad": {
        "category": "Mathematics",
        "sub_category": "",
        "hf_path": "lighteval/MATH",
        "split": "train",
        "extracted_size": "~15 MB",
        "item_count": "~3.8M tokens (estimated)",
        "description": "High-school and competition Olympiad mathematics problems across 7 subject categories.",
        "cleaner": clean_chatml_entry,
    },
    "numinamath_cot": {
        "category": "Mathematics",
        "sub_category": "",
        "hf_path": "AI-MO/NuminaMath-CoT",
        "split": "train",
        "extracted_size": "~1.2 GB",
        "item_count": "~300M tokens (estimated)",
        "description": "Massive competition and academic math dataset with step-by-step Chain-of-Thought proofs and derivations.",
        "cleaner": clean_chatml_entry,
    },
    "math_instruct": {
        "category": "Mathematics",
        "sub_category": "",
        "hf_path": "TIGER-Lab/MathInstruct",
        "split": "train",
        "extracted_size": "~380 MB",
        "item_count": "~95M tokens (estimated)",
        "description": "Curated mathematical instruction-following pairs across arithmetic, algebra, calculus, and discrete mathematics.",
        "cleaner": clean_chatml_entry,
    },
    "camel_math": {
        "category": "Mathematics",
        "sub_category": "",
        "hf_path": "camel-ai/math",
        "split": "train",
        "extracted_size": "~90 MB",
        "item_count": "~22.5M tokens (estimated)",
        "description": "University-level mathematical problem/solution pairs covering calculus, linear algebra, and statistics.",
        "cleaner": clean_chatml_entry,
    },
}
