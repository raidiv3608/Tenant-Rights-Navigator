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
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* ---------- GLOBAL ---------- */

    .stApp {
        background: linear-gradient(
            135deg,
            #0b1020 0%,
            #111827 45%,
            #172554 100%
        );
    }

    .main .block-container {
        max-width: 1250px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    /* ---------- HEADINGS ---------- */

    h1, h2, h3 {
        letter-spacing: -0.5px;
    }

    /* ---------- HERO ---------- */

    .hero-box {
        padding: 3rem 2rem;
        border-radius: 24px;
        margin-bottom: 2rem;
        background: linear-gradient(
            135deg,
            #172554,
            #1e3a5f,
            #0f172a
        );
        border: 1px solid rgba(255,255,255,0.12);
        box-shadow: 0 20px 50px rgba(0,0,0,0.30);
        text-align: center;
        animation: fadeUp 0.7s ease-out;
    }

    .hero-icon {
        font-size: 3.2rem;
        margin-bottom: 0.5rem;
    }

    .hero-title {
        font-size: 3rem;
        font-weight: 800;
        color: white;
        margin-bottom: 0.8rem;
    }

    .hero-subtitle {
        font-size: 1.15rem;
        color: #cbd5e1;
        max-width: 760px;
        margin: auto;
        line-height: 1.7;
    }

    .hero-badge {
        display: inline-block;
        padding: 0.45rem 1rem;
        border-radius: 999px;
        background: rgba(255,255,255,0.08);
        border: 1px solid rgba(255,255,255,0.15);
        color: #bfdbfe;
        font-size: 0.85rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        margin-bottom: 1rem;
    }

    /* ---------- INFO CARDS ---------- */

    .info-card {
        padding: 1.5rem;
        border-radius: 18px;
        min-height: 180px;
        background: rgba(255,255,255,0.96);
        color: #1e293b;
        border: 1px solid rgba(255,255,255,0.25);
        box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        transition:
            transform 0.25s ease,
            box-shadow 0.25s ease;
        animation: fadeUp 0.8s ease-out;
    }

    .info-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 18px 40px rgba(0,0,0,0.28);
    }

    .info-icon {
        font-size: 2rem;
        margin-bottom: 0.6rem;
    }

    .info-title {
        font-size: 1.15rem;
        font-weight: 750;
        margin-bottom: 0.6rem;
    }

    .info-text {
        color: #475569;
        line-height: 1.55;
        font-size: 0.95rem;
    }

    /* ---------- STATUS ---------- */

    .status-box {
        padding: 1rem 1.25rem;
        border-radius: 14px;
        background: rgba(16,185,129,0.12);
        border: 1px solid rgba(16,185,129,0.35);
        color: #a7f3d0;
        margin: 1.5rem 0;
        animation: fadeUp 0.9s ease-out;
    }

    /* ---------- QUESTION AREA ---------- */

    .question-box {
        padding: 2rem;
        border-radius: 20px;
        background: rgba(255,255,255,0.055);
        border: 1px solid rgba(255,255,255,0.10);
        margin-top: 2rem;
        margin-bottom: 2rem;
        animation: fadeUp 1s ease-out;
    }

    /* ---------- BUTTONS ---------- */

    .stButton > button {
        border-radius: 12px;
        min-height: 48px;
        font-weight: 700;
        transition:
            transform 0.2s ease,
            box-shadow 0.2s ease;
    }

    .stButton > button:hover {
        transform: translateY(-3px) scale(1.015);
        box-shadow: 0 8px 20px rgba(0,0,0,0.25);
    }

    /* ---------- TEXT AREA ---------- */

    textarea {
        border-radius: 14px !important;
    }

    /* ---------- RESULT ---------- */

    .answer-header {
        margin-top: 2rem;
        animation: fadeUp 0.5s ease-out;
    }

    .source-title {
        margin-top: 2rem;
    }

    /* ---------- FOOTER ---------- */

    .footer-box {
        margin-top: 4rem;
        padding: 2rem;
        border-top: 1px solid rgba(255,255,255,0.12);
        text-align: center;
        color: #94a3b8;
    }

    .footer-title {
        color: #e2e8f0;
        font-size: 1.15rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }

    /* ---------- ANIMATION ---------- */

    @keyframes fadeUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }

        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    /* ---------- SIDEBAR ---------- */

    [data-testid="stSidebar"] {
        background: #0f172a;
    }

    /* ---------- MOBILE ---------- */

    @media (max-width: 768px) {

        .hero-title {
            font-size: 2.1rem;
        }

        .hero-subtitle {
            font-size: 1rem;
        }

        .main .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("⚖️ Navigator")

    st.markdown("### About")

    st.write(
        "Tenant Rights Navigator combines:"
    )

    st.markdown(
        """
        📄 **Official legislation**

        🧩 **Document chunking**

        🔎 **Semantic retrieval**

        🧠 **Vector search**

        ✨ **Gemini AI**

        📚 **Grounded legal sources**
        """
    )

    st.divider()

    st.markdown("### Current Jurisdiction")

    st.info("🇮🇳 Karnataka")

    st.markdown("### Legal Document")

    st.write("Karnataka Rent Act, 1999")


# ============================================================
# HERO SECTION
# ============================================================

st.markdown(
    """
    <div class="hero-box">

        <div class="hero-badge">
            ⚖️ AI-POWERED LEGAL INFORMATION
        </div>

        <div class="hero-icon">
            ⚖️
        </div>

        <div class="hero-title">
            Tenant Rights Navigator
        </div>

        <div class="hero-subtitle">
            Understand your tenancy rights through
            legislation-grounded answers from the
            Karnataka Rent Act, 1999.
        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# INTRODUCTION
# ============================================================

st.subheader("Explore the Law")

st.write(
    "Retrieve relevant provisions from the legislation "
    "before generating an answer."
)


# ============================================================
# INFORMATION CARDS
# ============================================================

col1, col2, col3 = st.columns(3)


with col1:

    st.markdown(
        """
        <div class="info-card">

        <div class="info-icon">📄</div>

        <div class="info-title">
        Legal Knowledge Base
        </div>

        <div class="info-text">
        Search information from the Karnataka Rent Act,
        1999 using a structured legal knowledge base.
        </div>

        </div>
        """,
        unsafe_allow_html=True
    )


with col2:

    st.markdown(
        """
        <div class="info-card">

        <div class="info-icon">🔎</div>

        <div class="info-title">
        Smart Retrieval
        </div>

        <div class="info-text">
        Your question is matched against relevant
        sections of the legislation before an answer
        is generated.
        </div>

        </div>
        """,
        unsafe_allow_html=True
    )


with col3:

    st.markdown(
        """
        <div class="info-card">

        <div class="info-icon">🧠</div>

        <div class="info-title">
        Grounded AI Answers
        </div>

        <div class="info-text">
        Gemini generates responses using retrieved
        legal text rather than relying only on
        general knowledge.
        </div>

        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# LOAD DATA AND MODELS
# ============================================================

PDF_PATH = "data/legislation/karnataka/34 of 2001 (E).pdf"


@st.cache_resource
def load_navigator():

    pages = extract_pages_from_pdf(PDF_PATH)

    chunks = chunk_pages(pages)

    embedding_model = EmbeddingModel()

    texts = [
        chunk["text"]
        for chunk in chunks
    ]

    embeddings = embedding_model.embed_documents(
        texts
    )

    vector_store = VectorStore()

    vector_store.add_documents(
        chunks,
        embeddings
    )

    llm = GeminiLLM()

    return (
        embedding_model,
        vector_store,
        llm
    )


# ============================================================
# INITIALIZE SYSTEM
# ============================================================

with st.spinner("Loading legal knowledge base..."):

    try:

        (
            embedding_model,
            vector_store,
            llm
        ) = load_navigator()

        st.success(
            "✓ Karnataka Rent Act knowledge base ready."
        )

    except Exception as e:

        st.error(
            "The legal database could not be loaded."
        )

        st.exception(e)

        st.stop()


# ============================================================
# QUESTION SECTION
# ============================================================

st.markdown(
    '<div class="question-box">',
    unsafe_allow_html=True
)

st.subheader("🔍 Ask a Legal Question")

st.write(
    "Ask a question about tenancy rights and obligations "
    "under the Karnataka Rent Act, 1999."
)


# ============================================================
# QUICK QUESTIONS
# ============================================================

st.write("**Try one of these questions:**")

q1, q2, q3 = st.columns(3)


with q1:

    if st.button(
        "📄 Tenancy Agreement",
        use_container_width=True
    ):
        st.session_state["question"] = (
            "What does the law say about a tenancy agreement?"
        )


with q2:

    if st.button(
        "💰 Rent & Charges",
        use_container_width=True
    ):
        st.session_state["question"] = (
            "What does the law say about rent and charges?"
        )


with q3:

    if st.button(
        "🏠 Eviction",
        use_container_width=True
    ):
        st.session_state["question"] = (
            "What does the law say about eviction?"
        )


# ============================================================
# QUESTION INPUT
# ============================================================

query = st.text_area(
    "Enter your question:",
    value=st.session_state.get("question", ""),
    placeholder=(
        "Example: What does the law say about "
        "a tenancy agreement?"
    ),
    height=120
)


ask_button = st.button(
    "🔎 Search Legal Database",
    type="primary",
    use_container_width=True
)

st.markdown(
    "</div>",
    unsafe_allow_html=True
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
    # EMBEDDING + RETRIEVAL
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

    st.subheader("📖 Answer")

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
            f"{i}. {metadata['source']} — Page {metadata['page']}"
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
# DISCLAIMER
# ============================================================

st.divider()

with st.expander(
    "⚠️ Legal Information Disclaimer"
):

    st.write(
        "Tenant Rights Navigator provides general legal "
        "information based on the legislation available "
        "in its knowledge base."
    )

    st.write(
        "It does not constitute personalized legal advice "
        "and does not create a lawyer-client relationship."
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer-box">

        <div class="footer-title">
            ⚖️ Tenant Rights Navigator
        </div>

        <div>
            AI-powered legal information assistant
            grounded in the Karnataka Rent Act, 1999.
        </div>

       

    </div>
    """,
    unsafe_allow_html=True
)