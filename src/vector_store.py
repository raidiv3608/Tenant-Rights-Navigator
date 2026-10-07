import chromadb
import re


class VectorStore:

    def __init__(self):

        self.client = chromadb.PersistentClient(
            path="chroma_db"
        )

        self.collection = self.client.get_or_create_collection(
            name="karnataka_rent_act_v2"
        )


    # =========================================================
    # ADD DOCUMENTS
    # =========================================================

    def add_documents(self, chunks, embeddings):

        ids = [
            f"chunk_{i}"
            for i in range(len(chunks))
        ]

        documents = [
            chunk["text"]
            for chunk in chunks
        ]

        metadatas = [
            {
                "page": chunk["page"],
                "section": chunk.get(
                    "section",
                    "Unknown"
                ),
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


    # =========================================================
    # SEARCH
    # =========================================================

    def search(
        self,
        query,
        query_embedding,
        n_results=5
    ):

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=[
                "documents",
                "metadatas",
                "distances"
            ]
        )

        documents = results["documents"][0]

        metadatas = results["metadatas"][0]

        distances = results["distances"][0]


        # =====================================================
        # QUERY KEYWORDS
        # =====================================================

        query_words = set(
            re.findall(
                r"\b[a-zA-Z]{4,}\b",
                query.lower()
            )
        )


        scored_results = []


        # =====================================================
        # COMBINE SEMANTIC + KEYWORD RELEVANCE
        # =====================================================

        for document, metadata, distance in zip(
            documents,
            metadatas,
            distances
        ):

            document_lower = document.lower()


            # Semantic similarity
            semantic_score = 1 / (
                1 + distance
            )


            # Keyword matching
            keyword_matches = sum(
                1
                for word in query_words
                if word in document_lower
            )


            # Small keyword boost
            keyword_boost = (
                keyword_matches * 0.02
            )


            # Final score
            final_score = (
                semantic_score +
                keyword_boost
            )


            scored_results.append(
                {
                    "text": document,
                    "metadata": metadata,
                    "semantic_score": semantic_score,
                    "keyword_score": keyword_matches,
                    "final_score": final_score
                }
            )


        # =====================================================
        # SORT BY FINAL RELEVANCE
        # =====================================================

        scored_results.sort(
            key=lambda x: x["final_score"],
            reverse=True
        )


        return scored_results