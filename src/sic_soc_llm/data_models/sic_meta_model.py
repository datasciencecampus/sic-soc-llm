from pydantic import BaseModel, Field
from typing import List


class ClassificationMeta(BaseModel):
    """
    Represents a classification meta model.

    Attributes:
        code (str): Category code. Either a full code or a partial code for a
            larger hierarchical group.
            Partial code has last digits replaced by 'x'.
        title (str): Short descriptive title of the code category.
        detail (str): Descriptive label of the category associated with the code.
        includes (List[str]): Optional list of titles that should be included
            in this category.
        excludes (List[str]): Optional list of titles that should be excluded
            from this category.
    """

    code: str = Field(
        description="""Category code. Either a full code or a partial code
        for a larger hierarchical group.
        Partial code has last digits replaced by 'x'."""
    )
    title: str = Field(description="Short descriptive title of the code category.")
    detail: str = Field(
        default="",
        description="Descriptive label of the category associated with code.",
    )
    includes: List[str] = Field(
        default=[],
        description="Optional list of titles that should be included in this category",
    )
    excludes: List[str] = Field(
        default=[],
        description="""Optional list of titles that should be excluded from
            this category""",
    )

    def check_code_match(self, subcode: str) -> bool:
        """Check for partial match of the code.
        Discards 1st letter on SIC and then check only valid numbers.

        Args:
            subcode (str): 2-5 digits code for matching

        Returns:
            bool: if partial match found
        """
        n = min(len(self.code.replace("x", "")), len(subcode) + 1)
        return (n > 2) & (self.code[1:n] == subcode[0 : (n - 1)])

    def pretty_print(self, subset_digits=[4, 2]) -> str:
        """Prints nicely the present fields.

        Returns:
            str: _description_
        """
        code = self.code[1:].replace("x", "")
        if len(code) in subset_digits:
            out = "Code " + code + ": " + self.title + ". "
            if self.detail:
                out += self.detail + ". "
            if self.includes:
                out += "Includes " + ", ".join(self.includes) + ". "
            if self.excludes:
                out += "Excludes " + ", ".join(self.excludes) + ". "
        else:
            out = ""
        return out
