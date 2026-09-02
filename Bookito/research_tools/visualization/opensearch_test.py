import sys
import os
import time
import argparse
import concurrent.futures

# Add parent directory to sys.path to import Bookito modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.query_manager import QueryManager

# Command Line Argument Configuration Constants
DEFAULT_QUERY = "Programming"
DEFAULT_PAGE = 1
SEARCH_PAGE_SIZE = 50
MAX_WORKERS = 2

ARG_QUERY_NAME = "query"
ARG_QUERY_HELP = "The query string to search for in OpenSearch (default: 'Programming')"
ARG_PAGE_NAME = "--page"
ARG_PAGE_HELP = "Page number for search results (default: 1)"

# Result Dictionary Keys (matching QueryManager)
RESULT_KEY_SCORE = "score"
RESULT_KEY_CHUNK_ID = "chunk_id"
RESULT_KEY_CHUNK_INDEX = "chunk_index"
RESULT_KEY_CHUNK_TEXT = "chunk_text"
RESULT_KEY_VECTOR_DIM = "vector_dim"
RESULT_KEY_CHAPTER_ID = "chapter_id"
RESULT_KEY_CHAPTER_NUMBER = "chapter_number"
RESULT_KEY_CHAPTER_TITLE = "chapter_title"
RESULT_KEY_BOOK_ID = "book_id"
RESULT_KEY_BOOK_NAME = "book_name"
RESULT_KEY_FILE_LINK = "file_link"

# Output Formatting Constants
HEADER_LEXICAL_TITLE = "=== LEXICAL SEARCH RESULTS (OpenSearch Text Match) ==="
HEADER_VECTOR_TITLE = "=== VECTOR SEARCH RESULTS (KNN Semantic Search) ==="
NO_RESULTS_MESSAGE = "No results found."
SUMMARY_FORMAT = "Query: '{query}' | Page: {page} | Lexical Hits: {lexical_count} | Vector Hits: {vector_count} | Elapsed Time: {elapsed:.4f}s"
SEPARATOR_LINE = "=" * 80

RESULT_ITEM_FORMAT = (
    "[{idx}] Score: {score:.6f} | Book: {book_name} | Ch {chapter_number}: {chapter_title} | Chunk #{chunk_index}\n"
    "    File: {file_link}\n"
    "    Text: {chunk_text}\n"
)

CLI_DESCRIPTION = "CLI Tool for testing OpenSearch lexical and vector queries."

def display_results_section(title: str, results: list):
    print(title)
    print(SEPARATOR_LINE)
    if not results:
        print(NO_RESULTS_MESSAGE)
        print()
        return

    for idx, item in enumerate(results, start=1):
        formatted_item = RESULT_ITEM_FORMAT.format(
            idx=idx,
            score=item[RESULT_KEY_SCORE],
            book_name=item[RESULT_KEY_BOOK_NAME],
            chapter_number=item[RESULT_KEY_CHAPTER_NUMBER],
            chapter_title=item[RESULT_KEY_CHAPTER_TITLE],
            chunk_index=item[RESULT_KEY_CHUNK_INDEX],
            file_link=item[RESULT_KEY_FILE_LINK],
            chunk_text=item[RESULT_KEY_CHUNK_TEXT]
        )
        print(formatted_item)
    print()

def main():
    parser = argparse.ArgumentParser(description=CLI_DESCRIPTION)
    parser.add_argument(
        ARG_QUERY_NAME,
        nargs="?",
        default=DEFAULT_QUERY,
        help=ARG_QUERY_HELP
    )
    parser.add_argument(
        ARG_PAGE_NAME,
        type=int,
        default=DEFAULT_PAGE,
        help=ARG_PAGE_HELP
    )

    args = parser.parse_args()
    query_text = args.query
    page = args.page

    query_manager = QueryManager()

    start_time = time.time()

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_lex = executor.submit(query_manager.lexical_search, query_text, page=page, page_size=SEARCH_PAGE_SIZE)
        future_vec = executor.submit(query_manager.vector_search, query_text, page=page, page_size=SEARCH_PAGE_SIZE)

        lexical_results = future_lex.result()
        vector_results = future_vec.result()

    elapsed = time.time() - start_time

    # Display results on console
    display_results_section(HEADER_LEXICAL_TITLE, lexical_results)
    display_results_section(HEADER_VECTOR_TITLE, vector_results)

    # Display elapsed time summary at the end, after results are displayed
    summary_msg = SUMMARY_FORMAT.format(
        query=query_text,
        page=page,
        lexical_count=len(lexical_results),
        vector_count=len(vector_results),
        elapsed=elapsed
    )
    print(SEPARATOR_LINE)
    print(summary_msg)
    print(SEPARATOR_LINE)

if __name__ == "__main__":
    main()
