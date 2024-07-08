from langchain.prompts.prompt import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from sic_soc_llm.data_models.response_model import SocResponse, SicResponse, RagResponse
from sic_soc_llm import get_config

config = get_config()

_core_prompt = """You are a conscientious classification assistant of respondent data
for the use in the UK official statistics. Respondent data may be in English or Welsh,
but you always respond in British English."""

_soc_template = """"Given the respondent data (that may include all or some of
job title, job description, level of education, line management responsibilities,
and company's main activity) your task is to determine
the UK SOC (Standard Occupational Classification) code for this job if it can be
determined. If the code cannot be determined, identify the additional information
needed to determine it. Make sure to use the provided 2020 SOC index.

===Respondent Data===
- Job Title: {job_title}
- Job Description: {job_description}
- Level of Education: {level_of_education}
- Line Management Responsibilities: {manage_others}
- Company's main activity: {industry_descr}

===Output Format===
{format_instructions}

===2020 SOC Index===
{soc_index}
"""

with open(config["lookups"]["soc_condensed"]) as f:
    soc_index = f.read()


parser = PydanticOutputParser(pydantic_object=SocResponse)

SOC_PROMPT_PYDANTIC = PromptTemplate.from_template(
    template=_core_prompt + _soc_template,
    partial_variables={
        "format_instructions": parser.get_format_instructions(),
        "soc_index": soc_index,
    },
)

# TODO include SIC/SOC definitions, coding guidance, the concept/question phrasing?


_sic_template = """"Given the respondent's description of the main activity their
company does, their job title and job description, your task is to determine
the UK SIC (Standard Industry Classification) code for this company if it can be
determined to the division (two-digit) level. If the code cannot be determined,
identify the additional information needed to determine it.
Make sure to use the provided 2007 SIC Index.

===Respondent Data===
- Company's main activity: {industry_descr}
- Job Title: {job_title}
- Job Description: {job_description}

===Output Format===
{format_instructions}

===2007 SIC Index===
{sic_index}
"""

with open(config["lookups"]["sic_condensed"]) as f:
    sic_index = f.read()


parser = PydanticOutputParser(pydantic_object=SicResponse)

SIC_PROMPT_PYDANTIC = PromptTemplate.from_template(
    template=_core_prompt + _sic_template,
    partial_variables={
        "format_instructions": parser.get_format_instructions(),
        "sic_index": sic_index,
    },
)


_sic_template_rag = """"Given the respondent's description of the main activity their
company does, their job title and job description (which may be different then the
main company activity), your task is to determine the UK SIC (Standard Industry
Classification) code for this company if it can be determined.
Make sure to use the provided Relevant subset of UK SIC 2007. If the code cannot be
determined (or is likely not included in the provided subset), identify the additional
information needed to determine it and a list of most likely codes.

===Respondent Data===
- Company's main activity: {industry_descr}
- Job Title: {job_title}
- Job Description: {job_description}

===Relevant subset of UK SIC 2007===
{sic_index}

===Output Format===
{format_instructions}

===Output===
"""

SIC_PROMPT_RAG = PromptTemplate.from_template(
    template=_core_prompt + _sic_template_rag,
    partial_variables={
        "format_instructions": parser.get_format_instructions(),
    },
)

_general_template_rag = """"Given the respondent's data, your task is to determine
the classification code. Make sure to use the provided Relevant subset of
classification index and select codes from this list only.
If the code cannot be determined (or not included in the provided subset),
do not provide final code, instead identify the additional information needed
to determine the correct code and suggest few most likely codes.

===Respondent Data===
{respondent_data}

===Relevant subset of classification index===
{classification_index}

===Output Format===
{format_instructions}

===Output===
"""
parser = PydanticOutputParser(pydantic_object=RagResponse)

GENERAL_PROMPT_RAG = PromptTemplate.from_template(
    template=_core_prompt + _general_template_rag,
    partial_variables={
        "format_instructions": parser.get_format_instructions(),
    },
)


class PromptTemplates:
    """Class to store prompt templates for SOC and SIC classification tasks.

    Each prompt template includes the necessary variables and formatting instructions
    to generate the prompt. The module also includes the necessary imports and
    configurations to generate the prompts.

    Attributes:
        SOC_PROMPT_PYDANTIC (PromptTemplate): Prompt template for determining SOC codes
            based on respondent's data.
        SIC_PROMPT_PYDANTIC (PromptTemplate): Prompt template for determining SIC codes
            based on respondent's data.
        SIC_PROMPT_RAG (PromptTemplate): Prompt template for determining SIC codes based
            on respondent's data, with a relevant subset of SIC codes provided.
        GENERAL_PROMPT_RAG (PromptTemplate): Prompt template for determining custom
            classification codes based on respondent data, with a relevant subset of
            codes provided.
    """

    def __init__(self):
        self.SOC_PROMPT_PYDANTIC = SOC_PROMPT_PYDANTIC
        self.SIC_PROMPT_PYDANTIC = SIC_PROMPT_PYDANTIC
        self.SIC_PROMPT_RAG = SIC_PROMPT_RAG
        self.GENERAL_PROMPT_RAG = GENERAL_PROMPT_RAG
