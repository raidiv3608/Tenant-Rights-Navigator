import streamlit as st

from src.pdf_loader import extract_pages_from_pdf
from src.chunker import chunk_pages
from src.embeddings import EmbeddingModel
from src.vector_store import VectorStore
from src.llm import GeminiLLM


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Tenant Rights Navigator",
    page_icon="⚖️",
    layout="wide"
)


# ============================================================
# TITLE
# ============================================================

st.title("⚖️ Tenant Rights Navigator")

st.markdown(
    """
    **AI-powered legal information assistant**

    Ask questions about the **Karnataka Rent Act, 1999** and
    receive answers grounded in the retrieved legislation.
    """
)

st.divider()


# ============================================================
# CONFIGURATION
# ============================================================

PDF_PATH = "data/legislation/karnataka/34 of 2001 (E).pdf"


# ============================================================
# LOAD DATA AND MODELS
# ============================================================

@st.cache_resource
def load_navigator():

    # --------------------------------------------------------
    # Load persistent vector database
    # --------------------------------------------------------

    vector_store = VectorStore()

    # Check whether ChromaDB already contains documents
    existing_count = vector_store.collection.count()

    # --------------------------------------------------------
    # FIRST RUN
    # --------------------------------------------------------

    if existing_count == 0:

        print("ChromaDB is empty.")
        print("Extracting Karnataka Rent Act...")

        # Extract PDF
        pages = extract_pages_from_pdf(PDF_PATH)

        print(f"Pages extracted: {len(pages)}")

        # Create chunks
        chunks = chunk_pages(pages)

        print(f"Chunks created: {len(chunks)}")

        # Load embedding model
        embedding_model = EmbeddingModel()

        print("Generating embeddings...")

        texts = [
            chunk["text"]
            for chunk in chunks
        ]

        embeddings = embedding_model.embed_documents(
            texts
        )

        print("Storing documents in ChromaDB...")

        vector_store.add_documents(
            chunks,
            embeddings
        )

        print(
            f"Successfully stored "
            f"{len(chunks)} chunks!"
        )

    # --------------------------------------------------------
    # EXISTING DATABASE
    # --------------------------------------------------------

    else:

        print(
            f"Existing ChromaDB detected "
            f"({existing_count} chunks)."
        )

        print(
            "Skipping PDF extraction "
            "and embedding generation."
        )

        # We still need the embedding model because
        # it is required to embed new user questions.

        embedding_model = EmbeddingModel()

    # --------------------------------------------------------
    # LOAD GEMINI
    # --------------------------------------------------------

    llm = GeminiLLM()

    return (
        embedding_model,
        vector_store,
        llm
    )


# ============================================================
# LOAD SYSTEM
# ============================================================

with st.spinner("Loading legal database..."):

    try:

        embedding_model, vector_store, llm = load_navigator()

        st.success(
            "Karnataka Rent Act database loaded successfully."
        )

    except Exception as e:

        st.error(
            "The legal database could not be loaded."
        )

        st.exception(e)

        st.stop()


# ============================================================
# QUESTION INPUT
# ============================================================

st.subheader("Ask a legal question")

query = st.text_area(
    "Enter your question:",
    placeholder=(
        "Example: What does the law say about "
        "a tenancy agreement?"
    ),
    height=100
)


# ============================================================
# ASK BUTTON
# ============================================================

ask_button = st.button(
    "🔍 Search Legal Database",
    type="primary"
)


# ============================================================
# PROCESS QUESTION
# ============================================================

if ask_button:

    if not query.strip():

        st.warning(
            "Please enter a question first."
        )

        st.stop()

    # --------------------------------------------------------
    # EMBED QUERY AND SEARCH
    # --------------------------------------------------------

    with st.spinner(
        "Searching the legal database..."
    ):

        query_embedding = embedding_model.embed_text(
            query
        )

        results = vector_store.search(
            query,
            query_embedding,
            n_results=5
        )

    # --------------------------------------------------------
    # BUILD CONTEXT
    # --------------------------------------------------------

    context_parts = []

    for result in results:

        metadata = result["metadata"]

        context_parts.append(
            f"""
Source: {metadata['source']}
Jurisdiction: {metadata['jurisdiction']}
Page: {metadata['page']}

Legal Text:
{result['text']}
"""
        )

    context = (
        "\n-----------------------------\n"
        .join(context_parts)
    )

    # --------------------------------------------------------
    # GENERATE ANSWER
    # --------------------------------------------------------

    with st.spinner(
        "Generating grounded legal answer..."
    ):

        answer = llm.generate_answer(
            query,
            context
        )

    # ========================================================
    # DISPLAY ANSWER
    # ========================================================

    st.divider()

    st.subheader("Answer")

    st.markdown(answer)

    # ========================================================
    # DISPLAY SOURCES
    # ========================================================

    st.divider()

    st.subheader("📚 Retrieved Legal Sources")

    for i, result in enumerate(
        results,
        start=1
    ):

        metadata = result["metadata"]

        with st.expander(
            f"{i}. {metadata['source']} — "
            f"Page {metadata['page']}"
        ):

            st.write(
                f"**Jurisdiction:** "
                f"{metadata['jurisdiction']}"
            )

            st.write(
                "**Retrieved legal text:**"
            )

            st.write(
                result["text"]
            )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Tenant Rights Navigator • "
    "Information grounded in the Karnataka Rent Act, 1999. "
    "This tool provides general legal information and "
    "does not constitute legal advice."
)