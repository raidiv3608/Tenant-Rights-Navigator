
from importlib import metadata

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
                "section": chunk.get("section", "Unknown"),
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
    # SEARCH AND RERANK
    # =========================================================

    def search(self, query, query_embedding, n_results=5):

        total_documents = self.collection.count()

        if total_documents == 0:
            return []

        candidate_count = min(
            total_documents,
            max(n_results * 6, 40)
        )

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=candidate_count,
            include=[
                "documents",
                "metadatas",
                "distances"
            ]
        )

        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]

        query_lower = query.lower()

        query_words = set(
            re.findall(r"\b[a-zA-Z]{3,}\b", query_lower)
        )

        # Expand common legal terminology.
        synonym_groups = [
            {"repair", "repairs", "repaired", "repairing", "maintenance"},
            {"landlord", "owner", "lessor"},
            {"tenant", "occupant", "lessee"},
            {"property", "premises", "building", "house"},
            {"responsible", "responsibility", "duty", "duties", "liable"},
            {"deposit", "security", "refund", "repayment"},
            {"evict", "eviction", "eject", "possession"},
            {"rent", "rental", "arrears", "payment"},
            {"notice", "notify", "notification"},
            {"increase", "enhancement", "revision"}
        ]

        expanded_words = set(query_words)

        for group in synonym_groups:
            if query_words.intersection(group):
                expanded_words.update(group)

        # Identify the question's main topic.
        topic_patterns = {
            "repair": (
                r"\brepairs?\b|\brepairing\b|\bmaintenance\b"
                r"|\bfix(?:ing|ed)?\b"
            ),
            "deposit": (
                r"\bdeposit\b|\bsecurity deposit\b"
                r"|\brefund\b|\brepayment\b"
            ),
            "eviction": (
                r"\beviction\b|\bevicted\b|\bevict\b"
                r"|\beject(?:ion)?\b"
                r"|\brecovery of possession\b"
                r"|\bpossession of the premises\b"
            ),
            "rent": (
                r"\brent\b|\brental\b|\barrears\b"
                r"|\brent increase\b"
            ),
            "notice": (
                r"\bnotice\b|\bnotice period\b"
                r"|\bwritten notice\b"
            ),
            "agreement": (
                r"\bagreement\b|\blease\b|\btenancy\b"
            )
        }

        active_topics = {
            topic
            for topic, pattern in topic_patterns.items()
            if re.search(pattern, query_lower)
        }

        scored_results = []

        for document, metadata, distance in zip(
            documents,
            metadatas,
            distances
        ):

            document_lower = document.lower()

            semantic_score = 1 / (1 + max(distance, 0))

            matched_words = sum(
                1
                for word in expanded_words
                if re.search(
                    r"\b" + re.escape(word) + r"\b",
                    document_lower
                )
            )

            keyword_score = (
                matched_words / len(expanded_words)
                if expanded_words
                else 0
            )

            # Detect topic-specific relevance.
            topic_score = 0

            topic_document_patterns = {
                "repair": (
                    r"\brepairs?\b|\brepairing\b|\bmaintenance\b"
                    r"|\bschedule\s+v\b|\btap washers?\b"
                ),
                "deposit": (
                    r"\bdeposit\b|\bsecurity deposit\b"
                    r"|\brefund\b|\brepayment\b"
                ),
                "eviction": (
                    r"\beviction\b|\bevicted\b|\beject(?:ion)?\b"
                    r"|\bgrounds for eviction\b"
                    r"|\brecovery of possession\b"
                    r"|\bpossession of the premises\b"
                ),
                "rent": (
                    r"\brent\b|\barrears\b|\brent increase\b"
                    r"|\bstandard rent\b"
                ),
                "notice": (
                    r"\bnotice\b|\bwritten notice\b"
                    r"|\bnotice period\b"
                ),
                "agreement": (
                    r"\bagreement\b|\blease\b|\btenancy agreement\b"
                )
            }

            for topic in active_topics:
                if re.search(
                    topic_document_patterns[topic],
                    document_lower
                ):
                    topic_score += 0.10

            # Extra relevance for repair questions involving
            # responsibilities of landlords and tenants.
            if "repair" in active_topics:

                mentions_party = bool(
                    re.search(
                        r"\blandlord\b|\btenant\b|\bowner\b"
                        r"|\boccupant\b",
                        document_lower
                    )
                )
                section_label = metadata.get("section", "").lower()

                mentions_schedule_v = (
                     bool(re.search(r"\bschedule\s+v\b", document_lower))
                     or "fifth schedule" in section_label
                )

                if mentions_party:
                    topic_score += 0.05

                if mentions_schedule_v:
                    topic_score += 0.10

            final_score = (
                0.65 * semantic_score
                + 0.25 * keyword_score
                + topic_score
            )

            scored_results.append({
                "text": document,
                "metadata": metadata,
                "semantic_score": semantic_score,
                "keyword_score": keyword_score,
                "final_score": final_score
            })

        scored_results.sort(
            key=lambda item: item["final_score"],
            reverse=True
        )

        return scored_results[:n_results]