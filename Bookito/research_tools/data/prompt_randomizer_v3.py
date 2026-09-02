import os
import glob
import json
import time
import argparse
import requests

# ============================================================================
# Constants & Configuration Defaults
# ============================================================================
DEFAULT_INDEX_START = 1
DEFAULT_INDEX_END = 1000
DEFAULT_MODEL = "qwen3.5:4b"
ALLOWED_MODELS = (
    "qwen3.5:9b",
    "gemma4:e2b",
    "granite4.1:8b",
    "phi4-mini:3.8b",
    "qwen3.5:4b",
    "qwen3.8:latest"
)

CHATSITO_API_URL = "http://localhost:5257/api/chat/stream"
CHATSITO_TIMEOUT = 180

PROMPTS_PER_FILE = 1000
TEST_SUITE_NAME = "Bookito Feature Design Benchmark Randomized v3"
TEST_SUITE_VERSION = "3.0"
OUTPUT_FILE_NAME_TEMPLATE = "test_prompts_randomized_v3_{start_id:04d}-{end_id:04d}.json"
INPUT_PROMPTS_PATTERN = "test_prompts_*.json"
EXCLUDED_RANDOMIZED_PREFIX = "test_prompts_randomized_"

USER_MESSAGE_TEMPLATE = """CATEGORY: {category}

INPUT PROMPT:

{prompt}"""

SYSTEM_PROMPT = """YOU ARE AN ASSISTANT CAPABLE OF REWRITING PROMTPS FOR ME. 
I WILL PROVIDE A PROMPT ALONG WITH A CATEGORY THAT THE PROMPT BELONGS TO. 
YOU WILL:
1. IDENTIFY THE SUBJECTS, OBJECTS AND OTHER IMPORTANT MAIN CONCEPTS FROM THE PROMPT
2. REWRITE THE ENTIRE PROMPT SUCH THAT THE TEXT OF THE PROMPT WILL BE AS DIFFERENT AS HUMANLY POSSIBLE, WHILE MAINTAINING THE IDEA
3. REPLACE THE SUBJECTS, OBJECTS, AND OTHER IMPORTANT CONCEPTS WITH CATEGORICALLY SIMILAR, BUT TECHNOLOGICALLY DIFFERENT SUBJECTS, OBJECTS, AND IMPORTANT CONCEPTS BY KEEPING IN MIND THE PROVIDED CATEGORY SO THAT THE REPLACEMENT STILL BELONGS TO THE SAME CATEGORY
4. CHANGE THE ORDER OF THE SENTENCES (AND ADJUST GRAMMAR SO THAT IT MAKES GRAMMATICAL SENSE WHEN THE ORDER OF THE SENTENCES IS CHANGED)
5. SEPARATE DISTINCT THOUGHTS, CONSTRAINTS, AND SECTIONS INTO MULTIPLE PARAGRAPHS DIVIDED BY A BLANK LINE (DO NOT MERGE THE ENTIRE OUTPUT INTO A SINGLE CONTINUOUS BLOCK OF TEXT)

THE IDEA IS TO MAKE A NEW PROMPT THAT IS GRAMATICALLY AND SYNTACTICALLY AS DIFFERENT AS POSSIBLE, WHILE MAINTAINING THE SEMANTICS AND SPIRIT, BUT APPLIED TO A DIFFERENT TECHNOLOGY CHOICE THAT IS CATEGORICALLY THE SAME AS THE ORIGINAL

---EXAMPPLE---

CATEGORY: Network Protocol

INPUT PROMPT:

We are building a zero-copy packet serialization protocol for kernel bypass networking of our production platform.

Our organization manages over 2,000,000 records and needs to ensure compliance with strict SOC2 and GDPR security requirements.

Can you walk me through the design? Specifically, I'd like to understand the component boundaries, how failure recovery works, what tradeoffs we're making, and how we should roll this out incrementally to production.

GENERIZICED PROMPT:

We are building a {sub-system} for {product}.

Our organization {responsibility} and needs to {requirement}.

Can you walk me through the design? Specifically, I'd like to understand the component boundaries, how failure recovery works, what tradeoffs we're making, and how we should roll this out incrementally to production.

EXTRACTED OBJECTS, SUBJECTS, AND IMPORTANT CONCEPTS:
- {sub-system}: zero-copy packet serialization protocol
- {product}: kernel bypass networking of our production platform
- {responsibility}: manages over 2,000,000 records
- {requirement}: ensure compliance with strict SOC2 and GDPR security requirements

NEW GENERICIZED PROMPT WITH MAJOR SYNTACTIC REPLACEMENT:

Our team is developing a {sub-system} intended to support {product}.

Because we {responsibility}, the solution must also {requirement}.

Describe an appropriate architecture and implementation strategy. Cover how the major pieces should interact, how the system should behave when disruptions or errors occur, and the important compromises between competing design goals. Also explain how the technology could be introduced gradually without putting the existing environment at unnecessary risk.

NEW EXTRACTED OBJECTS, SUBJECTS, AND IMPORTANT CONCEPTS:

- {sub-system}: store-and-forward telemetry transport protocol
- {product}: intermittently connected industrial IoT sensors deployed at remote facilities
- {responsibility}: collect real-time measurements from tens of thousands of geographically distributed monitoring devices
= {requirement}: preserve ordered, reliable delivery despite unstable links, device restarts, and prolonged connectivity outages

OUTPUT PROMPT THAT KEEPS THE SAME SENTENCE ORDERING:

Our team is developing a store-and-forward telemetry transport protocol intended to support intermittently connected industrial IoT sensors deployed at remote facilities.

Because we collect real-time measurements from tens of thousands of geographically distributed monitoring devices, the solution must also preserve ordered, reliable delivery despite unstable links, device restarts, and prolonged connectivity outages.

Describe an appropriate architecture and implementation strategy. Cover how the major pieces should interact, how the system should behave when disruptions or errors occur, and the important compromises between competing design goals. Also explain how the technology could be introduced gradually without putting the existing environment at unnecessary risk.

FINAL OUTPUT PROMPT WITH DIFFERENT SENTENCE ORDERING:

Could you propose an architecture for this and explain the major design decisions involved? Include behavior during partial failures, reconnections, and recovery, the boundaries between major components, and a safe strategy for introducing the solution into an existing environment.

A major constraint is that we operate tens of thousands of geographically distributed monitoring devices, so whatever we deploy has to preserve ordered, reliable delivery despite unstable links, device restarts, and prolonged connectivity outages.

The underlying project involves a store-and-forward telemetry transport protocol for intermittently connected industrial IoT sensors deployed at remote facilities. We need the design to remain practical under real-world operating conditions rather than assuming an ideal environment.

---END OF EXAMPLE---

YOU SHOULD OUTPUT THE FINAL PROMPT ONLY. YOU DO NOT NEED TO PROVIDE THE INTERIM STEPS NOR ANY OTHER TEXT OTHER THAN THE PLAIN OUTPUT PROMPT."""

def call_chatsito_rewrite(model: str, category: str, prompt_text: str, api_url: str = CHATSITO_API_URL) -> str:
    """
    Sends a rewriting request to Chatsito's LLM API using the standardized system prompt
    and returns the rewritten prompt text.
    """
    user_content = USER_MESSAGE_TEMPLATE.format(category=category, prompt=prompt_text)
    
    payload = {
        "Model": model,
        "Messages": [
            {"Role": "System", "Content": SYSTEM_PROMPT},
            {"Role": "User", "Content": user_content}
        ],
        "Tools": []
    }
    
    headers = {"Content-Type": "application/json"}
    
    try:
        resp = requests.post(api_url, json=payload, headers=headers, stream=True, timeout=CHATSITO_TIMEOUT)
        if resp.status_code != 200:
            raise RuntimeError(f"Error from Chatsito API ({resp.status_code}): {resp.text}")
        
        full_content = []
        for line in resp.iter_lines():
            if line:
                decoded = line.decode('utf-8')
                if decoded.startswith('data: '):
                    data_str = decoded[6:]
                    try:
                        data_json = json.loads(data_str)
                        if data_json.get("type") == "content" and "content" in data_json:
                            full_content.append(data_json["content"])
                    except Exception:
                        pass
                else:
                    try:
                        data_json = json.loads(decoded)
                        if "content" in data_json:
                            full_content.append(data_json["content"])
                        elif "message" in data_json and "content" in data_json["message"]:
                            full_content.append(data_json["message"]["content"])
                    except Exception:
                        pass
        
        result_text = "".join(full_content).strip()
        if not result_text:
            return prompt_text
        return result_text
        
    except Exception as e:
        print(f"  [Warning] API call failed ({e}). Retaining original prompt.")
        return prompt_text

def load_source_prompts(data_dir: str, index_start: int, index_end: int) -> list:
    """
    Scans data directory for original benchmark JSON files, sorting them numerically,
    and returns prompt objects whose 1-based index falls within [index_start, index_end].
    """
    pattern = os.path.join(data_dir, INPUT_PROMPTS_PATTERN)
    all_files = sorted(glob.glob(pattern))
    
    # Filter out any randomized files
    source_files = [f for f in all_files if EXCLUDED_RANDOMIZED_PREFIX not in os.path.basename(f)]
    
    selected_prompts = []
    current_idx = 0
    for file_path in source_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                file_prompts = data.get("prompts", [])
                for p in file_prompts:
                    current_idx += 1
                    if current_idx >= index_start and current_idx <= index_end:
                        p_copy = dict(p)
                        p_copy["_global_index"] = current_idx
                        selected_prompts.append(p_copy)
                    if current_idx > index_end:
                        return selected_prompts
        except Exception as e:
            print(f"  [Warning] Could not read {file_path}: {e}")
            
    return selected_prompts

def generate_randomized_prompts_v3(
    model: str,
    index_start: int,
    index_end: int,
    verbose: bool,
    api_url: str = CHATSITO_API_URL
):
    """
    Main orchestration routine for V3 LLM-driven prompt rewriting over an index range.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    print(f"Loading source benchmark prompts from {base_dir} (Index Range: {index_start} to {index_end})...")
    source_prompts = load_source_prompts(base_dir, index_start=index_start, index_end=index_end)
    
    if not source_prompts:
        print(f"No source prompts found in range {index_start}-{index_end} in data directory!")
        return

    actual_count = len(source_prompts)
    print(f"Processing {actual_count} prompts with Chatsito API model '{model}'...\n")
    
    start_time = time.time()
    total_generated = 0
    file_batch_prompts = []
    batch_first_id = source_prompts[0].get("_global_index", index_start)

    for i, orig_item in enumerate(source_prompts, start=1):
        global_idx = orig_item.get("_global_index", index_start + i - 1)
        prompt_id = orig_item.get("id", f"FEATURE-{global_idx:04d}")
        category = orig_item.get("primaryCategory", "General")
        difficulty = orig_item.get("difficulty", "Medium")
        original_text = orig_item.get("prompt", "")

        # Call Chatsito LLM API for rewriting
        rewritten_text = call_chatsito_rewrite(
            model=model,
            category=category,
            prompt_text=original_text,
            api_url=api_url
        )

        prompt_obj = {
            "id": prompt_id,
            "primaryCategory": category,
            "difficulty": difficulty,
            "prompt": rewritten_text
        }
        file_batch_prompts.append(prompt_obj)
        total_generated += 1

        if verbose:
            print("\n" + "=" * 80)
            print(f"PROMPT {global_idx} [{prompt_id} | {category} | {difficulty}] (Progress: {i}/{actual_count})")
            print("-" * 80)
            print(f"ORIGINAL:\n{original_text}\n")
            print(f"RANDOMIZED (V3 - {model}):\n{rewritten_text}")
            print("=" * 80)
        elif i % 10 == 0 or i == actual_count:
            print(f"  Processed {i}/{actual_count} prompts (Global Index: {global_idx})...")

        # Write to JSON file every 1,000 prompts or on final prompt in the selection
        if len(file_batch_prompts) == PROMPTS_PER_FILE or i == actual_count:
            batch_last_id = global_idx
            out_file_name = OUTPUT_FILE_NAME_TEMPLATE.format(start_id=batch_first_id, end_id=batch_last_id)
            out_file_path = os.path.join(base_dir, out_file_name)

            file_payload = {
                "testSuite": TEST_SUITE_NAME,
                "version": TEST_SUITE_VERSION,
                "model": model,
                "promptCount": len(file_batch_prompts),
                "prompts": file_batch_prompts
            }

            with open(out_file_path, "w", encoding="utf-8") as f:
                json.dump(file_payload, f, indent=2)

            print(f"Saved {len(file_batch_prompts)} prompts to {out_file_name}")
            file_batch_prompts = []
            if i < actual_count:
                batch_first_id = source_prompts[i].get("_global_index", global_idx + 1)

    print(f"\nAll done! Successfully rewritten and saved {total_generated} prompts in {time.time() - start_time:.2f} seconds.")

def main():
    parser = argparse.ArgumentParser(
        description="Prompt Randomizer V3: LLM-Driven Semantic & Technological Prompt Rewriting via Chatsito API"
    )
    parser.add_argument(
        "--model",
        type=str,
        default=DEFAULT_MODEL,
        choices=ALLOWED_MODELS,
        help=f"Chatsito LLM model to use for prompt rewriting. Choices: {', '.join(ALLOWED_MODELS)} (default: {DEFAULT_MODEL})"
    )
    parser.add_argument(
        "--index_start",
        "--index-start",
        type=int,
        default=DEFAULT_INDEX_START,
        dest="index_start",
        help=f"1-based starting index of prompts to rewrite (default: {DEFAULT_INDEX_START})"
    )
    parser.add_argument(
        "--index_end",
        "--index-end",
        type=int,
        default=DEFAULT_INDEX_END,
        dest="index_end",
        help=f"1-based ending index of prompts to rewrite (inclusive, default: {DEFAULT_INDEX_END})"
    )
    parser.add_argument(
        "--api-url",
        type=str,
        default=CHATSITO_API_URL,
        help=f"Chatsito API chat/stream endpoint URL (default: {CHATSITO_API_URL})"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print side-by-side ORIGINAL vs. RANDOMIZED text comparison for every rewritten prompt"
    )

    args = parser.parse_args()

    # Validate model selection
    if args.model not in ALLOWED_MODELS:
        parser.error(f"Invalid model '{args.model}'. Allowed choices: {', '.join(ALLOWED_MODELS)}")

    # Validate index range
    if args.index_start < 1:
        parser.error(f"Invalid --index_start '{args.index_start}'. Must be >= 1.")
    if args.index_end < args.index_start:
        parser.error(f"--index_end ({args.index_end}) cannot be less than --index_start ({args.index_start}).")

    print("--- Configuration (v3 - LLM Rewriting) ---")
    print(f"Selected Model:  {args.model}")
    print(f"Index Start:     {args.index_start}")
    print(f"Index End:       {args.index_end}")
    print(f"Chatsito URL:    {args.api_url}")
    print(f"Verbose Logging: {args.verbose}")
    print("------------------------------------------\n")

    generate_randomized_prompts_v3(
        model=args.model,
        index_start=args.index_start,
        index_end=args.index_end,
        verbose=args.verbose,
        api_url=args.api_url
    )

if __name__ == "__main__":
    main()
