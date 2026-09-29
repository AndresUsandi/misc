# Copyright (c) Sebastian Raschka under Apache License 2.0 (see LICENSE.txt).
# Response format and quality validators for model evaluation tests.

import re
from typing import List, Tuple


def validate_format_quality(prompt: str, response: str) -> Tuple[bool, List[str]]:
    """
    Validates format quality and non-degeneracy of model response without judging factual truth:
    - Non-empty and reasonable minimum length.
    - Zero special token / template delimiter leakage.
    - Anti-degeneracy / repetition loops (distinct n-grams & consecutive sentence repeats).
    - Encoding sanity (no Unicode replacement characters, printable text).
    """
    errors: List[str] = []
    stripped = response.strip()

    # 1. Non-empty and minimum length check
    if len(stripped) < 10 or len(stripped.split()) < 3:
        errors.append(f"Response too short or empty ({len(stripped)} chars, {len(stripped.split())} words).")

    # 2. Special token leakage check
    forbidden_tokens = ["<|im_start|>", "<|im_end|>", "<|user|>", "<|assistant|>", "<|endoftext|>"]
    for tok in forbidden_tokens:
        if tok in response:
            errors.append(f"Leaked special token delimiter: '{tok}'")

    # 3. Repetition loop / degeneracy check
    words = re.findall(r"\b\w+\b", stripped.lower())
    if len(words) >= 15:
        tri_grams = [tuple(words[i:i + 3]) for i in range(len(words) - 2)]
        distinct_tri = set(tri_grams)
        distinct_ratio = len(distinct_tri) / len(tri_grams) if tri_grams else 1.0
        if distinct_ratio < 0.40:
            errors.append(f"Degenerate repetition loop detected (distinct 3-gram ratio: {distinct_ratio:.2f} < 0.40).")

    # Consecutive identical sentence check
    sentences = [s.strip() for s in re.split(r"[.!?\n]+", stripped) if len(s.strip()) > 15]
    for i in range(len(sentences) - 1):
        if sentences[i].lower() == sentences[i + 1].lower():
            errors.append(f"Consecutive duplicate sentence detected: '{sentences[i]}'")
            break

    # 4. Encoding sanity
    if "\ufffd" in response:
        errors.append("Contains Unicode replacement character (\\ufffd).")

    printable_count = sum(1 for c in response if c.isprintable() or c in "\n\r\t")
    if len(response) > 0 and (printable_count / len(response)) < 0.95:
        errors.append("Unacceptable ratio of non-printable or corrupt characters.")

    return len(errors) == 0, errors
