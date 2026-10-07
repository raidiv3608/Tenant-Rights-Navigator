

from src.pdf_loader import extract_pages_from_pdf
from src.chunker import chunk_pages
from src.embeddings import EmbeddingModel
from src.vector_store import VectorStore


PDF_PATH = "data/legislation/karnataka/34 of 2001 (E).pdf"


print("=" * 60)
print("REBUILDING TENANT RIGHTS NAVIGATOR DATABASE")
print("=" * 60)


# =========================================================
# 1. DELETE OLD CHROMADB
# =========================================================



# =========================================================
# 2. EXTRACT PDF
# =========================================================

print("\nExtracting Karnataka Rent Act...")

pages = extract_pages_from_pdf(
    PDF_PATH
)

print(
    f"Pages extracted: {len(pages)}"
)


# =========================================================
# 3. CREATE NEW CHUNKS
# =========================================================

print("\nCreating chunks...")

chunks = chunk_pages(pages)

print(
    f"Chunks created: {len(chunks)}"
)


# =========================================================
# 4. SHOW SECTION INFORMATION
# =========================================================

section_count = sum(
    1
    for chunk in chunks
    if chunk.get("section") != "Unknown"
)

print(
    f"Chunks with section metadata: "
    f"{section_count}"
)


# =========================================================
# 5. GENERATE EMBEDDINGS
# =========================================================

print("\nGenerating embeddings...")

embedding_model = EmbeddingModel()

texts = [
    chunk["text"]
    for chunk in chunks
]

embeddings = embedding_model.embed_documents(
    texts
)

print("Embeddings generated.")


# =========================================================
# 6. STORE IN CHROMADB
# =========================================================

print("\nStoring documents in ChromaDB...")

vector_store = VectorStore()

vector_store.add_documents(
    chunks,
    embeddings
)


print(
    f"\nSuccessfully stored "
    f"{len(chunks)} chunks!"
)


# =========================================================
# 7. VERIFY
# =========================================================

print("\nVerifying database...")

print(
    f"Database contains: "
    f"{vector_store.collection.count()} "
    f"documents"
)


print("\n" + "=" * 60)
print("DATABASE REBUILD COMPLETE")
print("=" * 60)