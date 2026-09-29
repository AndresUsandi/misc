# Copyright (c) Sebastian Raschka under Apache License 2.0 (see LICENSE.txt).
# General text file I/O utility for reading encoded text.

from pathlib import Path
from typing import Union


def read_text_file(file_path: Union[str, Path]) -> str:
    """Reads a text file with UTF-8 encoding (falling back to character replacement on decode errors)."""
    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()
