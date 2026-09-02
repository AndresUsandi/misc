import os
import json
import time
import argparse
from prompt_randomizer_v2_phase1 import WordReplacerV2
from prompt_randomizer_v2_phase2 import PhraseRandomizer
from prompt_randomizer_v2_phase3 import ParagraphAssemblerV2

# ============================================================================
# Constants & Configuration Defaults
# ============================================================================
PROMPTS_PER_FILE = 1000
TEST_SUITE_NAME = "Bookito Feature Design Benchmark Randomized v2"
TEST_SUITE_VERSION = "2.0"
PROMPT_ID_PREFIX = "FEATURE-"
DIFFICULTY_OPTIONS = ("Easy", "Medium", "Hard")
FILE_NAME_TEMPLATE = "test_prompts_randomized_v2_{start_id:04d}-{end_id:04d}.json"

# 1. Non-Templated Word Randomization Defaults (Phase 1: DistilRoBERTa)
DEFAULT_WORD_PROB = 1.0
DEFAULT_WORD_THRESHOLD = 0.05

# 2. Template Value Randomization Defaults (Phase 3: Concept Swapping)
DEFAULT_TEMPLATE_VALUE_PROB = 1.0

# 3. Paragraph Quantity Randomization Defaults (Phase 3: Paragraph Count Limits)
DEFAULT_MIN_OPTIONAL_PARAGRAPHS = 0
DEFAULT_MAX_OPTIONAL_PARAGRAPHS = 5

# 4. Paragraph Combination Randomization Defaults (Phase 3: Inclusion Sampling)
DEFAULT_OPTIONAL_PARAGRAPH_PROB = 1.0

# 5. Paragraph Order Randomization Defaults (Phase 2 & Phase 3: Section & Global Ordering)
DEFAULT_SHUFFLE_PROB = 0.50
DEFAULT_SECTION_SHUFFLE_PROB = 1.0
DEFAULT_EXECUTIVE_LEAD_PROB = 0.40

# General Execution Defaults
DEFAULT_QUANTITY = 100000

DEFAULT_GENERATION_BATCH_SIZE = 50

def generate_randomized_prompts_v2(
    word_prob: float,
    word_threshold: float,
    template_value_prob: float,
    min_optional_paragraphs: int,
    max_optional_paragraphs: int,
    optional_paragraph_prob: float,
    section_shuffle_prob: float,
    executive_lead_prob: float,
    shuffle_prob: float,
    batch_size: int,
    quantity: int,
    verbose: bool
):
    print("Initializing NLP randomizers (v2: Batched DistilRoBERTa + Combinatorics)...")
    start_time = time.time()
    
    assembler_kwargs = {
        "min_optional_paragraphs": min_optional_paragraphs,
        "max_optional_paragraphs": max_optional_paragraphs,
        "optional_paragraph_prob": optional_paragraph_prob,
        "executive_lead_prob": executive_lead_prob,
        "section_shuffle_prob": section_shuffle_prob,
        "template_value_prob": template_value_prob
    }

    assembler = ParagraphAssemblerV2(**assembler_kwargs)
    word_replacer = WordReplacerV2(prob=word_prob, threshold=word_threshold, batch_size=batch_size)
    phrase_randomizer = PhraseRandomizer(prob=shuffle_prob)
    
    print(f"Initialization complete in {time.time() - start_time:.2f} seconds.")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    total_start = time.time()
    total_generated = 0
    file_batch_prompts = []
    file_start_id = 1

    categories_list = assembler.categories
    if not categories_list:
        print("No categories found in TEMPLATED_CATEGORY_PARAGRAPHS!")
        return

    print(f"Generating {quantity} randomized prompts in GPU batches across {len(categories_list)} categories (ckNN)...")

    for chunk_start in range(1, quantity + 1, batch_size):
        chunk_end = min(chunk_start + batch_size - 1, quantity)
        chunk_items = []

        # Step 1: Assemble templated paragraphs (Phase 3)
        for i in range(chunk_start, chunk_end + 1):
            prompt_id = f"{PROMPT_ID_PREFIX}{i:04d}"
            category_name = categories_list[(i - 1) % len(categories_list)]
            difficulty = DIFFICULTY_OPTIONS[(i - 1) % len(DIFFICULTY_OPTIONS)]

            _, assembled_templated = assembler.generate_prompt(category_name)
            original_prompt_text = assembler.render_original_prompt(assembled_templated, category_name=category_name)

            chunk_items.append({
                "i": i,
                "id": prompt_id,
                "category": category_name,
                "difficulty": difficulty,
                "templated": assembled_templated,
                "original": original_prompt_text
            })

        # Step 2: Parallel batched Masked Language Modeling on GPU (Phase 1: DistilRoBERTa)
        templated_texts = [item["templated"] for item in chunk_items]
        randomized_words_list = word_replacer.process_prompts_batch(templated_texts)

        # Step 3 & 4: Template Concept Swapping (Phase 3) and Block Shuffling (Phase 2)
        for item, randomized_words in zip(chunk_items, randomized_words_list):
            filled_prompt = assembler.fill_template_placeholders(randomized_words, category_name=item["category"])
            final_prompt_text = phrase_randomizer.process_prompt(filled_prompt)

            prompt_obj = {
                "id": item["id"],
                "primaryCategory": item["category"],
                "difficulty": item["difficulty"],
                "prompt": final_prompt_text
            }
            file_batch_prompts.append(prompt_obj)
            total_generated += 1

            if verbose:
                print("\n" + "=" * 80)
                print(f"PROMPT {item['i']} [{item['category']} | {item['difficulty']}]")
                print("-" * 80)
                print(f"ORIGINAL:\n{item['original']}\n")
                print(f"RANDOMIZED:\n{final_prompt_text}")
                print("=" * 80)

            # When a batch reaches 1000 prompts or is the last prompt, write to file
            if len(file_batch_prompts) == PROMPTS_PER_FILE or item["i"] == quantity:
                file_end_id = item["i"]
                out_file_name = FILE_NAME_TEMPLATE.format(start_id=file_start_id, end_id=file_end_id)
                out_file_path = os.path.join(base_dir, out_file_name)

                file_payload = {
                    "testSuite": TEST_SUITE_NAME,
                    "version": TEST_SUITE_VERSION,
                    "promptCount": len(file_batch_prompts),
                    "prompts": file_batch_prompts
                }

                with open(out_file_path, "w", encoding="utf-8") as f:
                    json.dump(file_payload, f, indent=2)

                print(f"Saved {len(file_batch_prompts)} prompts to {out_file_name}")
                file_batch_prompts = []
                file_start_id = item["i"] + 1

        if not verbose and (chunk_end % 100 == 0 or chunk_end == quantity):
            print(f"  Generated {chunk_end}/{quantity} prompts...")

    print(f"\nAll done! Successfully generated {total_generated} prompts in {time.time() - total_start:.2f} seconds.")

def main():
    parser = argparse.ArgumentParser(
        description="NLP Randomization Pipeline V2: Neural Masked LM, Paragraph Combinatorics, and Structural Shuffling"
    )

    # 1. Non-Templated Word Randomization Controls (Phase 1)
    parser.add_argument(
        "--word-prob",
        type=float,
        default=DEFAULT_WORD_PROB,
        help="Probability (0.0 to 1.0) of replacing an eligible non-templated word in the paragraph with a DistilRoBERTa synonym (default: 1.00)"
    )
    parser.add_argument(
        "--word-threshold",
        type=float,
        default=DEFAULT_WORD_THRESHOLD,
        help="Minimum confidence score threshold (0.0 to 1.0) required for a DistilRoBERTa fill-mask predicted word (default: 0.05)"
    )

    # 2. Template Value Randomization Controls (Phase 3)
    parser.add_argument(
        "--template-value-prob",
        type=float,
        default=DEFAULT_TEMPLATE_VALUE_PROB,
        help="Probability (0.0 to 1.0) of swapping a {category_id} placeholder with a random concept from that category. Lower values retain the original value (default: 1.0)"
    )

    # 3. Paragraph Quantity Randomization Controls (Phase 3)
    parser.add_argument(
        "--min-optional-paragraphs",
        type=int,
        default=DEFAULT_MIN_OPTIONAL_PARAGRAPHS,
        help="Minimum number of optional paragraphs (e.g. tech_stack, target_audience) to include beyond the 3 mandatory paragraphs (default: 0)"
    )
    parser.add_argument(
        "--max-optional-paragraphs",
        type=int,
        default=DEFAULT_MAX_OPTIONAL_PARAGRAPHS,
        help="Maximum number of optional paragraphs (e.g. tech_stack, target_audience) to include beyond the 3 mandatory paragraphs (default: 5)"
    )

    # 4. Paragraph Combination Randomization Controls (Phase 3)
    parser.add_argument(
        "--optional-paragraph-prob",
        type=float,
        default=DEFAULT_OPTIONAL_PARAGRAPH_PROB,
        help="Probability (0.0 to 1.0) of each optional paragraph type being eligible for candidate sampling (default: 1.0)"
    )

    # 5. Paragraph Order Randomization Controls (Phase 2 & Phase 3)
    parser.add_argument(
        "--section-shuffle-prob",
        type=float,
        default=DEFAULT_SECTION_SHUFFLE_PROB,
        help="Probability (0.0 to 1.0) of shuffling the internal order of paragraphs within each logical section (Context, Middle, Request) (default: 1.0)"
    )
    parser.add_argument(
        "--executive-lead-prob",
        type=float,
        default=DEFAULT_EXECUTIVE_LEAD_PROB,
        help="Probability (0.0 to 1.0) of inverting prompt structure to place the Request section at the very top ('Executive Lead' style) (default: 0.40)"
    )
    parser.add_argument(
        "--shuffle-prob",
        type=float,
        default=DEFAULT_SHUFFLE_PROB,
        help="Probability (0.0 to 1.0) of performing global block-level paragraph shuffling across the entire prompt in Phase 2 (default: 0.50)"
    )

    # Performance & Execution Controls
    parser.add_argument(
        "--batch-size",
        type=int,
        default=DEFAULT_GENERATION_BATCH_SIZE,
        help="Batch size of prompts to process simultaneously on GPU for neural word replacement (default: 50)"
    )
    parser.add_argument(
        "--quantity",
        type=int,
        default=DEFAULT_QUANTITY,
        help="Total number of synthetic prompts to generate across all categories (default: 1000)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print side-by-side ORIGINAL vs. RANDOMIZED text comparison for every generated prompt"
    )
    
    args = parser.parse_args()
    
    print("--- Configuration (v2) ---")
    print(f"Word Replacement Prob:       {args.word_prob}")
    print(f"Word Prediction Threshold:   {args.word_threshold}")
    print(f"Template Value Swap Prob:    {args.template_value_prob}")
    print(f"Min Optional Paragraphs:     {args.min_optional_paragraphs} (Min total: {args.min_optional_paragraphs + 3})")
    print(f"Max Optional Paragraphs:     {args.max_optional_paragraphs} (Max total: {args.max_optional_paragraphs + 3})")
    print(f"Optional Paragraph Prob:     {args.optional_paragraph_prob}")
    print(f"Section Shuffle Prob:        {args.section_shuffle_prob}")
    print(f"Executive Lead Prob:         {args.executive_lead_prob}")
    print(f"Global Phrase Shuffle Prob:  {args.shuffle_prob}")
    print(f"GPU Batch Size:              {args.batch_size}")
    print(f"Quantity:                    {args.quantity}")
    print(f"Verbose Logging:             {args.verbose}")
    print("--------------------------\n")
    
    generate_randomized_prompts_v2(
        word_prob=args.word_prob,
        word_threshold=args.word_threshold,
        template_value_prob=args.template_value_prob,
        min_optional_paragraphs=args.min_optional_paragraphs,
        max_optional_paragraphs=args.max_optional_paragraphs,
        optional_paragraph_prob=args.optional_paragraph_prob,
        section_shuffle_prob=args.section_shuffle_prob,
        executive_lead_prob=args.executive_lead_prob,
        shuffle_prob=args.shuffle_prob,
        batch_size=args.batch_size,
        quantity=args.quantity,
        verbose=args.verbose
    )

if __name__ == "__main__":
    main()
