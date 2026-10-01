import chromadb


class VectorStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(path="chroma_db")

        self.collection = self.client.get_or_create_collection(
            name="karnataka_rent_act"
        )

    def add_documents(self, chunks, embeddings):
        ids = [f"chunk_{i}" for i in range(len(chunks))]

        documents = [chunk["text"] for chunk in chunks]

        metadatas = [
            {
                "page": chunk["page"],
                "source": "Karnataka Rent Act, 1999",
                "jurisdiction": "Karnataka"
            }
            for chunk in chunks
        ]

        self.collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas
        )

    def search(self, query_embedding, n_results=3):
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )

        return results