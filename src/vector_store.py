import chromadb
import re


class VectorStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(path="chroma_db")

        self.collection = self.client.get_or_create_collection(
            name="karnataka_rent_act_v2"
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

    def search(self, query, query_embedding, n_results=5):
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )

        documents = results["documents"][0]
        metadatas = results["metadatas"][0]

        # Extract meaningful terms from the question
        query_words = set(
            re.findall(r"\b[a-zA-Z]{4,}\b", query.lower())
        )

        scored_results = []

        for document, metadata in zip(documents, metadatas):
            document_lower = document.lower()

            keyword_matches = sum(
                1 for word in query_words
                if word in document_lower
            )

            # Semantic similarity remains the main signal.
            # Keyword matching provides a small legal-terminology boost.
            score = keyword_matches

            scored_results.append(
                {
                    "text": document,
                    "metadata": metadata,
                    "keyword_score": score
                }
            )

        scored_results.sort(
            key=lambda x: x["keyword_score"],
            reverse=True
        )

        return scored_results