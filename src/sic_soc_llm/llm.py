import logging
import numpy as np
from functools import lru_cache
from collections import defaultdict
from typing import Optional, Union
from langchain.chains.llm import LLMChain
from langchain.output_parsers import PydanticOutputParser
from langchain_google_vertexai import VertexAI
from langchain_openai import ChatOpenAI

from sic_soc_llm import get_config
from sic_soc_llm.prompt import (
    SOC_PROMPT_PYDANTIC,
    SIC_PROMPT_PYDANTIC,
    SIC_PROMPT_RAG,
    GENERAL_PROMPT_RAG,
)
from sic_soc_llm.data_models.response_model import SocResponse, SicResponse, RagResponse
from sic_soc_llm.embedding import EmbeddingHandler
from sic_soc_llm.data_models.sicDB import sic_meta
from sic_soc_llm.data_models.sic_data_access import load_sic_index, load_sic_structure
from sic_soc_llm.data_models.sic_hierarchy import load_hierarchy

logger = logging.getLogger(__name__)
config = get_config()


class ClassificationLLM:
    """
    Wraps the logic for using an LLM to classify respondent's data
    based on provided index. Includes direct (one-shot) generative llm
    method and Retrieval Augmented Generation (RAG).

    Args:
        model_name (str): Name of the model. Defaults to the value in the `config` file.
            Used if no LLM object is passed.
        llm (LLM): LLM to use. Optional.
        embedding_handler (EmbeddingHandler): Embedding handler. Optional.
            If None a default embedding handler is retrieved based on config file.
        max_tokens (int): Maximum number of tokens to generate. Defaults to 1600.
        temperature (float): Temperature of the LLM model. Defaults to 0.0.
        verbose (bool): Whether to print verbose output. Defaults to False.
        openai_api_key (str): OpenAI API key. Optional, but needed for OpenAI models.
    """

    def __init__(
        self,
        model_name: str = config["llm"]["llm_model_name"],
        llm: Optional[Union[VertexAI, ChatOpenAI]] = None,
        embedding_handler: Optional[EmbeddingHandler] = None,
        max_tokens: int = 1600,
        temperature: float = 0.0,
        verbose: bool = False,
        openai_api_key: Optional[str] = None,
    ):
        """
        Initialises the ClassificationLLM object.
        """
        if llm is not None:
            self.llm = llm
        else:
            if model_name.startswith("text-") or model_name.startswith("gemini"):
                self.llm = VertexAI(
                    model_name=model_name,
                    max_output_tokens=max_tokens,
                    temperature=temperature,
                    location="europe-west2",
                )
            elif model_name.startswith("gpt"):
                if openai_api_key is None:
                    raise NotImplementedError("Need to provide an OpenAI API key")
                self.llm = ChatOpenAI(
                    model=model_name,
                    openai_api_key=openai_api_key,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
            else:
                raise NotImplementedError("Unsupported model family")

        self.soc_prompt = SOC_PROMPT_PYDANTIC
        self.sic_prompt = SIC_PROMPT_PYDANTIC
        self.sic_meta = sic_meta
        self.sic_prompt_rag = SIC_PROMPT_RAG
        self.general_prompt_rag = GENERAL_PROMPT_RAG
        self.embed = embedding_handler
        self.sic = None
        self.verbose = verbose

    def _load_embedding_handler(self):
        """
        Loads the default embedding handler according to the 'config' file.
        Expects an existing and populated persistent vector store.

        Raises:
            ValueError: If the retrieved embedding handler has an empty vector store.
                Please embed an index before using it in the ClassificationLLM.
        """
        logger.info(
            """Loading default embedding handler according to 'config' file.
            Expecting existing & populated persistent vector store."""
        )
        self.embed = EmbeddingHandler()
        if self.embed._index_size == 0:
            raise ValueError(
                """The retrieved embedding handler has an empty vector store.
                Please embed an index before using in the ClassificationLLM."""
            )

    @lru_cache
    def get_soc_code(
        self,
        job_title: str,
        job_description: str,
        level_of_education: str,
        manage_others: bool,
        industry_descr: str,
    ) -> SocResponse:
        """
        Generates a SOC classification based on respondent's data
        using a whole condensed index embedded in the query.

        Args:
            job_title (str): The title of the job.
            job_description (str): The description of the job.
            level_of_education (str): The level of education required for the job.
            manage_others (bool): Indicates whether the job involves managing others.
            industry_descr (str): The description of the industry.

        Returns:
            SocResponse: The generated response to the query.

        Raises:
            ValueError: If there is an error parsing the response from the LLM model.

        """
        chain = LLMChain(llm=self.llm, prompt=self.soc_prompt)
        response = chain.invoke(
            {
                "job_title": job_title,
                "job_description": job_description,
                "level_of_education": level_of_education,
                "manage_others": manage_others,
                "industry_descr": industry_descr,
            },
            return_only_outputs=True,
        )
        if self.verbose:
            logger.debug(f"{response=}")
        # Parse the output to desired format with one retry
        parser = PydanticOutputParser(pydantic_object=SocResponse)
        try:
            validated_answer = parser.parse(response["text"])
        except Exception as parse_error:
            logger.error(f"Unable to parse llm response: {str(parse_error)}")
            reasoning = (
                f'ERROR parse_error=<{parse_error}>, response=<{response["text"]}>'
            )
            validated_answer = SocResponse(
                codable=False, soc_candidates=[], reasoning=reasoning
            )

        return validated_answer

    @lru_cache
    def get_sic_code(
        self,
        industry_descr: str,
        job_title: str,
        job_description: str,
    ) -> SicResponse:
        """
        Generates a SIC classification based on respondent's data
        using a whole condensed index embedded in the query.

        Args:
            industry_descr (str): Description of the industry.
            job_title (str): Title of the job.
            job_description (str): Description of the job.

        Returns:
            SicResponse: Generated response to the query.
        """

        chain = LLMChain(llm=self.llm, prompt=self.sic_prompt)
        response = chain.invoke(
            {
                "industry_descr": industry_descr,
                "job_title": job_title,
                "job_description": job_description,
            },
            return_only_outputs=True,
        )
        if self.verbose:
            logger.debug(f"{response=}")
        # Parse the output to desired format with one retry
        parser = PydanticOutputParser(pydantic_object=SicResponse)
        try:
            validated_answer = parser.parse(response["text"])
        except ValueError as parse_error:
            logger.debug(
                f"Retrying llm response parsing due to an error: {parse_error}"
            )
            logger.error(f"Unable to parse llm response: {str(parse_error)}")

            reasoning = (
                f'ERROR parse_error=<{parse_error}>, response=<{response["text"]}>'
            )
            validated_answer = SicResponse(
                codable=False,
                sic_candidates=[],
                reasoning=reasoning,
            )

        return validated_answer

    def _prompt_candidate(
        self, code: str, activities: list[str], include_all: bool = False
    ) -> str:
        """Reformat the candidate activities for the prompt.

        Args:
            code (str): The code for the item.
            activities (list[str]): The list of example activities.
            include_all (bool, optional): Whether to include all the sic metadata.

        Returns:
            str: A formatted string containing the code, title, and example activities.
        """
        if self.sic is None:
            sic_index_df = load_sic_index(config["lookups"]["sic_index"])
            sic_df = load_sic_structure(config["lookups"]["sic_structure"])
            self.sic = load_hierarchy(sic_df, sic_index_df)

        item = self.sic[code]
        txt = "{" + f"Code: {item.numeric_string_padded()}, Title: {item.description}"
        txt += f", Example activities: {', '.join(activities)}"
        if include_all:
            if item.sic_meta.detail:
                txt += f", Details: {item.sic_meta.detail}"
            if item.sic_meta.includes:
                txt += f", Includes: {', '.join(item.sic_meta.includes)}"
            if item.sic_meta.excludes:
                txt += f", Excludes: {', '.join(item.sic_meta.excludes)}"
        return txt + "}"

    def _prompt_candidate_list(
        self,
        short_list: list[dict],
        chars_limit: int = 14000,
        candidates_limit: int = 5,
        activities_limit: int = 3,
        code_digits: int = 5,
    ) -> str:
        """Create candidate list for the prompt based on the given parameters.

        This method takes a structured list of candidates and generates a short
        string list based on the provided parameters. It filters the candidates
        based on the code digits and activities limit, and shortens the list to
        fit the character limit.

        Args:
            short_list (list[dict]): A list of candidate dictionaries.
            chars_limit (int, optional): The character limit for the generated
                prompt. Defaults to 14000.
            candidates_limit (int, optional): The maximum number of candidates
                to include in the prompt. Defaults to 5.
            activities_limit (int, optional): The maximum number of activities
                to include for each code. Defaults to 3.
            code_digits (int, optional): The number of digits to consider from
                the code for filtering candidates. Defaults to 5.

        Returns:
            str: The generated candidate list for the prompt.
        """
        a = defaultdict(list)
        for item in short_list:
            if item["title"] not in a[item["code"][:code_digits]]:
                a[item["code"][:code_digits]].append(item["title"])

        sic_candidates = [
            self._prompt_candidate(code, activities[:activities_limit])
            for code, activities in a.items()
        ][:candidates_limit]

        if chars_limit:
            chars_count = np.cumsum([len(x) for x in sic_candidates])
            nn = sum([x <= chars_limit for x in chars_count])
            if nn < len(sic_candidates):
                logger.warning(
                    "Shortening list of candidates to fit token limit "
                    + f"from {len(sic_candidates)} to {nn}"
                )
                sic_candidates = sic_candidates[:nn]

        return "\n".join(sic_candidates)

    def rag_sic_code(  # noqa: C901
        self,
        industry_descr: str,
        job_title: str = None,
        job_description: str = None,
        expand_search_terms: bool = True,
        code_digits: int = 5,
        candidates_limit: int = 5,
    ) -> SicResponse:
        """
        Generates a SIC classification based on respondent's data using RAG approach.

        Args:
            industry_descr (str): The description of the industry.
            job_title (str, optional): The job title. Defaults to None.
            job_description (str, optional): The job description. Defaults to None.
            expand_search_terms (bool, optional): Whether to expand the search terms
                to include job title and description. Defaults to True.
            code_digits (int, optional): The number of digits in the generated
                SIC code. Defaults to 5.
            candidates_limit (int, optional): The maximum number of SIC code candidates
                to consider. Defaults to 5.

        Returns:
            SicResponse: The generated response to the query.

        Raises:
            ValueError: If there is an error during the parsing of the response.
            ValueError: If the default embedding handler is required but
                not loaded correctly.

        """

        def prep_call_dict(industry_descr, job_title, job_description, sic_codes):
            # Helper function to prepare the call dictionary
            is_job_title_present = job_title is None or job_title in {"", " "}
            job_title = "Unknown" if is_job_title_present else job_title

            is_job_description_present = job_description is None or job_description in {
                "",
                " ",
            }
            job_description = (
                "Unknown" if is_job_description_present else job_description
            )

            call_dict = {
                "industry_descr": industry_descr,
                "job_title": job_title,
                "job_description": job_description,
                "sic_index": sic_codes,
            }
            return call_dict

        if self.embed is None:
            try:
                self._load_embedding_handler()
            except ValueError as err:
                logger.exception(err)
                logger.warning("Error: Empty embedding vector store, exit early")
                validated_answer = SicResponse(
                    codable=False,
                    sic_candidates=[],
                    reasoning="Error, Empty embedding vector store, exit early",
                )
                return validated_answer, None, None

        # Retrieve relevant SIC codes and format them for prompt
        if expand_search_terms:
            short_list = self.embed.search_index_multi(
                query=[industry_descr, job_title, job_description]
            )
        else:
            short_list = self.embed.search_index(query=industry_descr)

        sic_codes = self._prompt_candidate_list(
            short_list, code_digits=code_digits, candidates_limit=candidates_limit
        )

        call_dict = prep_call_dict(
            industry_descr=industry_descr,
            job_title=job_title,
            job_description=job_description,
            sic_codes=sic_codes,
        )

        if self.verbose:
            final_prompt = self.sic_prompt_rag.format(**call_dict)
            logger.debug(final_prompt)

        chain = LLMChain(llm=self.llm, prompt=self.sic_prompt_rag)

        try:
            response = chain.invoke(call_dict, return_only_outputs=True)
        except ValueError as err:
            logger.exception(err)
            logger.warning("Error from LLMChain, exit early")
            validated_answer = SicResponse(
                codable=False,
                sic_candidates=[],
                reasoning="Error from LLMChain, exit early",
            )
            return validated_answer, short_list, call_dict

        if self.verbose:
            logger.debug(f"{response=}")

        # Parse the output to the desired format
        parser = PydanticOutputParser(pydantic_object=SicResponse)
        try:
            validated_answer = parser.parse(response["text"])
        except ValueError as parse_error:
            logger.exception(parse_error)
            logger.warning(f"Failed to parse response:\n{response['text']}")

            reasoning = (
                f'ERROR parse_error=<{parse_error}>, response=<{response["text"]}>'
            )
            validated_answer = SicResponse(
                codable=False,
                sic_candidates=[],
                reasoning=reasoning,
            )

        return validated_answer, short_list, call_dict

    def rag_general_code(  # noqa: C901
        self,
        respondent_data: dict,
        candidates_limit: int = 7,
    ) -> RagResponse:
        """
        Generates a classification answer based on respondent's data
        using RAG and custom index.

        Args:
            respondent_data (dict): A dictionary containing respondent data.
            candidates_limit (int, optional): The maximum number of candidate
                codes to consider. Defaults to 7.

        Returns:
            RagResponse: The generated classification response to the query.

        Raises:
            ValueError: If there is an error during the parsing of the response.
            ValueError: If the default embedding handler is required but
                not loaded correctly.
        """

        if self.embed is None:
            try:
                self._load_embedding_handler()
            except ValueError as err:
                logger.exception(err)
                logger.warning("Error: Empty embedding vector store, exit early")
                validated_answer = RagResponse(
                    codable=False,
                    alt_candidates=[],
                    reasoning="Error: Empty embedding vector store, exit early",
                )
                return validated_answer, None

        # Retrieve relevant SIC codes and format them for prompt
        short_list = self.embed.search_index_multi(query=respondent_data.values())

        candidate_codes = (
            "{"
            + "}, /n{".join(
                [
                    "Code: " + x["code"] + ", Description: " + x["title"]
                    for x in short_list[:candidates_limit]
                ]
            )
            + "}"
        )

        if self.verbose:
            final_prompt = self.general_prompt_rag.format(
                respondent_data=str(respondent_data),
                classification_index=candidate_codes,
            )
            logger.debug(final_prompt)

        chain = LLMChain(llm=self.llm, prompt=self.general_prompt_rag)

        try:
            response = chain.invoke(
                {
                    "respondent_data": str(respondent_data),
                    "classification_index": candidate_codes,
                },
                return_only_outputs=True,
            )
        except ValueError as err:
            logger.exception(err)
            logger.warning("Error from LLMChain, exit early")
            validated_answer = RagResponse(
                codable=False,
                alt_candidates=[],
                reasoning="Error from LLMChain, exit early",
            )
            return validated_answer, short_list

        if self.verbose:
            logger.debug(f"llm_response={response}")

        # Parse the output to desired format
        parser = PydanticOutputParser(pydantic_object=RagResponse)
        try:
            validated_answer = parser.parse(response["text"])
        except ValueError as parse_error:
            logger.exception(parse_error)
            logger.warning(f"Failed to parse response:\n{response['text']}")

            reasoning = (
                f'ERROR parse_error=<{parse_error}>, response=<{response["text"]}>'
            )
            validated_answer = RagResponse(
                codable=False,
                alt_candidates=[],
                reasoning=reasoning,
            )

        return validated_answer, short_list
