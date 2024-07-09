from pydantic import BaseModel, Field, model_validator
from typing import List, Optional


class SocCandidate(BaseModel):
    """
    Represents a candidate SOC code based on provided job title and description.

    Attributes:
        soc_code (str): Plausible SOC code based on the provided job title and
            description.
        soc_descriptive (str): Descriptive label of the SOC category associated
            with soc_code.
        likelihood (float): Likelihood of this soc_code with a value between 0 and 1.
    """

    soc_code: str = Field(
        description="Plausible SOC code based on provided job title and description."
    )
    soc_descriptive: str = Field(
        description="Descriptive label of the SOC category associated with soc_code."
    )
    likelihood: float = Field(
        description="Likelihood of this soc_code with value between 0 and 1."
    )


class SocResponse(BaseModel):
    """Represents a response model for SOC code assignment.

    Attributes:
        codable (bool): True if enough information is provided to decide SOC code,
            False otherwise.
        followup (Optional[str]): Question to ask the user in order to collect
            additional  information to enable reliable SOC assignment.
            Empty if codable=True.
        soc_code (Optional[str]): Full four-digit SOC code assigned based on provided
            job title, description, etc. Empty if codable=False.
        soc_descriptive (Optional[str]): Descriptive label of the SOC category
            associated with soc_code if provided. Empty if codable=False.
        soc_candidates (List[SocCandidate]): List of possible or alternative SOC
            codes that may be applicable with their descriptive label and estimated
            likelihood.
        soc_code_2digits (Optional[str]): First two digits of the hierarchical SOC code
            assigned. This field should be non-empty if the larger (two-digit) group of
            SOC codes can be determined even in cases where additional information is
            needed to code to four digits (for example when all SOC candidates share
            the same first two digits).
        reasoning (str): Step by step reasoning behind classification selected.
            Specifies the information used to assign the SOC code or any additional
            information required to assign a SOC code.
    """

    codable: bool = Field(
        description="""True if enough information is provided to decide
        SOC code, False otherwise."""
    )
    followup: Optional[str] = Field(
        description="""Question to ask user in order to collect additional information
        to enable reliable SOC assignment. Empty if codable=True.""",
        default=None,
    )
    soc_code: Optional[str] = Field(
        description="""Full four digit SOC code assigned based on provided job title,
        description, etc. Empty if codable=False.""",
        default=None,
    )
    soc_descriptive: Optional[str] = Field(
        description="""Descriptive label of the SOC category associated with soc_code
        if provided. Empty if codable=False.""",
        default=None,
    )
    soc_candidates: List[SocCandidate] = Field(
        description="""List of possible or alternative SOC codes that may be applicable
        with their descriptive label and estimated likelihood."""
    )
    soc_code_2digits: Optional[str] = Field(
        description="""First two digits of the hierarchical SOC code assigned.
        This field should be non empty if the larger (two-digit) group of SOC codes
        can be determined even in cases where additional information is needed to
        to code to four digits (for example when all SOC candidates share
        the same first two digits).""",
        default=None,
    )
    reasoning: str = Field(
        description="""Step by step reasoning behind classification selected. Specifies
            the information used to assign the SOC code or any additional information
            required to assign a SOC code."""
    )

    @classmethod
    def soc_code_validator(cls, v):
        # TODO: check for valid codes from some list
        assert v != "", "If codable, then valid soc_code needs to be provided"
        return v

    @model_validator(mode="before")
    @classmethod
    def check_valid_fields(cls, values):
        if values.get("codable"):
            cls.soc_code_validator(values.get("soc_code"))
        else:
            assert (
                values.get("followup") != ""
            ), """If uncodable,
            follow up question needs to be provided."""
        return values


class SicCandidate(BaseModel):
    """Represents a candidate SIC code with associated information.

    Attributes:
        sic_code (str): Plausible SIC code based on the company activity description.
        sic_descriptive (str): Descriptive label of the SIC category associated with
            sic_code.
        likelihood (float): Likelihood of this sic_code with a value between 0 and 1.

    """

    sic_code: str = Field(
        description="Plausible SIC code based on the company activity description."
    )
    sic_descriptive: str = Field(
        description="Descriptive label of the SIC category associated with sic_code."
    )
    likelihood: float = Field(
        description="Likelihood of this sic_code with value between 0 and 1."
    )


class SicResponse(BaseModel):
    """Represents a response model for SIC code assignment.

    Attributes:
        codable (bool): True if enough information is provided to decide SIC code,
            False otherwise.
        followup (Optional[str]): Question to ask user in order to collect additional
            information to enable reliable SIC assignment. Empty if codable=True.
        sic_code (Optional[str]): Full SIC code (to the required number of digits)
            assigned based on the provided company activity description.
            Empty if codable=False.
        sic_descriptive (Optional[str]): Descriptive label of the SIC category
            associated with sic_code if provided. Empty if codable=False.
        sic_candidates (List[SicCandidate]): Short list of less than ten possible or
            alternative sic codes that may be applicable with their descriptive label
            and estimated likelihood.
        sic_code_2digits (Optional[str]): First two digits of the hierarchical SIC
            code assigned. This field should be non empty if the larger (two-digit)
            group of SIC codes can be determined even in cases where additional
            information is needed to code to four digits (for example when all
            SIC candidates share the same first two digits).
        reasoning (str): Specifies the information used to assign the SIC code or any
            additional information required to assign a SIC code.
    """

    codable: bool = Field(
        description="""True if enough information is provided to decide
        SIC code, False otherwise."""
    )
    followup: Optional[str] = Field(
        description="""Question to ask user in order to collect additional information
        to enable reliable SIC assignment. Empty if codable=True.""",
        default=None,
    )
    sic_code: Optional[str] = Field(
        description="""Full SIC code (to the required number of digits) assigned based
        on provided the company activity description.  Empty if codable=False.""",
        default=None,
    )
    sic_descriptive: Optional[str] = Field(
        description="""Descriptive label of the SIC category associated with sic_code
        if provided. Empty if codable=False.""",
        default=None,
    )
    sic_candidates: List[SicCandidate] = Field(
        description="""Short list of less than ten possible or alternative SIC codes
        that may be applicable with their descriptive label and estimated likelihood."""
    )

    reasoning: str = Field(
        description="""Step by step reasoning behind classification selected. Specifies
            the information used to assign the SIC code or any additional information
            required to assign a SIC code."""
    )

    @classmethod
    def sic_code_validator(cls, v):
        # TODO: check for valid codes from some list
        assert v != "", "If codable, then valid sic_code needs to be provided"
        return v

    @model_validator(mode="before")
    @classmethod
    def check_valid_fields(cls, values):
        if values.get("codable"):
            cls.sic_code_validator(values.get("sic_code"))
        else:
            assert (
                values.get("followup") != ""
            ), """If uncodable,
            follow up question needs to be provided."""
        return values


class RagCandidate(BaseModel):
    """Represents a candidate classification code with associated information.

    Attributes:
        class_code (str): Plausible classification code based on the respondent's data.
        class_descriptive (str): Descriptive label of the classification category
            associated with class_code.
        likelihood (float): Likelihood of this class_code with a value between 0 and 1.

    """

    class_code: str = Field(
        description="Plausible classification code based on the respondent's data."
    )
    class_descriptive: str = Field(
        description="""Descriptive label of the classification category
        associated with class_code."""
    )
    likelihood: float = Field(
        description="Likelihood of this class_code with value between 0 and 1."
    )


class RagResponse(BaseModel):
    """Represents a response model for classification code assignment.

    Attributes:
        codable (bool): True if enough information is provided to decide
            classification code, False otherwise.
        followup (Optional[str]): Question to ask user in order to collect
            additional information to enable reliable classification assignment.
            Empty if codable=True.
        class_code (Optional[str]): Full classification code (to the required
            number of digits) assigned based on provided respondent's data.
            Empty if codable=False.
        class_descriptive (Optional[str]): Descriptive label of the classification
            category associated with class_code if provided.
            Empty if codable=False.
        alt_candidates (List[RagCandidate]): Short list of less than ten possible
            or alternative classification codes that may be applicable with their
            descriptive label and estimated likelihood.
        reasoning (str): Step by step reasoning behind the classification selected.
            Specifies the information used to assign the SIC code or any additional
            information required to assign a SIC code.
    """

    codable: bool = Field(
        description="""True if enough information is provided to decide
        classification code, False otherwise."""
    )
    followup: Optional[str] = Field(
        description="""Question to ask user in order to collect additional information
        to enable reliable classification assignment. Empty if codable=True.""",
        default=None,
    )
    class_code: Optional[str] = Field(
        description="""Full classification code (to the required number of digits)
        assigned based on provided respondent's data. Empty if codable=False.""",
        default=None,
    )
    class_descriptive: Optional[str] = Field(
        description="""Descriptive label of the classification category associated
        with class_code if provided. Empty if codable=False.""",
        default=None,
    )
    alt_candidates: List[RagCandidate] = Field(
        description="""Short list of less than ten possible or alternative
        classification codes that may be applicable with their descriptive label
        and estimated likelihood."""
    )
    reasoning: str = Field(
        description="""Step by step reasoning behind classification selected. Specifies
            the information used to assign the SIC code or any additional information
            required to assign a SIC code."""
    )
