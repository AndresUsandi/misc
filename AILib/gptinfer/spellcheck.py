# Copyright (c) Sebastian Raschka under Apache License 2.0 (see LICENSE.txt).
# SymSpell-based autocorrection and prompt cleaning utilities.

import inspect
from pathlib import Path
import re
from typing import Any, Dict, Optional, Tuple

from symspellpy import SymSpell, Verbosity


def init_spell_checker() -> Optional[SymSpell]:
    """Initializes and returns a SymSpell instance with frequency dictionaries loaded."""
    sym_dir = Path(inspect.getfile(SymSpell)).parent
    dict_path = sym_dir / "frequency_dictionary_en_82_765.txt"
    bigram_path = sym_dir / "frequency_bigramdictionary_en_243_342.txt"
    if not dict_path.exists():
        return None
    sym = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)
    sym.load_dictionary(str(dict_path), term_index=0, count_index=1)
    if bigram_path.exists():
        sym.load_bigram_dictionary(str(bigram_path), term_index=0, count_index=2)
    return sym


def autocorrect_prompt(text: str, sym_spell: Any) -> Tuple[str, Dict[str, str]]:
    """
    Cleans up user input prompt by correcting misspelled words using SymSpell.
    Returns (cleaned_text, dict_of_corrections).
    """
    if not sym_spell:
        return text, {}

    corrections: Dict[str, str] = {}

    def replace_word(match: re.Match) -> str:
        orig = match.group(0)
        low = orig.lower()
        if len(low) <= 1 or low in sym_spell.words:
            return orig
        suggestions = sym_spell.lookup(low, Verbosity.CLOSEST, max_edit_distance=2)
        if suggestions:
            best = suggestions[0].term
            if best != low:
                if orig.istitle():
                    best = best.capitalize()
                elif orig.isupper():
                    best = best.upper()
                corrections[orig] = best
                return best
        return orig

    cleaned = re.sub(r"\b[a-zA-Z]+\b", replace_word, text)
    return cleaned, corrections
