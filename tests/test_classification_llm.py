# %%
import unittest
import tempfile
import os
from pathlib import Path
from sic_soc_llm import setup_logging, check_file_exists
from sic_soc_llm.llm import ClassificationLLM
from sic_soc_llm.embedding import EmbeddingHandler
from langchain.llms.fake import FakeListLLM
from sic_soc_llm.data_models.response_model import SocResponse, SicResponse, RagResponse

# %%
FAKE_LLM = FakeListLLM(responses=["something not structured"])


# %%
class TestClassificationLLM(unittest.TestCase):
    def setUp(self):
        # Create a temporary testing directory
        self.cwd = os.getcwd()
        self.temp_dir = tempfile.TemporaryDirectory()
        os.chdir(self.temp_dir.name)
        self.llm = ClassificationLLM(llm=FAKE_LLM, verbose=True)

    def tearDown(self):
        # Clean up the temporary testing directory
        self.temp_dir.cleanup()
        os.chdir(self.cwd)

    def test_logging_setup(self):
        # check new file exists in tmp log dir
        logger = setup_logging(log_dir=Path(self.temp_dir.name) / "logs")
        logger.info("TestClassificationLLM: Setting up test")
        log_files = list((Path(self.temp_dir.name) / "logs").iterdir())
        self.assertEqual(len(log_files), 1)

    def test_classification_llm_initialised(self):
        # Test if the ClassificationLLM instance is initialized correctly
        self.assertIsInstance(self.llm, ClassificationLLM)

    def test_prompt_candidate_list_empty(self):
        out = self.llm._prompt_candidate_list([])
        print(out)
        self.assertEqual(out, "")

    def test_get_soc_code(self):
        # Test if the SOC code is returned correctly
        soc_code = self.llm.get_soc_code(
            job_title="science teacher",
            job_description="",
            manage_others=False,
            level_of_education="Other",
            industry_descr="",
        )
        self.assertIsInstance(soc_code, SocResponse)

    def test_get_sic_code(self):
        # Test if the SIC code is returned correctly
        sic_code = self.llm.get_sic_code(
            industry_descr="secondary school",
            job_title="teacher",
            job_description="",
        )
        self.assertIsInstance(sic_code, SicResponse)

    def test_sic_empty_embed_error(self):
        print(Path.cwd())
        resp = self.llm.rag_sic_code(industry_descr="secondary school")
        assert resp[0].reasoning.startswith("Error")

    def test_rag_empty_embed_error(self):
        resp = self.llm.rag_general_code(respondent_data={"descr": "school"})
        assert resp[0].reasoning.startswith("Error")


# %%
class TestGeneralRAG(unittest.TestCase):
    def setUp(self):
        embed = EmbeddingHandler(db_dir=None)
        file_path = check_file_exists("toy_index.txt")
        with open(file_path, "r") as file_object:
            embed.embed_index(from_empty=True, file_object=file_object)
        self.llm = ClassificationLLM(
            llm=FAKE_LLM, embedding_handler=embed, verbose=True
        )

    def tearDown(self):
        pass

    def test_rag_general_code(self):
        # Test if the RAG code is returned correctly
        rag_code, shortlist = self.llm.rag_general_code(
            respondent_data={"characteristics": "gills"}
        )
        self.assertIsInstance(rag_code, RagResponse)
        assert len(shortlist) == 4
