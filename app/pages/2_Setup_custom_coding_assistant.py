# %%
import streamlit as st
from io import StringIO
from importlib import resources
from sic_soc_llm.embedding import EmbeddingHandler

# %%
st.set_page_config(
    page_title="Custom LLM coding assistant",
    page_icon="🐥",
)


def main():
    # File upload
    st.subheader("1. Upload Classification Index", divider=True)
    index_file = st.file_uploader("Upload a file", type=["txt"])
    st.markdown(
        """The index file should be a text file with one classification entry
        per line in the format `code: description`.
        You can download an example index file for reference:"""
    )
    # Put the download buttons on one row with different spacing
    col1, col2, col3, col4 = st.columns([1.3, 2.2, 2, 2])
    col1.download_button(
        "Toy index",
        data=(
            resources.files("sic_soc_llm.example_data") / "toy_index.txt"
        ).read_bytes(),
        file_name="toy_index.txt",
        mime="text/plain",
    )
    col2.download_button(
        "COICOP 5d condensed",
        data=(
            resources.files("sic_soc_llm.example_data") / "coicop_5d_condensed.txt"
        ).read_bytes(),
        file_name="coicop_5d_condensed.txt",
        mime="text/plain",
    )
    col3.download_button(
        "SOC 4d condensed",
        data=(
            resources.files("sic_soc_llm.example_data") / "soc_4d_condensed.txt"
        ).read_bytes(),
        file_name="soc_4d_condensed.txt",
        mime="text/plain",
    )
    col4.download_button(
        "SIC 4d condensed",
        data=(
            resources.files("sic_soc_llm.example_data") / "sic_4d_condensed.txt"
        ).read_bytes(),
        file_name="sic_4d_condensed.txt",
        mime="text/plain",
    )

    if index_file is not None:
        try:
            # Embed the index
            embedding_handler = EmbeddingHandler(db_dir=None)
            embedding_handler.embed_index(
                file_object=StringIO(index_file.getvalue().decode("utf-8"))
            )
            # Display size of embedded index
            coll_size = embedding_handler._index_size
            if coll_size > 0:
                st.session_state.custom_embed = embedding_handler
                st.success(
                    f"Index embedding successful. Embedded index of size {coll_size}."
                )
            else:
                st.warning(
                    "Index embedding failed. Please check the index file and try again."
                )
        except Exception as e:
            st.error(
                f"""Index embedding failed. Please check the index file and try again.
                       Error: {e}"""
            )
    else:
        if st.session_state.get("custom_embed", None) is not None:
            coll_size = st.session_state.custom_embed._index_size
            st.info(
                f"""A custom index has been embedded previously with
                {coll_size} entries. Uploading new index will replace it."""
            )

    # Specify respondent data fields
    st.subheader("2. Specify respondent data fields", divider=True)
    # Specify respondent data fields
    fields = st.text_input("Enter respondent data fields (separated by commas)")
    if fields:
        field_list = [s.strip() for s in fields.split(",")]
        # Save the custom fields in session state
        st.session_state.custom_fields = field_list
        st.success(f"Respondent data fields registered: {field_list}")
    else:
        if st.session_state.get("custom_fields", None) is not None:
            st.info(
                f"""A custom respondent data fields previously registered:
                {st.session_state.custom_fields}."""
            )


if __name__ == "__main__":
    main()

# %%
