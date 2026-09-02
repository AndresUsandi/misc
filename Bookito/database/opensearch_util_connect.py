from opensearchpy import OpenSearch

# Top-of-file Constants
DEFAULT_HOST = "localhost"
DEFAULT_PORT = 9200
DEFAULT_TIMEOUT = 60

KEY_HOST = "host"
KEY_PORT = "port"

def connect_opensearch(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT, timeout: int = DEFAULT_TIMEOUT) -> OpenSearch:
    """Creates and returns an OpenSearch client instance."""
    client = OpenSearch(
        hosts=[{KEY_HOST: host, KEY_PORT: port}],
        http_compress=True,
        use_ssl=False,
        verify_certs=False,
        ssl_assert_hostname=False,
        ssl_show_warn=False,
        timeout=timeout
    )
    client.info()
    return client
