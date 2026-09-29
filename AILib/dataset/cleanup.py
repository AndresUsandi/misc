
import random
import re
from typing import Any, Callable, Dict, Iterator, List, Optional, Tuple

TEXT_START_MARKERS = frozenset((
    "*END*THE SMALL PRINT",
    "*** START OF THE PROJECT GUTENBERG",
    "*** START OF THIS PROJECT GUTENBERG",
    "This etext was prepared by",
    "E-text prepared by",
    "Produced by",
    "Distributed Proofreading Team",
    "Proofreading Team at http://www.pgdp.net",
    "http://gallica.bnf.fr)",
    "      http://archive.org/details/",
    "http://www.pgdp.net",
    "by The Internet Archive)",
    "by The Internet Archive/Canadian Libraries",
    "by The Internet Archive/American Libraries",
    "public domain material from the Internet Archive",
    "Internet Archive)",
    "Internet Archive/Canadian Libraries",
    "Internet Archive/American Libraries",
    "material from the Google Print project",
    "*END THE SMALL PRINT",
    "***START OF THE PROJECT GUTENBERG",
    "This etext was produced by",
    "*** START OF THE COPYRIGHTED",
    "The Project Gutenberg",
    "http://gutenberg.spiegel.de/ erreichbar.",
    "Project Runeberg publishes",
    "Beginning of this Project Gutenberg",
    "Project Gutenberg Online Distributed",
    "Gutenberg Online Distributed",
    "the Project Gutenberg Online Distributed",
    "Project Gutenberg TEI",
    "This eBook was prepared by",
    "http://gutenberg2000.de erreichbar.",
    "This Etext was prepared by",
    "This Project Gutenberg Etext was prepared by",
    "Gutenberg Distributed Proofreaders",
    "Project Gutenberg Distributed Proofreaders",
    "the Project Gutenberg Online Distributed Proofreading Team",
    "**The Project Gutenberg",
    "*SMALL PRINT!",
    "More information about this book is at the top of this file.",
    "tells you about restrictions in how the file may be used.",
    "l'authorization à les utilizer pour preparer ce texte.",
    "of the etext through OCR.",
    "*****These eBooks Were Prepared By Thousands of Volunteers!*****",
    "We need your donations more than ever!",
    " *** START OF THIS PROJECT GUTENBERG",
    "****     SMALL PRINT!",
    '["Small Print" V.',
    '      (http://www.ibiblio.org/gutenberg/',
    'and the Project Gutenberg Online Distributed Proofreading Team',
    'Mary Meehan, and the Project Gutenberg Online Distributed Proofreading',
    '                this Project Gutenberg edition.',
))

TEXT_END_MARKERS = frozenset((
    "*** END OF THE PROJECT GUTENBERG",
    "*** END OF THIS PROJECT GUTENBERG",
    "***END OF THE PROJECT GUTENBERG",
    "End of the Project Gutenberg",
    "End of The Project Gutenberg",
    "Ende dieses Project Gutenberg",
    "by Project Gutenberg",
    "End of Project Gutenberg",
    "End of this Project Gutenberg",
    "Ende dieses Projekt Gutenberg",
    "        ***END OF THE PROJECT GUTENBERG",
    "*** END OF THE COPYRIGHTED",
    "End of this is COPYRIGHTED",
    "Ende dieses Etextes ",
    "Ende dieses Project Gutenberg",
    "**This is a COPYRIGHTED Project Gutenberg Etext, Details Above**",
    "Fin de Project Gutenberg",
    "The Project Gutenberg Etext of ",
    "Ce document fut presente en lecture",
    "Ce document fut présenté en lecture",
    "More information about this book is at the top of this file.",
    "We need your donations more than ever!",
    "END OF PROJECT GUTENBERG",
    " End of the Project Gutenberg",
    " *** END OF THIS PROJECT GUTENBERG",
))

LEGALESE_START_MARKERS = frozenset(("<<THIS ELECTRONIC VERSION OF",))
LEGALESE_END_MARKERS = frozenset(("SERVICE THAT CHARGES FOR DOWNLOAD",))


def strip_gutenberg_headers(text: str) -> str:
    """
    Remove lines that are part of the Project Gutenberg header, footer, or license.
    Ported from Gutenberg cleaning utilities.
    """
    lines = text.splitlines()
    out = []
    i = 0
    footer_found = False
    ignore_section = False

    for line in lines:
        reset = False

        if i <= 600:
            if any(line.startswith(token) for token in TEXT_START_MARKERS):
                reset = True
            if reset:
                out = []
                continue

        if i >= 100:
            if any(line.startswith(token) for token in TEXT_END_MARKERS):
                footer_found = True
            if footer_found:
                break

        if any(line.startswith(token) for token in LEGALESE_START_MARKERS):
            ignore_section = True
            continue
        elif any(line.startswith(token) for token in LEGALESE_END_MARKERS):
            ignore_section = False
            continue

        if not ignore_section:
            out.append(line)
            i += 1

    return "\n".join(out)


def is_english(text: str, threshold: float = 0.9) -> bool:
    """Check if the text consists primarily of English ASCII characters."""
    if not text:
        return False
    ascii_chars = sum(1 for c in text if ord(c) < 128)
    return (ascii_chars / len(text)) > threshold


def clean_text_formatting(text: str) -> str:
    """Replaces multiple blank lines with a single blank line and strips whitespace."""
    return re.sub(r"\n\s*\n", "\n\n", text).strip()


def maybe_lowercase_user_text(text: str, p: float = 0.5) -> str:
    """Randomly lowercases user/input text with probability p (default 50%) for capitalization robustness."""
    if text and random.random() < p:
        return text.lower()
    return text



def clean_gutenberg_entry(item: Dict[str, Any]) -> Optional[str]:
    text = item.get("TEXT") or item.get("text") or ""
    if not text:
        return None
    cleaned = strip_gutenberg_headers(text)
    if not is_english(cleaned):
        return None
    cleaned = clean_text_formatting(cleaned)
    return cleaned if len(cleaned) > 100 else None


def clean_standard_entry(item: Dict[str, Any]) -> Optional[str]:
    text = item.get("text") or item.get("story") or item.get("content") or ""
    if not text or len(text.strip()) < 10:
        return None
    return clean_text_formatting(text)


def clean_wikipedia_entry(item: Dict[str, Any]) -> Optional[str]:
    title = item.get("title") or ""
    text = item.get("text") or item.get("content") or ""
    if not text or len(text.strip()) < 50:
        return None
    cleaned = clean_text_formatting(text)
    if not is_english(cleaned, threshold=0.85):
        return None
    if title and not cleaned.startswith(title):
        cleaned = f"{title}\n\n{cleaned}"
    return cleaned if len(cleaned) > 50 else None





def clean_chatml_entry(item: Dict[str, Any]) -> Optional[str]:
    """Cleans and formats conversational or instruction entries into standard ChatML format (<|im_start|>, <|im_end|>)."""
    # 1. Check messages / conversations / data (list of dicts with role/content)
    messages = None
    for k in ("messages", "conversations", "conversation", "data"):
        val = item.get(k)
        if val is not None:
            messages = val
            break

    if messages is not None and (isinstance(messages, (list, tuple)) or (hasattr(messages, "__iter__") and not isinstance(messages, str))):
        turns = []
        for idx, m in enumerate(messages):
            if isinstance(m, dict):
                if "input" in m and "output" in m:
                    u = str(m.get("input") or "").strip()
                    a = str(m.get("output") or "").strip()
                    if u:
                        turns.append(f"<|im_start|>user\n{maybe_lowercase_user_text(u)}<|im_end|>")
                    if a:
                        turns.append(f"<|im_start|>assistant\n{a}<|im_end|>")
                    continue
                raw_role = str(m.get("role") or m.get("from") or "user").strip().lower()
                role = "user" if raw_role in ("user", "human") else ("assistant" if raw_role in ("assistant", "gpt", "bot", "chatbot") else ("system" if raw_role == "system" else raw_role))
                content = str(m.get("content") or m.get("value") or "").strip()
                if content:
                    if role == "user":
                        content = maybe_lowercase_user_text(content)
                    turns.append(f"<|im_start|>{role}\n{content}<|im_end|>")
            elif isinstance(m, str):
                line_str = m.strip()
                if line_str:
                    role = "user" if idx % 2 == 0 else "assistant"
                    if role == "user":
                        line_str = maybe_lowercase_user_text(line_str)
                    turns.append(f"<|im_start|>{role}\n{line_str}<|im_end|>")
        if len(turns) >= 2:
            return "\n".join(turns)

    # 2. Check utterances / history / dialog / dialogue (list/array of strings)
    dialog_turns = None
    for k in ("utterances", "history", "dialog", "dialogue"):
        val = item.get(k)
        if val is not None:
            dialog_turns = val
            break

    if dialog_turns is not None:
        if isinstance(dialog_turns, (list, tuple)) or hasattr(dialog_turns, "__iter__") and not isinstance(dialog_turns, str):
            turns = []
            for idx, line in enumerate(dialog_turns):
                line_str = str(line).strip()
                if line_str:
                    role = "user" if idx % 2 == 0 else "assistant"
                    if role == "user":
                        line_str = maybe_lowercase_user_text(line_str)
                    turns.append(f"<|im_start|>{role}\n{line_str}<|im_end|>")
            if len(turns) >= 2:
                return "\n".join(turns)
        elif isinstance(dialog_turns, str) and len(dialog_turns.strip()) > 20:
            return clean_text_formatting(dialog_turns)

    # 3. Check instruction / prompt pairs
    instruction = (item.get("instruction") or item.get("question") or item.get("Question") or item.get("prompt") or item.get("problem") or item.get("Problem") or item.get("query") or item.get("message_1") or "").strip()
    input_ctx = (item.get("input") or item.get("context") or item.get("system_prompt") or item.get("support") or "").strip()
    output = (item.get("output") or item.get("response") or item.get("Response") or item.get("completion") or item.get("solution") or item.get("Solution") or item.get("answer") or item.get("Answer") or item.get("correct_answer") or item.get("message_2") or item.get("code") or "").strip()
    if not output and "solutions" in item:
        s = item.get("solutions")
        if isinstance(s, (list, tuple)) and s:
            output = str(s[0]).strip()
        elif isinstance(s, str):
            output = s.strip()

    if instruction and output:
        user_content = f"{instruction}\n\n{input_ctx}" if input_ctx else instruction
        user_content = maybe_lowercase_user_text(user_content)
        return f"<|im_start|>user\n{user_content}<|im_end|>\n<|im_start|>assistant\n{output}<|im_end|>"

    # 4. Fallback to standard text
    text = item.get("text") or item.get("content") or item.get("story") or ""
    if text and len(str(text).strip()) > 20:
        return clean_text_formatting(str(text))
    return None


def clean_llama_entry(item: Dict[str, Any]) -> Optional[str]:
    """Cleans and formats conversational or instruction entries into standard LLaMA-3 format (<|start_header_id|>, <|end_header_id|>, <|eot_id|>)."""
    # 1. Check messages / conversations / data (list of dicts with role/content)
    messages = None
    for k in ("messages", "conversations", "data"):
        val = item.get(k)
        if val is not None:
            messages = val
            break

    if messages is not None:
        turns = []
        for m in messages:
            if isinstance(m, dict):
                raw_role = str(m.get("role") or m.get("from") or "user").strip().lower()
                role = "user" if raw_role in ("user", "human") else ("assistant" if raw_role in ("assistant", "gpt", "bot", "chatbot") else ("system" if raw_role == "system" else raw_role))
                content = str(m.get("content") or m.get("value") or "").strip()
                if content:
                    if role == "user":
                        content = maybe_lowercase_user_text(content)
                    turns.append(f"<|start_header_id|>{role}<|end_header_id|>\n\n{content}<|eot_id|>")
        if len(turns) >= 2:
            return "\n".join(turns)

    # 2. Check utterances / history / dialog / dialogue (list/array of strings)
    dialog_turns = None
    for k in ("utterances", "history", "dialog", "dialogue"):
        val = item.get(k)
        if val is not None:
            dialog_turns = val
            break

    if dialog_turns is not None:
        if isinstance(dialog_turns, (list, tuple)) or hasattr(dialog_turns, "__iter__") and not isinstance(dialog_turns, str):
            turns = []
            for idx, line in enumerate(dialog_turns):
                line_str = str(line).strip()
                if line_str:
                    role = "user" if idx % 2 == 0 else "assistant"
                    if role == "user":
                        line_str = maybe_lowercase_user_text(line_str)
                    turns.append(f"<|start_header_id|>{role}<|end_header_id|>\n\n{line_str}<|eot_id|>")
            if len(turns) >= 2:
                return "\n".join(turns)

    # 3. Check instruction / prompt pairs
    instruction = (item.get("instruction") or item.get("question") or item.get("prompt") or "").strip()
    input_ctx = (item.get("input") or item.get("context") or item.get("system_prompt") or "").strip()
    output = (item.get("output") or item.get("response") or item.get("completion") or "").strip()

    if instruction and output:
        user_content = f"{instruction}\n\n{input_ctx}" if input_ctx else instruction
        user_content = maybe_lowercase_user_text(user_content)
        return f"<|start_header_id|>user<|end_header_id|>\n\n{user_content}<|eot_id|>\n<|start_header_id|>assistant<|end_header_id|>\n\n{output}<|eot_id|>"

    # 4. Fallback to standard text
    text = item.get("text") or item.get("content") or item.get("story") or ""
    if text and len(str(text).strip()) > 20:
        return clean_text_formatting(str(text))
    return None


def clean_instruction_entry(item: Dict[str, Any]) -> Optional[str]:
    """Cleans and formats instruction-following / SFT entries using the Phi format (<|user|>, <|assistant|>)."""
    instruction = (item.get("instruction") or item.get("question") or item.get("prompt") or "").strip()
    input_ctx = (item.get("input") or item.get("context") or item.get("system_prompt") or "").strip()
    output = (item.get("output") or item.get("response") or item.get("completion") or "").strip()

    if not instruction or not output:
        # Fall back to checking conversational dialog turns
        return clean_chatml_entry(item)

    user_content = f"{instruction}\n{input_ctx}" if input_ctx else instruction
    user_content = maybe_lowercase_user_text(user_content)
    return f"<|user|>\n{user_content}\n<|assistant|>\n{output}"


def clean_story_entry(item: Dict[str, Any]) -> Optional[str]:
    """Cleans WritingPrompts or creative fiction entries (combining prompt and story)."""
    story = (item.get("story") or item.get("text") or "").strip()
    prompt = (item.get("prompt") or item.get("title") or "").strip()
    if not story or len(story) < 50:
        return None
    if prompt:
        prompt = re.sub(r"^\[\s*[A-Z]{2,4}\s*\]\s*", "", prompt, flags=re.I).strip()
        cleaned_story = clean_text_formatting(story)
        return f"{prompt}\n\n{cleaned_story}"
    return clean_text_formatting(story)


def clean_preference_entry(item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Cleans and standardizes preference pairs (chosen and rejected responses)
    for Direct Preference Optimization (DPO).
    Returns a standardized dictionary with keys: 'instruction', 'input', 'chosen', 'rejected'.
    """
    if not isinstance(item, dict):
        return None

    # 1. Anthropic HH format (\n\nHuman: ... \n\nAssistant: ...)
    if "chosen" in item and "rejected" in item and isinstance(item["chosen"], str) and "Assistant:" in item["chosen"]:
        c_parts = item["chosen"].rsplit("Assistant:", 1)
        r_parts = item["rejected"].rsplit("Assistant:", 1)
        prompt = c_parts[0].replace("Human:", "").strip()
        chosen = c_parts[1].strip()
        rejected = r_parts[1].strip() if len(r_parts) > 1 else item["rejected"].strip()
        if prompt and chosen and rejected:
            return {"instruction": maybe_lowercase_user_text(prompt), "input": "", "chosen": chosen, "rejected": rejected}

    # 2. SHP (Stanford Human Preferences) format
    if "human_ref_A" in item and "human_ref_B" in item and "labels" in item:
        prompt = str(item.get("history") or item.get("prompt") or "").strip()
        label = item["labels"]
        chosen = str(item["human_ref_A"] if label == 1 else item["human_ref_B"]).strip()
        rejected = str(item["human_ref_B"] if label == 1 else item["human_ref_A"]).strip()
        if prompt and chosen and rejected:
            return {"instruction": maybe_lowercase_user_text(prompt), "input": "", "chosen": chosen, "rejected": rejected}

    # 3. PKU-SafeRLHF format
    if "response_0" in item and "response_1" in item and "better_response_id" in item:
        prompt = str(item.get("prompt") or "").strip()
        bid = int(item["better_response_id"])
        chosen = str(item["response_0"] if bid == 0 else item["response_1"]).strip()
        rejected = str(item["response_1"] if bid == 0 else item["response_0"]).strip()
        if prompt and chosen and rejected:
            return {"instruction": maybe_lowercase_user_text(prompt), "input": "", "chosen": chosen, "rejected": rejected}

    # 4. LMSYS Chatbot Arena / Chat-1M format
    if "conversation_a" in item and "conversation_b" in item and "winner" in item:
        winner = str(item.get("winner") or "").strip().lower()
        if winner in ("model_a", "model_b"):
            ca, cb = item["conversation_a"], item["conversation_b"]
            chosen_conv = ca if winner == "model_a" else cb
            rej_conv = cb if winner == "model_a" else ca
            prompt = ""
            chosen_resp = ""
            if isinstance(chosen_conv, (list, tuple)):
                for m in chosen_conv:
                    if isinstance(m, dict):
                        if m.get("role") in ("user", "human") and not prompt:
                            prompt = str(m.get("content") or "").strip()
                        elif m.get("role") in ("assistant", "gpt", "bot"):
                            chosen_resp = str(m.get("content") or "").strip()
            rej_resp = ""
            if isinstance(rej_conv, (list, tuple)):
                for m in rej_conv:
                    if isinstance(m, dict) and m.get("role") in ("assistant", "gpt", "bot"):
                        rej_resp = str(m.get("content") or "").strip()
            if prompt and chosen_resp and rej_resp:
                return {"instruction": maybe_lowercase_user_text(prompt), "input": "", "chosen": chosen_resp, "rejected": rej_resp}

    # 5. Nectar format (prompt + answers list with rank)
    if "prompt" in item and "answers" in item and isinstance(item["answers"], (list, tuple)):
        answers = item["answers"]
        if len(answers) >= 2:
            if isinstance(answers[0], dict) and "rank" in answers[0]:
                sorted_ans = sorted(answers, key=lambda x: x.get("rank", 99))
                chosen = str(sorted_ans[0].get("answer") or sorted_ans[0].get("text") or "").strip()
                rejected = str(sorted_ans[-1].get("answer") or sorted_ans[-1].get("text") or "").strip()
            else:
                chosen = str(answers[0]).strip()
                rejected = str(answers[-1]).strip()
            prompt = str(item["prompt"]).strip()
            if prompt and chosen and rejected:
                return {"instruction": maybe_lowercase_user_text(prompt), "input": "", "chosen": chosen, "rejected": rejected}

    # 6. Standard chosen & rejected fields (DPO Mix, Orca DPO, UltraFeedback, ORPO Mix, etc.)
    if "chosen" in item and "rejected" in item:
        prompt = str(item.get("prompt") or item.get("question") or item.get("instruction") or "").strip()
        input_ctx = str(item.get("context") or item.get("system") or "").strip()
        if not prompt and "input" in item:
            prompt = str(item.get("input") or "").strip()
        elif "input" in item and not input_ctx:
            input_ctx = str(item.get("input") or "").strip()
        chosen = item["chosen"]
        rejected = item["rejected"]

        if isinstance(chosen, (list, tuple)) and len(chosen) > 0 and isinstance(chosen[0], dict):
            if not prompt:
                user_msgs = [m.get("content") for m in chosen if isinstance(m, dict) and m.get("role") in ("user", "human")]
                if user_msgs and user_msgs[-1]:
                    prompt = str(user_msgs[-1]).strip()
            chosen_msgs = [m.get("content") for m in chosen if isinstance(m, dict) and m.get("role") in ("assistant", "gpt", "bot")]
            chosen = str(chosen_msgs[-1] if chosen_msgs and chosen_msgs[-1] else "").strip()
            if isinstance(rejected, (list, tuple)) and len(rejected) > 0 and isinstance(rejected[0], dict):
                rej_msgs = [m.get("content") for m in rejected if isinstance(m, dict) and m.get("role") in ("assistant", "gpt", "bot")]
                rejected = str(rej_msgs[-1] if rej_msgs and rej_msgs[-1] else "").strip()
        else:
            chosen = str(chosen).strip()
            rejected = str(rejected).strip()

        if prompt and chosen and rejected:
            if random.random() < 0.5:
                prompt = prompt.lower()
                if input_ctx:
                    input_ctx = input_ctx.lower()
            return {"instruction": prompt, "input": input_ctx, "chosen": chosen, "rejected": rejected}

    return None

