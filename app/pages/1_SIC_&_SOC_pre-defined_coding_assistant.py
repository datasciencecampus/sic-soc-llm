import dotenv
import streamlit as st
from sic_soc_llm.llm import ClassificationLLM
from sic_soc_llm.embedding import EmbeddingHandler

st.set_page_config(
    page_title="SIC/SOC LLM assistant",
    page_icon="🐥",
)

if st.session_state.get("open_ai_key") is None:
    try:
        openai_api_key = dotenv.dotenv_values(".env")["OPENAI_API_KEY"]
        st.session_state["open_ai_key"] = openai_api_key
    except Exception as e:
        st.session_state["open_ai_key"] = str(e)

embed = EmbeddingHandler()  # Loaded once, used twice
uni_chat = ClassificationLLM("gemini-pro", embedding_handler=embed)  # "text-unicorn"
gpt_chat = ClassificationLLM(
    "gpt-4", openai_api_key=st.session_state["open_ai_key"], embedding_handler=embed
)


# Ask the user for the OpenAI API key if they want to use it remotely
ai_key_enter = st.sidebar.text_input(
    "If you want to use GPT, update OpenAI API key",
    value="",
    type="password",
    on_change=None,
)
if ai_key_enter:
    st.session_state["open_ai_key"] = ai_key_enter
    gpt_chat = ClassificationLLM(
        "gpt-4", openai_api_key=st.session_state["open_ai_key"], embedding_handler=embed
    )
    st.sidebar.success("OpenAI API key updated successfully")


# Streamlit app
def main(verbose: bool = True):  # noqa: C901
    st.subheader("LLM assisted SIC/SOC Coding", divider=True)
    st.subheader("Respondent data - survey fields", divider=True)
    # Job Title and Description inputs
    job_title = st.text_input("Job Title")
    job_description = st.text_area("Job Description")
    manage_others = st.toggle("Line management responsibility")

    # Level of Education input
    education_levels = [
        "No formal qualifications",
        "Level 1: one to four GCSE passes (grade A* to C or grade 4 and above)"
        + " and any other GCSEs at other grades, or equivalent qualifications",
        "Level 2: five or more GCSE passes (grade A* to C or grade 4 and above)"
        + " or equivalent qualifications",
        "Level 3: two or more A Levels or equivalent qualifications",
        "Level 4 or above: Higher National Certificate, Higher National Diploma,"
        + " Bachelor's degree, or post-graduate qualifications",
        "Other qualifications, of unknown level",
    ]
    level_of_education = st.selectbox("Level of Education", education_levels)
    industry_descr = st.text_area("What does the organisation mainly make or do?")

    buttons = {}
    st.subheader("Validate using LLM (one-shot)", divider=True)
    col1, col2 = st.columns(2)
    buttons["soc_uni"] = col1.button(
        "Validate input for SOC using Gemini ⛋"
    )  # Palm2 🦄")
    buttons["soc_gpt"] = col2.button("Validate input for SOC using GPT ⚛")
    buttons["sic_uni"] = col1.button(
        "Validate input for SIC using Gemini ⛋"
    )  # Palm2  🦄")
    buttons["sic_gpt"] = col2.button("Validate input for SIC using GPT ⚛")
    # Add buttons for rag
    st.subheader("Validate SIC using LLM (RAG)", divider=True)
    col3, col4 = st.columns(2)
    buttons["rag_uni"] = col3.button(
        "Validate input for SIC using RAG Gemini ⛋"
    )  # Palm2  🦄")
    buttons["rag_gpt"] = col4.button("Validate input for SIC using RAG GPT ⚛")

    if any(buttons.values()):
        if job_title or job_description or industry_descr:
            if buttons["soc_uni"]:
                response = uni_chat.get_soc_code(
                    job_title,
                    job_description,
                    level_of_education,
                    manage_others,
                    industry_descr,
                )
            elif buttons["soc_gpt"]:
                response = gpt_chat.get_soc_code(
                    job_title,
                    job_description,
                    level_of_education,
                    manage_others,
                    industry_descr,
                )
            elif buttons["sic_uni"]:
                response = uni_chat.get_sic_code(
                    industry_descr, job_title, job_description
                )
            elif buttons["sic_gpt"]:
                response = gpt_chat.get_sic_code(
                    industry_descr, job_title, job_description
                )
            elif buttons["rag_uni"]:
                response, _, _ = uni_chat.rag_sic_code(
                    industry_descr, job_title, job_description
                )
            else:
                response, _, _ = gpt_chat.rag_sic_code(
                    industry_descr, job_title, job_description
                )

            if response.codable & ("soc_code" in response.model_fields):
                st.success(
                    f"👍 Coded as {response.soc_code}: {response.soc_descriptive}"
                )
            elif response.codable & ("sic_code" in response.model_fields):
                st.success(
                    f"👍 Coded as {response.sic_code}: {response.sic_descriptive}"
                )
            else:
                st.warning(f"👆 More details needed: {response.followup}")

            if verbose:
                print(
                    "Input: ",
                    job_title,
                    job_description,
                    manage_others,
                    level_of_education,
                )
                print("Response: ", response)
                st.subheader("Debugging info", divider=True)
                st.json(response.model_dump())
        else:
            st.warning("👆 Please enter something somewhere at least...")


if __name__ == "__main__":
    main()
