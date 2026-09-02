import sys
import os
import time
import argparse

# Add parent directory to sys.path to import Bookito modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from processors.augmented_content_generator import (
    AugmentedContentGenerator,
    format_augmented_results_to_text,
    RESULT_KEY_TOTAL_AGGREGATED_SCORE,
    RESULT_KEY_CHUNKS,
    RESULT_KEY_MATCHED_CONCEPTS
)
from processors.concept_extractor import ConceptExtractor
from database.query_manager import (
    RESULT_KEY_SCORE,
    RESULT_KEY_CHUNK_INDEX,
    RESULT_KEY_CHUNK_TEXT,
    RESULT_KEY_CHAPTER_NUMBER,
    RESULT_KEY_CHAPTER_TITLE,
    RESULT_KEY_BOOK_NAME,
    RESULT_KEY_FILE_LINK
)
from visualization.constants import (
    CLI_ARG_QUERIES_FLAG,
    CLI_ARG_QUERIES_SHORT_FLAG,
    CLI_ARG_QUERIES_HELP,
    CLI_ARG_MAX_CONCURRENT_FLAG,
    CLI_ARG_MAX_CONCURRENT_SHORT_FLAG,
    CLI_ARG_MAX_CONCURRENT_HELP,
    CLI_DESCRIPTION,
    QUERY_DELIMITER,
    DEFAULT_MAX_CONCURRENT_QUERIES
)

# Top-of-File Constants
CLI_ARG_PROMPT_FLAG = "--prompt"
CLI_ARG_PROMPT_SHORT_FLAG = "-p"
CLI_ARG_PROMPT_HELP = "Multi-paragraph text prompt for concept extraction and final search"

TEST_USE_WORD_SCORING = True
TEST_USE_MULTI_INSTANCE_BOOST = True
TEST_USE_SEMANTIC_BOOST = True
TEST_MAX_DF_THRESHOLD = 0.90

DEFAULT_TEST_PROMPT = """Our organization needs a distributed workflow engine capable of executing business processes that may run for several weeks.

The engine should survive crashes, retries, duplicate messages, version upgrades, and regional failures while guaranteeing exactly-once logical execution.

The workflow language should support timers, parallel branches, compensation, retries, and human approval steps.

Generate a feature design document comparing different workflow execution models."""

MAX_SNIPPET_LENGTH = 100
MAX_SAMPLE_CHUNKS_DISPLAY = 5

BOOK_SECTION_DELIMITER = "--------------------------------"
ELLIPSIS_GAP_INDICATOR = "..."
EMPTY_STRING = ""
NEWLINE = "\n"

HEADER_MASTER_TITLE = "=== AUGMENTED CONTENT GENERATOR RESULTS ==="
SEPARATOR_LINE = "=" * 85
SUB_SEPARATOR_LINE = "-" * 85
NO_RESULTS_MESSAGE = "No aggregated search results found."
SUMMARY_FORMAT = "Concepts Searched: {concepts} | Result Groups: {count} | Total Chunks Across Groups: {total_chunks} | Elapsed Time: {elapsed:.4f}s"

GROUP_HEADER_FORMAT = (
    "[{rank}] Total Score: {total_score:.4f} | Book: {book_name} | Ch {chapter_number}: {chapter_title}\n"
    "    File Link       : {file_link}\n"
    "    Matched Concepts: {matched_concepts}\n"
    "    Total Chunks    : {chunks_count} (+/- 5 context expansion)"
)

CHUNK_ITEM_FORMAT = "    Chunk #{chunk_index:3d} | Score: {score:.4f} | Direct Hit: {is_hit} | Snippet: {snippet}"

CLI_TEST_DESCRIPTION = "CLI tool for testing AugmentedContentGenerator multi-concept search and aggregation."

def display_augmented_results(results: list, concepts_str: str, elapsed: float):
    """Prints formatted search result groups to console."""
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    print(HEADER_MASTER_TITLE)
    print(SEPARATOR_LINE)
    if not results:
        print(NO_RESULTS_MESSAGE)
        print(SEPARATOR_LINE)
        return

    total_chunks_across_groups = 0

    for rank, group in enumerate(results, start=1):
        tot_score = group.get(RESULT_KEY_TOTAL_AGGREGATED_SCORE, 0.0)
        b_name = str(group.get(RESULT_KEY_BOOK_NAME, "")).encode("ascii", "replace").decode("ascii")
        ch_num = group.get(RESULT_KEY_CHAPTER_NUMBER, 1)
        ch_title = str(group.get(RESULT_KEY_CHAPTER_TITLE, "")).encode("ascii", "replace").decode("ascii")
        f_link = group.get(RESULT_KEY_FILE_LINK, "")
        matched_concepts = group.get(RESULT_KEY_MATCHED_CONCEPTS, [])
        chunks = group.get(RESULT_KEY_CHUNKS, [])

        total_chunks_across_groups += len(chunks)

        formatted_header = GROUP_HEADER_FORMAT.format(
            rank=rank,
            total_score=tot_score,
            book_name=b_name,
            chapter_number=ch_num,
            chapter_title=ch_title,
            file_link=f_link,
            matched_concepts=matched_concepts,
            chunks_count=len(chunks)
        )
        print(formatted_header)
        print(SUB_SEPARATOR_LINE)

        # Print sample chunks
        sample_chunks = chunks[:MAX_SAMPLE_CHUNKS_DISPLAY]
        for c in sample_chunks:
            c_idx = c.get(RESULT_KEY_CHUNK_INDEX, 0)
            sc = c.get(RESULT_KEY_SCORE, 0.0)
            is_hit = c.get("_is_direct_hit", False)
            raw_text = c.get(RESULT_KEY_CHUNK_TEXT, "")
            clean_text = raw_text.replace("\n", " ")[:MAX_SNIPPET_LENGTH]
            snippet = clean_text.encode("ascii", "replace").decode("ascii")

            print(CHUNK_ITEM_FORMAT.format(
                chunk_index=c_idx,
                score=sc,
                is_hit=is_hit,
                snippet=snippet
            ))

        if len(chunks) > MAX_SAMPLE_CHUNKS_DISPLAY:
            print(f"    ... and {len(chunks) - MAX_SAMPLE_CHUNKS_DISPLAY} more context chunks")
        print(SEPARATOR_LINE)

    summary_msg = SUMMARY_FORMAT.format(
        concepts=concepts_str,
        count=len(results),
        total_chunks=total_chunks_across_groups,
        elapsed=elapsed
    )
    print(summary_msg)
    print(SEPARATOR_LINE)

def main():
    parser = argparse.ArgumentParser(description=CLI_TEST_DESCRIPTION)
    parser.add_argument(
        CLI_ARG_PROMPT_FLAG,
        CLI_ARG_PROMPT_SHORT_FLAG,
        type=str,
        default=DEFAULT_TEST_PROMPT,
        help=CLI_ARG_PROMPT_HELP
    )
    parser.add_argument(
        CLI_ARG_MAX_CONCURRENT_FLAG,
        CLI_ARG_MAX_CONCURRENT_SHORT_FLAG,
        type=int,
        default=DEFAULT_MAX_CONCURRENT_QUERIES,
        help=CLI_ARG_MAX_CONCURRENT_HELP
    )

    args = parser.parse_args()
    prompt_text = args.prompt.strip()

    # Step 1: Extract concepts using ConceptExtractor with configured flags
    extractor = ConceptExtractor(
        use_word_scoring=TEST_USE_WORD_SCORING,
        use_multi_instance_boost=TEST_USE_MULTI_INSTANCE_BOOST,
        use_semantic_boost=TEST_USE_SEMANTIC_BOOST,
        max_df_threshold=TEST_MAX_DF_THRESHOLD
    )
    kept_tuples, _ = extractor.extract_with_details(prompt_text)
    extracted_concepts = [phrase for phrase, score, occ in kept_tuples]

    print("=== EXTRACTED CONCEPTS FROM PROMPT ===")
    print(f"Total Extracted Concepts: {len(extracted_concepts)}")
    for idx, (phrase, sc, occ) in enumerate(kept_tuples[:10], start=1):
        print(f"  {idx:2d}. {phrase:40s} | Score: {sc:.4f} | Occ: {occ}")
    print(SEPARATOR_LINE)

    # Step 2: Pass extracted concepts List[str] to AugmentedContentGenerator
    generator = AugmentedContentGenerator()

    start_time = time.time()
    results = generator.generate_augmented_content(extracted_concepts, max_concurrent=args.max_concurrent)
    elapsed = time.time() - start_time

    formatted_text = format_augmented_results_to_text(results)

    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    print(formatted_text)

if __name__ == "__main__":
    main()
