# Docker Image may have old sqlite3 version for ChromaDB
import sys
import sqlite3  # noqa:F401

if sys.modules["sqlite3"].sqlite_version_info < (3, 35, 0):
    __import__("pysqlite3")
    sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")

import uuid
import logging
from langchain_community.embeddings import HuggingFaceEmbeddings, VertexAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.docstore.document import Document
from autocorrect import Speller

from sic_soc_llm import get_config
from sic_soc_llm.data_models.sic_data_access import load_sic_index, load_sic_structure
from sic_soc_llm.data_models.sic_hierarchy import load_hierarchy, SIC

logger = logging.getLogger(__name__)
config = get_config()


class EmbeddingHandler:
    """
    Handles embedding operations for the Chroma vector store.

    Args:
        embedding_model_name (str, optional): The name of the embedding model to use.
            Defaults to the value specified in the configuration file.
        db_dir (str, optional): The directory where the vector store database
            is located. Defaults to the value specified in the configuration file.
            If None then the embedding db will be non-persistent.
        k_matches (int, optional): The number of nearest matches to retrieve.
            Defaults to 20.
    """

    def __init__(
        self,
        embedding_model_name: str = config["llm"]["embedding_model_name"],
        db_dir: str = config["llm"]["db_dir"],
        k_matches: int = 20,
    ):
        """
        Initialises the EmbeddingHandler.
        """
        if embedding_model_name.startswith("textembedding-"):
            self.embeddings = VertexAIEmbeddings(model_name=embedding_model_name)
        else:
            self.embeddings = HuggingFaceEmbeddings(model_name=embedding_model_name)
        self.db_dir = db_dir
        self.vector_store = self._create_vector_store()
        self.k_matches = k_matches
        self.spell = Speller()
        self._index_size = self.vector_store._client.get_collection("langchain").count()

    def _create_vector_store(self) -> Chroma:
        """
        Initialises Chroma VectorDB on known DB dir in data.

        Returns:
            Chroma: The LangChain vector store object for Chroma.
        """
        if self.db_dir is None:
            return Chroma(embedding_function=self.embeddings)
        else:
            return Chroma(
                embedding_function=self.embeddings, persist_directory=self.db_dir
            )

    def embed_index(
        self,
        from_empty: bool = True,
        sic: SIC = None,
        file_object=None,
    ):
        """
        Embeds the index entries into the vector store.

        Args:
            from_empty (bool, optional): Whether to drop the current vector store
                content and start fresh.
            sic (SIC, optional): The SIC hierarchy object. If None, the hierarchy
                is loaded from files specified in the config.
            file_object (StringIO object): The index file as StringIO object.
                If provided, the file will be read by line and embedded.
                Each line has expected format of **code**: **description**
        """
        if from_empty:
            self.vector_store._client.delete_collection("langchain")
            self.vector_store = self._create_vector_store()

        docs = []
        ids = []
        if file_object is not None:
            for line in file_object:
                if line:
                    bits = line.split(":", 1)
                    docs.append(
                        Document(
                            page_content=bits[1],
                            metadata={
                                "code": bits[0],
                                "four_digit_code": bits[0][0:4],
                                "two_digit_code": bits[0][0:2],
                            },
                        )
                    )
                    ids.append(str(uuid.uuid3(uuid.NAMESPACE_URL, line)))

        else:
            if sic is None:
                sic_index_df = load_sic_index(config["lookups"]["sic_index"])
                sic_df = load_sic_structure(config["lookups"]["sic_structure"])
                sic = load_hierarchy(sic_df, sic_index_df)

            logger.debug("Loading entries from SIC hierarchy for embedding.")
            for _, row in sic.all_leaf_text().iterrows():
                code = (row["code"].replace(".", "").replace("/", "") + "0")[:5]
                docs.append(
                    Document(
                        page_content=row["text"],
                        metadata={
                            "code": code,
                            "four_digit_code": code[0:4],
                            "two_digit_code": code[0:2],
                        },
                    )
                )
                ids.append(str(uuid.uuid3(uuid.NAMESPACE_URL, row["text"])))

        self.vector_store.add_documents(docs, ids=ids)
        self._index_size = self.vector_store._client.get_collection("langchain").count()
        logger.debug(f"Inserted {len(docs):,} entries into vector embedding database.")

    def search_index(self, query: str, return_dicts: bool = True) -> list[dict]:
        """
        Returns k document chunks with the highest relevance to the query.

        Args:
            query (str): Question for which most relevant index entries
                will be returned.
            return_dicts (bool, optional): If True, data returned as list of
                dictionaries, otherwise as document tuples. Defaults to True.

        Returns:
            List[dict]: List of top k index entries by relevance.
        """
        top_matches = self.vector_store.similarity_search_with_score(
            query=query, k=self.k_matches
        )

        if return_dicts:
            return [
                {"distance": float(doc[1])}
                | {"title": doc[0].page_content}
                | doc[0].metadata
                for doc in top_matches
            ]
        return top_matches

    def search_index_multi(self, query: list[str]) -> list[dict]:
        """
        Returns k document chunks with the highest relevance to the query.

        Args:
            query (list[str]): List of query fields (in priority order) for which
                most relevant index entries will be returned.
                e.g [industry_descr, job_title, job_descr]

        Returns:
            List[dict]: List of top k index entries by relevance.
        """
        query = [x for x in query if x is not None]
        search_terms_list = set()
        for i in range(len(query)):
            x = " ".join(query[: (i + 1)])
            search_terms_list.add(x)
            search_terms_list.add(self.spell(x))
        short_list = [y for x in search_terms_list for y in self.search_index(query=x)]
        return sorted(short_list, key=lambda x: x["distance"])
