# Copyright (c) Sebastian Raschka under Apache License 2.0 (see LICENSE.txt).
# Response format and quality validators for model evaluation tests.

from collections import Counter
import re
from typing import Any, Dict, List, Optional, Tuple

# Turn spec keys (see testcore.normalize_spec) and categories.
SPEC_PROMPT = "prompt"
SPEC_CATEGORY = "category"
SPEC_MUST_ANY = "must_any"      # at least one of these strings must appear (case-insensitive)
SPEC_MUST_ALL = "must_all"      # every one of these strings must appear
SPEC_MUST_NOT = "must_not"      # none of these strings may appear (known confusions / hallucinations)
SPEC_REGEX = "regex"            # optional regex that must match somewhere in the response
SPEC_FACTS = "facts"            # reference facts: ground truth for the NLI verifier and the LLM judge
SPEC_RUBRIC = "rubric"          # extra grading guidance for the LLM judge
CATEGORY_FACTUAL = "factual"
CATEGORY_CREATIVE = "creative"

_STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "of", "to", "in", "on", "at", "for", "with", "by", "from", "is", "are",
    "was", "were", "be", "been", "it", "its", "this", "that", "he", "she", "they", "we", "you", "i", "his", "her",
    "their", "as", "not", "had", "has", "have", "who", "what", "when", "where", "which", "how", "did", "do", "does",
}
_FORBIDDEN_TOKENS = ["<|im_start|>", "<|im_end|>", "<|user|>", "<|assistant|>", "<|endoftext|>", "<|im", "<|end"]
_ROLE_LEAK_RE = re.compile(r"(^|\n)\s*(User|Assistant|Human|AI|System)\s*:|###\s*(Instruction|Response|Input)", re.IGNORECASE)
_CREATIVE_RE = re.compile(r"\b(story|poem|essay|feel|imagine|write|opinion)\b")
_NEEDS_DATE_RE = re.compile(r"\bwhen\b|\bwhat (year|date|time)\b")
_NEEDS_PROPER_NOUN_RE = re.compile(r"\bwho\b|\bwhere\b|\b(what|which)\b.*\b(country|city|capital|name|river|planet|company)\b")
_NEEDS_STORY_RE = re.compile(r"\b(write|tell|compose)\b.*\b(story|essay)\b")
_DATE_RE = re.compile(r"\b\d{3,4}\b|\b(january|february|march|april|may|june|july|august|september|october|november|december)\b", re.IGNORECASE)
_PROPER_NOUN_RE = re.compile(r"(?<=[^.!?\n] )[A-Z][a-z]+")


def validate_format_quality(prompt: str, response: str, stats: Optional[Dict[str, Any]] = None, spell_checker: Any = None) -> Tuple[bool, List[str], List[str]]:
    """
    Validates format quality and non-degeneracy of model response without judging factual truth.
    Returns (is_valid, errors, warnings): errors fail the check, warnings are reported only.
    Checks: length bounds, delimiter/role leakage, truncation, repetition, encoding, language,
    answer-type sanity derived from the prompt, prompt echo, balance, and misspelling rate.
    """
    errors: List[str] = []
    warnings: List[str] = []
    stripped = response.strip()
    words = re.findall(r"\b\w+\b", stripped.lower())
    p = prompt.lower()
    is_creative = bool(_CREATIVE_RE.search(p))

    # 1. Non-empty and minimum length check
    if len(stripped) < 10 or len(words) < 3:
        errors.append(f"Response too short or empty ({len(stripped)} chars, {len(words)} words).")

    # 2. Special token / role leakage check
    for tok in _FORBIDDEN_TOKENS:
        if tok in response:
            errors.append(f"Leaked special token delimiter: '{tok}'")
    leak = _ROLE_LEAK_RE.search(response)
    if leak:
        errors.append(f"Role/template leakage (fake next turn): '{leak.group(0).strip()}'")

    # 3. Truncation / no-EOS check
    if stats and stats.get("tokens", 0) >= stats.get("allowed_new_tokens", float("inf")):
        errors.append(f"Filled the context window ({stats['tokens']} tokens) without emitting EOS (truncated).")
    if stripped and stripped[-1] not in ".!?\"')\u201d\u2019":
        warnings.append(f"Does not end with terminal punctuation: '...{stripped[-20:]}'")

    # 4. Repetition loop / degeneracy check
    if len(words) >= 15:
        tri_grams = [tuple(words[i:i + 3]) for i in range(len(words) - 2)]
        distinct_ratio = len(set(tri_grams)) / len(tri_grams)
        if distinct_ratio < 0.50:
            errors.append(f"Degenerate repetition loop detected (distinct 3-gram ratio: {distinct_ratio:.2f} < 0.50).")
    sentences = [s.strip().lower() for s in re.split(r"[.!?\n]+", stripped) if len(s.strip()) > 15]
    for sent, count in Counter(sentences).items():
        if count > 1:
            errors.append(f"Duplicate sentence detected ({count}x): '{sent}'")
            break

    # 5. Encoding sanity
    if "\ufffd" in response:
        errors.append("Contains Unicode replacement character (\\ufffd).")
    printable_count = sum(1 for c in response if c.isprintable() or c in "\n\r\t")
    if len(response) > 0 and (printable_count / len(response)) < 0.95:
        errors.append("Unacceptable ratio of non-printable or corrupt characters.")

    # 6. Language check (English stopword ratio)
    if len(words) >= 8:
        stop_ratio = sum(w in _STOPWORDS for w in words) / len(words)
        if stop_ratio < 0.2:
            errors.append(f"Not English or token soup (stopword ratio {stop_ratio:.2f} < 0.20).")

    # 7. Prompt echo check (content words only)
    prompt_words = set(re.findall(r"\b\w+\b", p))
    content_words = [w for w in words if w not in _STOPWORDS]
    if content_words and sum(w in prompt_words for w in content_words) / len(content_words) >= 0.9:
        errors.append("Response merely echoes the prompt.")

    # 8. Answer-type sanity derived from the prompt
    if _NEEDS_DATE_RE.search(p) and not _DATE_RE.search(stripped):
        errors.append("'When' question answered without any date/year.")
    if _NEEDS_PROPER_NOUN_RE.search(p) and not _PROPER_NOUN_RE.search(stripped):
        errors.append("Who/where/which-name question answered without any proper noun.")
    if _NEEDS_STORY_RE.search(p):
        if len(words) < 100:
            errors.append(f"Story/essay too short ({len(words)} words < 100).")
        if len(re.split(r"\n\s*\n", stripped)) < 2:
            warnings.append("Story/essay is a single paragraph.")
    elif not is_creative:
        if len(words) > 300:
            errors.append(f"Overly verbose answer to a factual question ({len(words)} words > 300).")
        elif len(words) > 150:
            warnings.append(f"Verbose answer to a factual question ({len(words)} words > 150).")

    # 9. Balance / capitalization checks
    if stripped.count('"') % 2:
        warnings.append("Unmatched double quote.")
    if stripped.count("(") != stripped.count(")"):
        warnings.append("Unbalanced parentheses.")
    first_alpha = re.search(r"[A-Za-z]", stripped)
    if first_alpha and first_alpha.group().islower():
        warnings.append("Response does not start with a capital letter.")

    # 10. Misspelling rate (lowercase words only, so proper nouns / invented names are ignored)
    if spell_checker:
        lower_words = [w for w in re.findall(r"\b[a-z]+\b", stripped) if len(w) > 2]
        misspelled = [w for w in lower_words if w not in spell_checker.words]
        if lower_words and len(misspelled) / len(lower_words) > 0.03:
            warnings.append(f"Misspelling rate {len(misspelled) / len(lower_words):.1%} > 3%: {misspelled[:5]}")

    return len(errors) == 0, errors, warnings


def validate_content_spec(spec: Dict[str, Any], response: str) -> List[str]:
    """Tier A content check: deterministic must/must-not/regex rules from the turn spec. Returns error strings."""
    errors: List[str] = []
    low = response.lower()
    if spec.get(SPEC_MUST_ANY) and not any(s.lower() in low for s in spec[SPEC_MUST_ANY]):
        errors.append(f"Expected answer not found; none of {spec[SPEC_MUST_ANY]} present.")
    for s in spec.get(SPEC_MUST_ALL, []):
        if s.lower() not in low:
            errors.append(f"Required term missing: '{s}'")
    for s in spec.get(SPEC_MUST_NOT, []):
        if s.lower() in low:
            errors.append(f"Forbidden term present (known confusion): '{s}'")
    if spec.get(SPEC_REGEX) and not re.search(spec[SPEC_REGEX], response, re.IGNORECASE):
        errors.append(f"Response does not match required pattern: {spec[SPEC_REGEX]}")
    return errors
