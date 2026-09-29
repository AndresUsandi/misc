import sys
from pathlib import Path
from typing import Any, Dict

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dataset.cleanup import clean_standard_entry


REGISTRY_TRAIN_MATH: Dict[str, Dict[str, Any]] = {
    # --------------------------------------------------------------------------
    # 7. Mathematics (Pretraining)
    # --------------------------------------------------------------------------
    "open_web_math": {
        "category": "Mathematics",
        "sub_category": "Mathematics",
        "hf_path": "open-web-math/open-web-math",
        "split": "train",
        "extracted_size": "~28 GB",
        "item_count": "~14.7B tokens",
        "description": "High-quality mathematical web text extracted from arXiv, ProofWiki, MathOverflow, and StackExchange Math.",
        "cleaner": clean_standard_entry,
    },
    "deepmind_math": {
        "category": "Mathematics",
        "sub_category": "Mathematics",
        "hf_path": "deepmind/math_dataset",
        "split": "train",
        "extracted_size": "~2.1 GB",
        "item_count": "~525M tokens (estimated)",
        "description": "Programmatically generated mathematics covering arithmetic, polynomial factorization, calculus, and linear equations.",
        "cleaner": clean_standard_entry,
    },
}
