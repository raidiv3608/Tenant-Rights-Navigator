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


    def search(
        self,
        query,
        query_embedding,
        n_results=5
    ):

        # Retrieve more candidates initially.
        # We will rank them ourselves afterwards.
        candidate_count = max(
            n_results * 3,
            15
        )

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=candidate_count
        )

        documents = results["documents"][0]
        metadatas = results["metadatas"][0]

        # ----------------------------------------------------
        # Extract meaningful words from the question
        # ----------------------------------------------------

        query_words = set(
            re.findall(
                r"\b[a-zA-Z]{4,}\b",
                query.lower()
            )
        )

        # Common words that should not influence ranking
        stop_words = {
            "what",
            "does",
            "this",
            "that",
            "about",
            "from",
            "with",
            "under",
            "where",
            "when",
            "which",
            "what",
            "law",
            "tell",
            "please"
        }

        query_words -= stop_words

        scored_results = []

        # ----------------------------------------------------
        # Score every retrieved candidate
        # ----------------------------------------------------

        for rank, (document, metadata) in enumerate(
            zip(documents, metadatas)
        ):

            document_lower = document.lower()

            keyword_matches = sum(
                1
                for word in query_words
                if word in document_lower
            )

            # ------------------------------------------------
            # Give additional importance to exact phrases
            # ------------------------------------------------

            phrase_bonus = 0

            query_lower = query.lower()

            if "tenancy agreement" in query_lower:
                if "tenancy agreement" in document_lower:
                    phrase_bonus += 4

            if "rent" in query_lower:
                if "rent" in document_lower:
                    phrase_bonus += 1

            if "eviction" in query_lower:
                if "eviction" in document_lower:
                    phrase_bonus += 2

            if "deposit" in query_lower:
                if "deposit" in document_lower:
                    phrase_bonus += 2

            if "sub tenant" in query_lower:
                if "sub-tenant" in document_lower:
                    phrase_bonus += 2

            # ------------------------------------------------
            # Earlier Chroma result = stronger semantic match
            # ------------------------------------------------

            semantic_rank_score = (
                candidate_count - rank
            )

            # ------------------------------------------------
            # Final combined score
            # ------------------------------------------------

            final_score = (
                semantic_rank_score
                + keyword_matches * 2
                + phrase_bonus
            )

            scored_results.append(
                {
                    "text": document,
                    "metadata": metadata,
                    "keyword_score": keyword_matches,
                    "phrase_bonus": phrase_bonus,
                    "score": final_score
                }
            )

        # ----------------------------------------------------
        # Sort by combined relevance
        # ----------------------------------------------------

        scored_results.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        # Return only the requested number
        return scored_results[:n_results]