import unittest
import sys
import os
import time
from opensearchpy import OpenSearch

# Add package root to search path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from processors.file_processor import FileProcessor
from database.opensearch_manager import BookitoOpenSearchUtil

class TestBookitoIntegration(unittest.TestCase):
    def setUp(self):
        self.host = "localhost"
        self.port = 9200
        self.prefix = "test_integration_"
        self.db_util = BookitoOpenSearchUtil(host=self.host, port=self.port, index_prefix=self.prefix)
        
        try:
            self.client = self.db_util.connect()
            if isinstance(self.client, MagicMock):
                self.skipTest("OpenSearch is mocked; skipping integration test.")
            if not self.client.ping():
                self.skipTest("OpenSearch cluster is not responding to ping.")
            self._cleanup_indices()
        except Exception as e:
            self.skipTest(f"OpenSearch is not available or connection failed: {e}")

    def tearDown(self):
        if os.environ.get('CLEANUP_AFTER_TEST') == '1':
            try:
                self._cleanup_indices()
            except Exception:
                pass

    def _cleanup_indices(self):
        for index in [
            self.db_util.books_index,
            self.db_util.chapters_index,
            self.db_util.chunks_index,
            self.db_util.concepts_index
        ]:
            try:
                if self.client.indices.exists(index=index, request_timeout=60):
                    self.client.indices.delete(index=index, request_timeout=60)
            except Exception as e:
                print(f"Warning cleaning up index {index}: {e}")

    def test_run_pipeline_on_sample_files(self):
        import tempfile
        import zipfile
        
        processor = FileProcessor(opensearch_host=self.host, opensearch_port=self.port, index_prefix=self.prefix)
        with tempfile.TemporaryDirectory() as tmp_dir:
            test_epub_path = os.path.join(tmp_dir, "test_book.epub")
            with zipfile.ZipFile(test_epub_path, 'w') as zf:
                zf.writestr('mimetype', 'application/epub+zip')
                zf.writestr('META-INF/container.xml', '<?xml version="1.0"?><container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles><rootfile full-path="content.opf" media-type="application/oebps-package+xml"/></rootfiles></container>')
                zf.writestr('content.opf', '<?xml version="1.0" encoding="UTF-8"?><package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="BookId"><metadata xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:title>Test Book</dc:title><dc:language>en</dc:language></metadata><manifest><item id="chapter1" href="chapter1.xhtml" media-type="application/xhtml+xml"/></manifest><spine><itemref idref="chapter1"/></spine></package>')
                zf.writestr('chapter1.xhtml', '<?xml version="1.0" encoding="utf-8"?><!DOCTYPE html><html xmlns="http://www.w3.org/1999/xhtml"><head><title>Chapter 1: Machine Learning Overview</title></head><body><h1>Chapter 1: Machine Learning Overview</h1><p>Machine learning is a field of inquiry devoted to understanding and building methods that learn, that is, methods that leverage data to improve performance on some set of tasks.</p><p>Supervised learning algorithms build a mathematical model of a set of data that contains both the inputs and the desired outputs.</p><p>Unsupervised learning algorithms take a set of data that contains only inputs, and find structure in the data, like grouping or clustering of data points.</p></body></html>')
            
            processor.process(tmp_dir)
            
            self.client = self.db_util.connect()
            chap_count = 0
            chunk_count = 0
            for _ in range(10):
                try:
                    self.client.indices.refresh(index=self.db_util.chapters_index, request_timeout=60)
                    self.client.indices.refresh(index=self.db_util.chunks_index, request_timeout=60)
                    chap_count = self.client.count(index=self.db_util.chapters_index, request_timeout=60).get("count", 0)
                    chunk_count = self.client.count(index=self.db_util.chunks_index, request_timeout=60).get("count", 0)
                    if chap_count > 0 and chunk_count > 0:
                        break
                except Exception as ex:
                    print(f"[DEBUG] Refresh/count error: {ex}")
                time.sleep(1)
            
        print(f"Integration results: Chapters={chap_count}, Chunks={chunk_count}")
        self.assertGreater(chap_count, 0)
        self.assertGreater(chunk_count, 0)

if __name__ == '__main__':
    if '--keep-data' in sys.argv:
        os.environ['KEEP_TEST_DATA'] = '1'
        sys.argv.remove('--keep-data')
    unittest.main()
