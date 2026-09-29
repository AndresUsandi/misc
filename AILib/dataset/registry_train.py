import sys
from pathlib import Path
from typing import Any, Dict

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dataset.registry_train_core import REGISTRY_TRAIN_CORE
from dataset.registry_train_sci import REGISTRY_TRAIN_SCI
from dataset.registry_train_eng import REGISTRY_TRAIN_ENG
from dataset.registry_train_math import REGISTRY_TRAIN_MATH
from dataset.registry_train_cs import REGISTRY_TRAIN_CS


REGISTRY_TRAIN: Dict[str, Dict[str, Any]] = {
    **REGISTRY_TRAIN_CORE,
    **REGISTRY_TRAIN_SCI,
    **REGISTRY_TRAIN_ENG,
    **REGISTRY_TRAIN_MATH,
    **REGISTRY_TRAIN_CS,
}
