from src.pdf_loader import extract_pages_from_pdf
from src.chunker import chunk_pages
from src.embeddings import EmbeddingModel
from src.vector_store import VectorStore


PDF_PATH = "data/legislation/karnataka/34 of 2001 (E).pdf"


# 1. Extract and decode PDF
print("Extracting Karnataka Rent Act...")
pages = extract_pages_from_pdf(PDF_PATH)

# 2. Create metadata-aware chunks
print("Creating chunks...")
chunks = chunk_pages(pages)

# 3. Generate embeddings
print("Generating embeddings...")
embedding_model = EmbeddingModel()

texts = [chunk["text"] for chunk in chunks]
embeddings = embedding_model.embed_documents(texts)

# 4. Store in ChromaDB
print("Storing documents in ChromaDB...")
vector_store = VectorStore()
vector_store.add_documents(chunks, embeddings)

print(f"\nSuccessfully stored {len(chunks)} chunks!")


# 5. Test semantic retrieval
query = "What does the law say about a tenancy agreement?"

print(f"\nSearching for: {query}")

query_embedding = embedding_model.embed_text(query)

results = vector_store.search(
    query_embedding,
    n_results=3
)

print("\n--- RETRIEVED RESULTS ---")

for i, document in enumerate(results["documents"][0], start=1):

    metadata = results["metadatas"][0][i - 1]

    print(f"\nResult {i}")
    print(f"Page: {metadata['page']}")
    print(f"Source: {metadata['source']}")
    print(f"Jurisdiction: {metadata['jurisdiction']}")
    print("\nText:")
    print(document[:1000])