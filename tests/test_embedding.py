# %%
import unittest
from sic_soc_llm import check_file_exists
from sic_soc_llm.embedding import EmbeddingHandler


# %%
class TestEmbeddingHandlerToy(unittest.TestCase):
    def setUp(self):
        self.embedding_handler = EmbeddingHandler(db_dir=None)
        file_path = check_file_exists("toy_index.txt")
        with open(file_path, "r") as file_object:
            self.embedding_handler.embed_index(from_empty=True, file_object=file_object)

    def tearDown(self):
        pass

    def test_embed_index_with_file_object(self):
        # Count number of entries
        assert self.embedding_handler._index_size == 4

    def test_search_index(self):
        # Test searching index with a query
        query = "mens best friend"
        results = self.embedding_handler.search_index(query)
        assert results[0]["code"] == "02"

    def test_search_index_multi(self):
        # Test searching index with multiple queries
        queries = ["has gills", "has scales"]
        results = self.embedding_handler.search_index_multi(queries)
        assert len(results) == 8
