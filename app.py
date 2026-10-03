
from src.pdf_loader import extract_pages_from_pdf
from src.chunker import chunk_pages
from src.embeddings import EmbeddingModel
from src.vector_store import VectorStore
from src.llm import GeminiLLM


# ==========================================
# CONFIGURATION
# ==========================================

PDF_PATH = "data/legislation/karnataka/34 of 2001 (E).pdf"


# ==========================================
# 1. EXTRACT PDF
# ==========================================

print("Extracting Karnataka Rent Act...")

pages = extract_pages_from_pdf(PDF_PATH)

print(f"Pages extracted: {len(pages)}")


# ==========================================
# 2. CREATE CHUNKS
# ==========================================

print("\nCreating chunks...")

chunks = chunk_pages(pages)

print(f"Chunks created: {len(chunks)}")


# ==========================================
# 3. GENERATE EMBEDDINGS
# ==========================================

print("\nGenerating embeddings...")

embedding_model = EmbeddingModel()

texts = [chunk["text"] for chunk in chunks]

embeddings = embedding_model.embed_documents(texts)


# ==========================================
# 4. STORE IN CHROMADB
# ==========================================

print("\nStoring documents in ChromaDB...")

vector_store = VectorStore()

vector_store.add_documents(
    chunks,
    embeddings
)

print(f"Successfully stored {len(chunks)} chunks!")


# ==========================================
# 5. ASK USER QUESTION
# ==========================================

query = input(
    "\nAsk a question about the Karnataka Rent Act: "
)


# ==========================================
# 6. EMBED USER QUERY
# ==========================================

print("\nSearching the legal database...")

query_embedding = embedding_model.embed_text(query)


# ==========================================
# 7. RETRIEVE RELEVANT LEGAL PASSAGES
# ==========================================

results = vector_store.search(
    query,
    query_embedding,
    n_results=5
)


# ==========================================
# 8. BUILD LEGAL CONTEXT
# ==========================================

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


context = "\n-----------------------------\n".join(
    context_parts
)


# ==========================================
# 9. GENERATE GEMINI ANSWER
# ==========================================

print("\nGenerating grounded answer...")

llm = GeminiLLM()

answer = llm.generate_answer(
    query,
    context
)


# ==========================================
# 10. DISPLAY ANSWER
# ==========================================

print("\n")
print("=" * 70)
print("TENANT RIGHTS NAVIGATOR")
print("=" * 70)

print("\nAnswer:\n")
print(answer)


# ==========================================
# 11. DISPLAY RETRIEVED SOURCES
# ==========================================

print("\n")
print("=" * 70)
print("RETRIEVED LEGAL SOURCES")
print("=" * 70)

for i, result in enumerate(results, start=1):

    metadata = result["metadata"]

    print(
        f"\n{i}. {metadata['source']} "
        f"— Page {metadata['page']}"
    )


# ==========================================
# 12. FALLBACK: SHOW LEGAL TEXT
# ==========================================

if (
    "temporarily unavailable" in answer.lower()
    or "could not generate" in answer.lower()
    or "technical error" in answer.lower()
):

    print("\n")
    print("=" * 70)
    print("RETRIEVED LEGAL CONTEXT")
    print("=" * 70)

    print(
        "\nGemini is currently unavailable. "
        "The following passages were retrieved directly "
        "from the Karnataka Rent Act:\n"
    )

    for i, result in enumerate(results, start=1):

        metadata = result["metadata"]

        print("\n" + "-" * 70)

        print(
            f"Result {i}\n"
            f"Source: {metadata['source']}\n"
            f"Jurisdiction: {metadata['jurisdiction']}\n"
            f"Page: {metadata['page']}\n"
        )

        print("Legal Text:")
        print(result["text"])


print("\n")
print("=" * 70)
print("END")
print("=" * 70)

