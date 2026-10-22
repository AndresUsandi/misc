import sys
from pathlib import Path
from typing import Any, Dict

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dataset.cleanup import clean_chatml_entry


REGISTRY_TUNE_CS: Dict[str, Dict[str, Any]] = {
    # --------------------------------------------------------------------------
    # 5. Computer Science Coding (Domain SFT)
    # --------------------------------------------------------------------------
    "code_alpaca_20k": {
        "category": "Computer Science (obsolete)",
        "sub_category": "",
        "hf_path": "sahil2801/CodeAlpaca-20k",
        "split": "train",
        "extracted_size": "~15 MB",
        "item_count": "4.0M tokens (estimate)",
        "description": "Instruction dataset for code generation, writing small utility scripts, helper functions, and basic apps.",
        "cleaner": clean_chatml_entry,
    },
    "python_instructions_18k": {
        "category": "Computer Science",
        "sub_category": "",
        "hf_path": "iamtarun/python_code_instructions_18k_alpaca",
        "split": "train",
        "extracted_size": "~14 MB",
        "item_count": "3.7M tokens (estimate)",
        "description": "Clean Python-specific instruction dataset focusing on standard library usage, algorithms, and CLI scripts.",
        "cleaner": clean_chatml_entry,
    },
    "mbpp": {
        "category": "Computer Science",
        "sub_category": "",
        "hf_path": "Muennighoff/mbpp",
        "hf_name": "sanitized",
        "split": "train",
        "extracted_size": "~2 MB",
        "item_count": "500,000 tokens (estimate)",
        "description": "Mostly Basic Python Problems: self-contained programming challenges with unit test verification.",
        "cleaner": clean_chatml_entry,
    },
    "code_feedback_156k": {
        "category": "Computer Science",
        "sub_category": "",
        "hf_path": "m-a-p/CodeFeedback-Filtered-Instruction",
        "split": "train",
        "extracted_size": "~180 MB",
        "item_count": "45M tokens (estimate)",
        "description": "Diverse multi-turn coding dialogues covering debugging, refactoring, code explanation, and completion.",
        "cleaner": clean_chatml_entry,
    },
    "evol_code_80k": {
        "category": "Computer Science",
        "sub_category": "",
        "hf_path": "nickrosh/Evol-Instruct-Code-80k-v1",
        "split": "train",
        "extracted_size": "~110 MB",
        "item_count": "27.5M tokens (estimate)",
        "description": "WizardCoder dataset of complex programming instructions systematically evolved for complexity and depth.",
        "cleaner": clean_chatml_entry,
    },
    "taco_algorithms": {
        "category": "Computer Science",
        "sub_category": "",
        "hf_path": "BAAI/TACO",
        "split": "train",
        "extracted_size": "~250 MB",
        "item_count": "62.5M tokens (estimate)",
        "description": "Topics in Algorithm & Competitive Optimization: algorithmic challenges from LeetCode, Codeforces, and AtCoder.",
        "cleaner": clean_chatml_entry,
    },
    "magicoder_75k": {
        "category": "Computer Science",
        "sub_category": "",
        "hf_path": "ise-uiuc/Magicoder-OSS-Instruct-75K",
        "split": "train",
        "extracted_size": "~95 MB",
        "item_count": "24M tokens (estimate)",
        "description": "High-signal code generation dataset grounded on real-world open-source code and API documentation.",
        "cleaner": clean_chatml_entry,
    },
}
