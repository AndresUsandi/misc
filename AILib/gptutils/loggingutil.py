import sys
import time
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional, Union

if TYPE_CHECKING:  # argsutil imports consoleutils -> this module, so only the type checker sees the import
    from argsutil import ModelArgs

_log_file_path: Optional[Path] = None
_at_start_of_line: bool = True


def set_log_file(log_path: Optional[Union[str, Path]]) -> None:
    """Sets the destination log file path for subsequent print statements."""
    global _log_file_path
    if log_path is None:
        _log_file_path = None
        return
    p = Path(log_path)
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        _log_file_path = p
    except Exception:
        _log_file_path = p


def get_log_file() -> Optional[Path]:
    """Returns the current destination log file path, if any."""
    return _log_file_path


def configure_model_logging(args: "ModelArgs") -> Path:
    """
    Configures file logging to write all output to:
      [models_base_dir]/[model_name]/log.txt
    Creates parent directories if they don't exist.
    """
    clean_name = str(args.model_name).split(":")[0].strip()
    log_file = Path(args.models_base_dir) / clean_name / "log.txt"
    set_log_file(log_file)
    return log_file


def get_active_log_file() -> Optional[Path]:
    """
    Returns active log file. If not explicitly set via set_log_file() or configure_model_logging(),
    attempts to infer model_name and models_base_dir from sys.argv.
    """
    global _log_file_path
    if _log_file_path is not None:
        return _log_file_path

    try:
        args = sys.argv
        model_name = None
        base_dir = "bin"
        for i, arg in enumerate(args):
            if arg == "--model_name" and i + 1 < len(args):
                model_name = args[i + 1]
            elif arg.startswith("--model_name="):
                model_name = arg.split("=", 1)[1]
            elif arg in ("--models_base_dir", "--base_dir", "--models_dir") and i + 1 < len(args):
                base_dir = args[i + 1]
            elif arg.startswith(("--models_base_dir=", "--base_dir=", "--models_dir=")):
                base_dir = arg.split("=", 1)[1]

        if model_name:
            clean_name = str(model_name).split(":")[0].strip()
            log_file = Path(base_dir) / clean_name / "log.txt"
            log_file.parent.mkdir(parents=True, exist_ok=True)
            _log_file_path = log_file
            return _log_file_path
    except Exception:
        pass

    return None


def write_to_log(text: str) -> None:
    log_file = get_active_log_file()
    if log_file is None:
        return
    try:
        with open(log_file, "a", encoding="utf-8", errors="replace") as f:
            f.write(text)
    except Exception:
        pass

