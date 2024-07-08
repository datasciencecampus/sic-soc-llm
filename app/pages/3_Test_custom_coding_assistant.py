import dotenv
import streamlit as st
from sic_soc_llm.llm import ClassificationLLM

st.set_page_config(
    page_title="Custom LLM coding assistant",
    page_icon="🐥",
)

if "custom_embed" not in st.session_state or "custom_fields" not in st.session_state:
    # Point user to setup page
    st.write(
        """Custom index and response fields not provided. Please go to the
        **Setup custom LLM coding assistant** page to setup your index and fields.""",
        unsafe_allow_html=True,
    )
    st.stop()

if st.session_state.get("open_ai_key") is None:
    try:
        openai_api_key = dotenv.dotenv_values(".env")["OPENAI_API_KEY"]
        st.session_state["open_ai_key"] = openai_api_key
    except Exception as e:
        st.session_state["open_ai_key"] = str(e)


uni_chat = ClassificationLLM(
    "gemini-pro", embedding_handler=st.session_state.custom_embed
)  # "text-unicorn"
gpt_chat = ClassificationLLM(
    "gpt-4",
    embedding_handler=st.session_state.custom_embed,
    openai_api_key=st.session_state["open_ai_key"],
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
        "gpt-4",
        embedding_handler=st.session_state.custom_embed,
        openai_api_key=st.session_state["open_ai_key"],
    )
    st.sidebar.success("OpenAI API key updated successfully")


fields = st.session_state.custom_fields


# Streamlit app
def main(verbose: bool = True):
    st.subheader("LLM assisted custom coding", divider=True)
    # Ask for specific field inputs from session state
    input_field = {}
    for field in st.session_state.custom_fields:
        input_field[field] = st.text_input(field)

    col1, col2 = st.columns(2)
    rag_uni_button = col1.button("Validate input using Gemini ⛋")  # Palm2 🦄")
    rag_gpt_button = col2.button("Validate input using GPT ⚛")

    if rag_uni_button or rag_gpt_button:
        # Check there is some value in input fields
        print("Input: ", input_field)
        if len(set(input_field.values()).difference({"", None})) > 0:
            if rag_uni_button:
                response, _ = uni_chat.rag_general_code(respondent_data=input_field)
            elif rag_gpt_button:
                response, _ = gpt_chat.rag_general_code(respondent_data=input_field)

            if response.codable:
                st.success(
                    f"👍 Coded as {response.class_code}: {response.class_descriptive}"
                )

            else:
                st.warning(f"👆 More details needed: {response.followup}")

            if verbose:
                print("Input: ", input_field)
                print("Response: ", response)
                st.subheader("Debugging info", divider=True)
                st.json(response.model_dump())
        else:
            st.warning("👆 Please enter something somewhere at least...")


if __name__ == "__main__":
    main()
