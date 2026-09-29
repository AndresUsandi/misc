import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dataset.registry_train import (
    REGISTRY_TRAIN,
    REGISTRY_TRAIN_CORE,
    REGISTRY_TRAIN_SCI,
    REGISTRY_TRAIN_ENG,
    REGISTRY_TRAIN_MATH,
    REGISTRY_TRAIN_CS,
)
from dataset.registry_tune import (
    REGISTRY_TUNE,
    REGISTRY_TUNE_CORE,
    REGISTRY_TUNE_SCI,
    REGISTRY_TUNE_ENG,
    REGISTRY_TUNE_MATH,
    REGISTRY_TUNE_CS,
)
from dataset.registry_optimize import REGISTRY_OPTIMIZE
from gptio.pathutil import STAGE_TRAIN, STAGE_TUNE, STAGE_OPTIMIZE

CAT_CORE = "core"
CAT_MATH = "math"
CAT_CS = "cs"
CAT_SCI = "sci"
CAT_ENG = "eng"

VALID_CATEGORIES: List[str] = [CAT_CORE, CAT_MATH, CAT_CS, CAT_SCI, CAT_ENG]


DATASET_REGISTRY: Dict[str, Dict[str, Dict[str, Any]]] = {
    STAGE_TRAIN: REGISTRY_TRAIN,
    STAGE_TUNE: REGISTRY_TUNE,
    STAGE_OPTIMIZE: REGISTRY_OPTIMIZE,
}


def get_dataset_category(dataset_key: str) -> Optional[str]:
    """
    Returns the category identifier ("core", "math", "cs", "sci", "eng")
    for a given dataset key, or None if not found or uncategorized.
    """
    k = dataset_key.lower().strip()
    if k in REGISTRY_TRAIN_CORE or k in REGISTRY_TUNE_CORE or k in REGISTRY_OPTIMIZE:
        return CAT_CORE
    if k in REGISTRY_TRAIN_MATH or k in REGISTRY_TUNE_MATH:
        return CAT_MATH
    if k in REGISTRY_TRAIN_CS or k in REGISTRY_TUNE_CS:
        return CAT_CS
    if k in REGISTRY_TRAIN_SCI or k in REGISTRY_TUNE_SCI:
        return CAT_SCI
    if k in REGISTRY_TRAIN_ENG or k in REGISTRY_TUNE_ENG:
        return CAT_ENG
    return None



def get_all_dataset_keys() -> List[str]:
    """Returns a list of all registered dataset keys across all purpose buckets."""
    keys: List[str] = []
    for bucket in DATASET_REGISTRY.values():
        keys.extend(bucket.keys())
    return keys


def find_dataset_entry(dataset_key: str, purpose: Optional[str] = None) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
    """
    Searches for a dataset key across all purpose buckets in DATASET_REGISTRY.
    If `purpose` is provided and the dataset exists in that bucket, returns it first.
    Returns (purpose_bucket, info_dict) or (None, None) if not found.
    """
    k = dataset_key.lower().strip()
    if purpose and purpose in DATASET_REGISTRY:
        if k in DATASET_REGISTRY[purpose]:
            return purpose, DATASET_REGISTRY[purpose][k]
    for p, entries in DATASET_REGISTRY.items():
        if k in entries:
            return p, entries[k]
    return None, None

