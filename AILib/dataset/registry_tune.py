import sys
from pathlib import Path
from typing import Any, Dict

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dataset.registry_tune_core import REGISTRY_TUNE_CORE
from dataset.registry_tune_sci import REGISTRY_TUNE_SCI
from dataset.registry_tune_eng import REGISTRY_TUNE_ENG
from dataset.registry_tune_math import REGISTRY_TUNE_MATH
from dataset.registry_tune_cs import REGISTRY_TUNE_CS


REGISTRY_TUNE: Dict[str, Dict[str, Any]] = {
    **REGISTRY_TUNE_CORE,
    **REGISTRY_TUNE_SCI,
    **REGISTRY_TUNE_ENG,
    **REGISTRY_TUNE_MATH,
    **REGISTRY_TUNE_CS,
}
