import streamlit as st
from sic_soc_llm import setup_logging

logger = setup_logging("streamlit_app")

st.set_page_config(
    page_title="SIC/SOC LLM assistant",
    page_icon="🐥",
)

st.subheader("LLM assisted classification coding", divider=True)

st.markdown(
    """This app/package has been created by the Data Science Campus
    as a proof of concept to evaluate Large Language Models (LLM) potential to assist
    with classification coding.
    It provides an example of using pre-trained LLM models to assist with
    Standard Industrial Classification (SIC) and Standard Occupational Classification
    (SOC) coding. It also provides a way to set up and test a custom index.
    """
)

st.markdown(
    """
    - Source code: [github/datasciencecampus/sic-soc-llm](
        https://github.com/datasciencecampus/sic-soc-llm)
    - Documentation & references:
    [github.io docs](https://datasciencecampus.github.io/sic-soc-llm/docs)
    - Website: [Data Science Campus](https://datasciencecampus.ons.gov.uk/)
    - Email: [Data Science Campus](mailto:datasciencecampus@ons.gov.uk)
    """
)

st.subheader(
    "Use the sidebar on the left to navigate to any of the pages:", divider=True
)
st.markdown(
    """
    1. **SIC & SOC pre-defined coding assistant**

    Enter respondent data into the input fields and press the validate button.
    The response and debugging info will be displayed below.
    Preloaded classification indices are used.

    2. **Setup custom LLM coding assistant**

    You can customise your own classification assistant by uploading your own index and
    specifying survey fields. This will be used in a Retrieval Augmented
    Generation (RAG) pipeline.

    3. **Test custom LLM coding assistant**

    After setting up a custom index and survey fields, you can test
    your custom LLM coding assistant.
    """
)
