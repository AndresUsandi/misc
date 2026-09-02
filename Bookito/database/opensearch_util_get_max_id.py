from opensearchpy import OpenSearch

# Top-of-file Constants
DEFAULT_MAX_ID = 0
QUERY_SIZE_ZERO = 0

KEY_SIZE = "size"
KEY_AGGS = "aggs"
KEY_MAX_ID = "max_id"
KEY_MAX = "max"
KEY_FIELD = "field"
KEY_AGGREGATIONS = "aggregations"
KEY_VALUE = "value"

def get_max_id(client: OpenSearch, index_name: str, id_field: str) -> int:
    """Retrieves the maximum numeric ID present in the specified OpenSearch index."""
    if not client or not client.indices.exists(index=index_name):
        return DEFAULT_MAX_ID

    query = {
        KEY_SIZE: QUERY_SIZE_ZERO,
        KEY_AGGS: {
            KEY_MAX_ID: {KEY_MAX: {KEY_FIELD: id_field}}
        }
    }
    
    try:
        res = client.search(index=index_name, body=query)
        val = res.get(KEY_AGGREGATIONS, {}).get(KEY_MAX_ID, {}).get(KEY_VALUE)
        return int(val) if val is not None else DEFAULT_MAX_ID
    except Exception:
        return DEFAULT_MAX_ID
