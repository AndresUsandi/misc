# ==============================================================================
# BOOKITO VISUALIZATION SHARED CONSTANTS
# ==============================================================================

CLI_ARG_QUERIES_FLAG = "--queries"
CLI_ARG_QUERIES_SHORT_FLAG = "-q"
CLI_ARG_QUERIES_HELP = "Semicolon-delimited list of initial search queries (e.g. 'programming;databases;design')"
CLI_ARG_MAX_CONCURRENT_FLAG = "--max-concurrent"
CLI_ARG_MAX_CONCURRENT_SHORT_FLAG = "-m"
CLI_ARG_MAX_CONCURRENT_HELP = "Maximum concurrent OpenSearch queries allowed simultaneously (default: 3)"
CLI_DESCRIPTION = "Bookito OpenSearch Multi-Tab Search Visualizer CLI"
QUERY_DELIMITER = ";"
OPENSEARCH_VISUALIZER_FILENAME = "opensearch_visualizer.py"
FINAL_SEARCH_VISUALIZER_FILENAME = "final_search_visualizer.py"
FINAL_SEARCH_TEST_FILENAME = "final_search_test.py"
DEFAULT_MAX_CONCURRENT_QUERIES = 3
DEFAULT_CONTEXT_EXPANSION_CHUNKS = 5

MATCH_TYPE_SYNTACTIC = "syntactic"
MATCH_TYPE_SEMANTIC = "semantic"
FORMAT_MATCHED_CONCEPT = "{concept} ({match_type})"
