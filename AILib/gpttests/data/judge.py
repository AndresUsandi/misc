# Copyright (c) Sebastian Raschka under Apache License 2.0 (see LICENSE.txt).
# Tier C content verifier: LLM-as-a-judge (Gemma 4 E4B GGUF via llama-cpp-python) with JSON-schema constrained verdicts.

import atexit
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List

import torch  # must be imported before llama_cpp: the prebuilt CUDA wheel resolves cublas64_13.dll/cudart64_13.dll from torch\lib
from llama_cpp import Llama, LLAMA_SPLIT_MODE_NONE

from gpttests.data.modelrefs import JUDGE_DIR, JUDGE_FILENAME
from gpttests.data.validators import CATEGORY_CREATIVE, SPEC_CATEGORY, SPEC_FACTS, SPEC_RUBRIC

JUDGE_CACHE_FILE = JUDGE_DIR / "judge_cache.json"
JUDGE_N_CTX = 8192
JUDGE_SCHEMA = {
    "type": "object",
    "properties": {
        "pass": {"type": "boolean"},
        "score": {"type": "integer", "minimum": 1, "maximum": 5},
        "issues": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["pass", "score", "issues"],
}
_SYSTEM = (
    "You are a strict, impartial grader of answers written by a small language model. Grade ONLY the final response. "
    "Trust the REFERENCE FACTS over your own memory. Equivalent wording is NOT an error (British/English, USA/United States, "
    "20 July 1969/July 20, 1969); flag only claims that are actually false, invented, or contradict the facts. Reply with JSON only."
)
_RULES = {
    CATEGORY_CREATIVE: (
        "Creative task. pass=true if the response fulfils the request, is coherent and internally consistent "
        "(names, places and events do not change), stays on topic, does not restart or repeat itself, and is written in fluent English. "
        "Clichés, simple plots, weak prose or an abrupt ending are NOT failures (lower the score instead); fail only for incoherence, "
        "contradictions, off-topic content, restarts, repetition loops, or ignoring the request."
    ),
    "default": (
        "Factual question. pass=true only if the response (a) directly answers the question, (b) every factual claim in it is true and "
        "consistent with the REFERENCE FACTS, and (c) it contains no invented names, dates, titles or events. "
        "A single false statement means pass=false even when the core answer is right."
    ),
}


class LlmJudge:
    """Loads the judge GGUF entirely on one GPU and grades (conversation, response) pairs; verdicts are cached on disk by content hash."""

    def __init__(self, gpu_index: int, model_path: Path = JUDGE_DIR / JUDGE_FILENAME):
        self.model_path = model_path
        if not model_path.exists():
            raise SystemExit(f"[judge] Missing {model_path}. Run `python gpttests\\download_judge.py` once to install llama-cpp-python and download the judge model.")
        self.llm = Llama(model_path=str(model_path), n_gpu_layers=-1, main_gpu=gpu_index, split_mode=LLAMA_SPLIT_MODE_NONE, n_ctx=JUDGE_N_CTX, seed=0, verbose=False)
        atexit.register(self.llm.close)  # free the model before module teardown; otherwise llama_cpp's __del__ raises at interpreter exit
        self.cache: Dict[str, Any] = json.loads(JUDGE_CACHE_FILE.read_text(encoding="utf-8")) if JUDGE_CACHE_FILE.exists() else {}

    def grade(self, history: List[Dict[str, str]], prompt: str, response: str, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Returns {'pass': bool, 'score': 1-5, 'issues': [str]} for the response to prompt given the prior conversation history."""
        if not response.strip():  # the LLM judge grades an empty response as a 5/5 pass; nothing to grade
            return {"pass": False, "score": 1, "issues": ["empty response"]}
        facts = spec.get(SPEC_FACTS) or []
        parts = [f"CATEGORY: {spec.get(SPEC_CATEGORY)}"]
        if history:
            parts.append("CONVERSATION SO FAR:\n" + "\n".join(f"{m['role']}: {m['content']}" for m in history))
        parts.append(f"QUESTION: {prompt}")
        parts.append(f"RESPONSE TO GRADE:\n{response}")
        if facts:
            parts.append("REFERENCE FACTS:\n" + "\n".join(f"- {f}" for f in facts))
        parts.append("GRADING RULES: " + _RULES.get(spec.get(SPEC_CATEGORY), _RULES["default"]))
        if spec.get(SPEC_RUBRIC):
            parts.append(f"TASK-SPECIFIC RUBRIC: {spec[SPEC_RUBRIC]}")
        parts.append('Return JSON: {"pass": true|false, "score": 1-5, "issues": ["one short string per problem found"]}')
        messages = [{"role": "system", "content": _SYSTEM}, {"role": "user", "content": "\n\n".join(parts)}]
        key = hashlib.sha256((self.model_path.name + json.dumps(messages, sort_keys=True)).encode("utf-8")).hexdigest()
        if key not in self.cache:
            out = self.llm.create_chat_completion(messages=messages, temperature=0.0, max_tokens=400, response_format={"type": "json_object", "schema": JUDGE_SCHEMA})
            try:
                verdict = json.loads(out["choices"][0]["message"]["content"])
            except json.JSONDecodeError:  # the issues list ran past max_tokens and the JSON was cut off: retry once with room, then fail the sample explicitly
                out = self.llm.create_chat_completion(messages=messages, temperature=0.0, max_tokens=1500, response_format={"type": "json_object", "schema": JUDGE_SCHEMA})
                try:
                    verdict = json.loads(out["choices"][0]["message"]["content"])
                except json.JSONDecodeError:
                    verdict = {"pass": False, "score": 1, "issues": ["judge reply was not valid JSON (cut off at max_tokens twice)"]}
            self.cache[key] = verdict
            JUDGE_DIR.mkdir(parents=True, exist_ok=True)
            JUDGE_CACHE_FILE.write_text(json.dumps(self.cache, indent=1), encoding="utf-8")
        return self.cache[key]
