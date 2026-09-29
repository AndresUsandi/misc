# Copyright (c) Sebastian Raschka under Apache License 2.0 (see LICENSE.txt).
# System and compiler pre-flight validation checks.

import os
from typing import Any, Union
import torch
import torch.nn as nn


def check_torch_compile_working(device: Union[str, torch.device]) -> bool:
    """Safely checks if torch.compile runs on the specified device without crashing."""
    if os.environ.get("TORCH_COMPILE_DISABLE", "0") == "1":
        return False
    if not hasattr(torch, "compile"):
        return False
    try:
        dummy_layer = nn.Linear(4, 4).to(device)
        compiled_dummy = torch.compile(dummy_layer)
        inp = torch.randn(2, 4, device=device)
        _ = compiled_dummy(inp)
        return True
    except Exception:
        return False
