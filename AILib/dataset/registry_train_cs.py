import sys
from pathlib import Path
from typing import Any, Dict

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dataset.cleanup import clean_standard_entry


REGISTRY_TRAIN_CS: Dict[str, Dict[str, Any]] = {
    # --------------------------------------------------------------------------
    # 8. Computer Science Code Foundations (Pretraining)
    # --------------------------------------------------------------------------
    "stack_smol_python": {
        "category": "Computer Science",
        "sub_category": "Computer Science",
        "hf_path": "bigcode/the-stack-smol",
        "data_dir": "data/python",
        "split": "train",
        "extracted_size": "~1.2 GB",
        "item_count": "~300M tokens",
        "description": "Curated open-source Python code repositories from The Stack Smol for code syntax and scripting pretraining.",
        "cleaner": clean_standard_entry,
    },
    "stack_smol_xl": {
        "category": "Computer Science",
        "sub_category": "Computer Science",
        "hf_path": "bigcode/the-stack-smol-xl",
        "split": "train",
        "extracted_size": "~10 GB",
        "item_count": "~2.5B tokens",
        "description": "Multi-language open-source code corpus spanning 87 programming languages for comprehensive code pretraining.",
        "cleaner": clean_standard_entry,
    },
}
