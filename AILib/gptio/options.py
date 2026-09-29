# Copyright (c) Sebastian Raschka under Apache License 2.0 (see LICENSE.txt).
# Options configuration overrides loader for GPT models.

import json
from pathlib import Path
import sys
from typing import TYPE_CHECKING, Optional, Union

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from gptutils.consoleutils import print
from gptio.pathutil import resolve_path, TARGET_OPTIONS

if TYPE_CHECKING:  # argsutil imports this module, so only the type checker sees the import
    from argsutil import ModelArgs


def apply_options_overrides(
    args: "ModelArgs",
    stage: Optional[str] = None,
    options_path: Optional[Union[str, Path]] = None,
) -> "ModelArgs":
    """Overrides args attributes from the model's .options-<stage>.json file, excluding model_name and models_base_dir."""
    if options_path is None and args.model_name is not None and stage:
        options_path = resolve_path(args.model_name, target=TARGET_OPTIONS, stage=stage, models_dir=args.models_base_dir)

    if options_path is None or not Path(options_path).exists():
        return args
    p = Path(options_path)
    try:
        with open(p, "r", encoding="utf-8") as f:
            options = json.load(f)
    except Exception as e:
        print(f"[Options Warning] Failed to parse options file '{p}': {e}")
        return args

    if not isinstance(options, dict):
        print(f"[Options Warning] Options file '{p}' must contain a JSON dictionary, got {type(options).__name__}.")
        return args

    protected_keys = {"model_name", "models_base_dir", "models_root_dir", "models_dir"}
    overridden = []
    for key, val in options.items():
        if key in protected_keys:
            continue
        if key == "precision" and isinstance(val, str):
            val = val.lower().strip()
        setattr(args, key, val)
        overridden.append(f"{key}={val}")

    if overridden:
        print(f"[Options] Overrode {len(overridden)} parameter(s) from '{p.name}': {', '.join(overridden)}")
    return args
