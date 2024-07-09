"""Provides data access for key files.

Filepaths are defined in config, see: `sic_soc_llm._config`.
"""

import pandas as pd


def load_sic_index(filepath: str) -> pd.DataFrame:
    """Load the SIC index.

    The SIC index provides a list of around 15,000 activities and
    their associated 5-digit SIC.
    """

    sic_index_df = pd.read_excel(
        filepath,
        sheet_name="Alphabetical Index",
        skiprows=1,
        usecols=["UK SIC 2007", "Activity"],
        dtype=str,
    )

    sic_index_df.columns = [
        col.lower().replace(" ", "_") for col in sic_index_df.columns
    ]

    return sic_index_df


def load_sic_structure(filepath: str) -> pd.DataFrame:
    """Load SIC structure.

    Loads a worksheet with all the levels/names of the UK SIC 2007 hierarchy.
    """

    sic_df = pd.read_excel(
        filepath,
        sheet_name="reworked structure",
        usecols=[
            "Description",
            "SECTION",
            "Most disaggregated level",
            "Level headings",
        ],
        dtype=str,
    )

    sic_df.columns = [col.lower().replace(" ", "_") for col in sic_df.columns]

    for col in sic_df.columns:
        sic_df[col] = sic_df[col].str.strip()

    return sic_df
