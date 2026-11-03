import time
import re

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pydantic import BaseModel, validator

from src.embeddings import EmbeddingModel
from src.vector_store import VectorStore
from src.llm import GeminiLLM

# ============================================================

# FASTAPI APPLICATION

# ============================================================

app = FastAPI(
title="Tenant Rights Navigator API",
description="Backend API for the Tenant Rights Navigator",
version="1.1.0"
)

# ============================================================

# CORS

# ============================================================

app.add_middleware(
CORSMiddleware,
allow_origins=["*"],
allow_credentials=True,
allow_methods=["*"],
allow_headers=["*"],
)

# ============================================================

# REQUEST MODEL

# ============================================================

class QuestionRequest(BaseModel):
    question: str

    @validator("question", pre=True)
    def validate_question(cls, value):
        if not isinstance(value, str):
            raise ValueError("Question must be a string.")

        value = value.strip()
        if not value:
            raise ValueError("Question cannot be empty.")

        return value

# ============================================================

# LOAD MODELS

# ============================================================

print("\n==============================================")
print("TENANT RIGHTS NAVIGATOR API")
print("==============================================")

print("\nLoading embedding model...")

embedding_model = EmbeddingModel()

print("Embedding model loaded successfully.")

print("\nLoading legal database...")

vector_store = VectorStore()

print("ChromaDB loaded successfully.")

print("\nLoading Gemini...")

llm = GeminiLLM()

print("Gemini client loaded successfully.")

print("\n==============================================")
print("API READY")
print("==============================================\n")

# ============================================================

# HELPER: NORMALIZE TEXT

# ============================================================

def normalize_text(text: str) -> str:
    """
    Normalize text for duplicate detection.
    This does not modify the original legal passage.
    """
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\w\s]", "", text)

    return text.strip()

# ============================================================

# HELPER: SELECT SOURCES

# ============================================================

def select_sources(results, max_sources=10):
    """
    Select relevant legal passages while removing exact duplicates.
    Preserves retrieval order and source metadata.
    """
    selected = []
    seen_texts = set()

    for result in results:
        text = result.get("text", "").strip()
        metadata = result.get("metadata", {})

        if not text:
            continue

        normalized_text = normalize_text(text)

        if normalized_text in seen_texts:
            continue

        seen_texts.add(normalized_text)

        selected.append({
            "source": metadata.get("source", "Unknown source"),
            "jurisdiction": metadata.get("jurisdiction", "Unknown"),
            "page": metadata.get("page", "Unknown"),
            "section": metadata.get("section", "Unknown"),
            "text": text
        })

        if len(selected) >= max_sources:
            break

    return selected

# ============================================================

# HELPER: SECTION-AWARE RETRIEVAL

# ============================================================

def get_section_chunks(section_name):
    """
    Retrieve all chunks belonging to a particular legal section
    directly from ChromaDB using section metadata.
    """
    try:
        collection = vector_store.collection

        result = collection.get(
            where={"section": section_name},
            include=["documents", "metadatas"]
        )

        documents = result.get("documents") or []
        metadatas = result.get("metadatas") or []

        section_results = []

        for text, metadata in zip(documents, metadatas):
            section_results.append({
                "text": text,
                "metadata": metadata or {}
            })

        return section_results

    except Exception as e:
        print(
            f"[RETRIEVAL WARNING] "
            f"Could not retrieve {section_name}: {e}"
        )
        return []

# ============================================================

# HELPER: BUILD LEGAL CONTEXT

# ============================================================

def build_legal_context(sources):
    """
    Build context from selected source passages.
    Includes section and page metadata to help the LLM
    associate legal statements with their sources.
    """
    context_parts = []

    for index, source in enumerate(sources, start=1):
        context_parts.append(
            f"""
SOURCE {index}

Document: {source["source"]}
Jurisdiction: {source["jurisdiction"]}
Section: {source["section"]}
Page: {source["page"]}

Legal text:
{source["text"]}
""".strip()
        )

    return "\n\n----------------------------------------\n\n".join(context_parts)

# ============================================================

# HEALTH CHECK

# ============================================================

@app.get("/")
def root():
    return {
        "status": "online",
        "application": "Tenant Rights Navigator",
        "message": "Backend API is running."
    }

# ============================================================

# ASK QUESTION

# ============================================================

@app.post("/ask")
def ask_question(request: QuestionRequest):
    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    request_start = time.perf_counter()

    try:
        print("\n----------------------------------------------")
        print("QUESTION")
        print("----------------------------------------------")
        print(question)

        # ====================================================
        # EMBED USER QUESTION
        # ====================================================
        embedding_start = time.perf_counter()

        query_embedding = embedding_model.embed_text(question)

        embedding_time = time.perf_counter() - embedding_start

        print(
            f"[TIMING] Embedding: "
            f"{embedding_time:.3f} seconds"
        )

        # ====================================================
        # SEARCH CHROMADB
        # ====================================================
        retrieval_start = time.perf_counter()

        results = vector_store.search(
            question,
            query_embedding,
            n_results=20
        )

        retrieval_time = time.perf_counter() - retrieval_start

        print(
            f"[TIMING] ChromaDB retrieval: "
            f"{retrieval_time:.3f} seconds"
        )

        # ====================================================
        # DETECT SECTION 27 / EVICTION QUESTIONS
        # ====================================================
        question_lower = question.lower()

        asks_about_section_27 = (
            "section 27" in question_lower
            or "section 27(2)" in question_lower
        )

        eviction_terms = [
            "eviction",
            "evict",
            "grounds for possession",
            "recovery of possession",
            "recover possession",
            "possession of the premises"
        ]

        asks_about_eviction = any(
            term in question_lower
            for term in eviction_terms
        )

        # ====================================================
        # SECTION-AWARE RETRIEVAL
        # ====================================================
        if asks_about_section_27 or asks_about_eviction:
            print("\n[RETRIEVAL] Section 27 query detected.")
            print("[RETRIEVAL] Fetching all Section 27 chunks...")

            section_27_results = get_section_chunks("Section 27")

            print(
                f"[RETRIEVAL] Section 27 chunks retrieved: "
                f"{len(section_27_results)}"
            )

            combined_results = results + section_27_results
            sources = select_sources(combined_results, max_sources=100)
        else:
            sources = select_sources(results, max_sources=10)

        # ====================================================
        # CHECK RETRIEVAL RESULTS
        # ====================================================
        if not sources:
            return {
                "answer": (
                    "I could not find relevant passages in "
                    "the available legal database for this "
                    "question. Please try rephrasing your "
                    "question."
                ),
                "sources": []
            }

        print(
            f"\n[RETRIEVAL] Candidates received: "
            f"{len(results)}"
        )

        print(
            f"[RETRIEVAL] Sources selected: "
            f"{len(sources)}"
        )

        for index, source in enumerate(sources, start=1):
            print(
                f"[SOURCE {index}] "
                f"Section={source['section']}, "
                f"Page={source['page']}"
            )

        # ====================================================
        # BUILD LEGAL CONTEXT
        # ====================================================
        context = build_legal_context(sources)

        if not context.strip():
            return {
                "answer": (
                    "No usable legal text was retrieved "
                    "for this question."
                ),
                "sources": []
            }

        # ====================================================
        # GENERATE GROUNDED ANSWER
        # ====================================================
        print("\nGenerating grounded legal answer...")

        gemini_start = time.perf_counter()

        answer = llm.generate_answer(question, context)

        gemini_time = time.perf_counter() - gemini_start

        print(
            f"[TIMING] Gemini generation: "
            f"{gemini_time:.3f} seconds"
        )

        # ====================================================
        # VALIDATE ANSWER
        # ====================================================
        if not answer or not answer.strip():
            raise RuntimeError("The language model returned an empty answer.")

        # ====================================================
        # TOTAL PROCESSING TIME
        # ====================================================
        total_time = time.perf_counter() - request_start

        print("\nAnswer generated successfully.")
        print(
            f"[TIMING] Total request processing: "
            f"{total_time:.3f} seconds"
        )

        # ====================================================
        # RETURN RESPONSE
        # ====================================================
        return {
            "answer": answer,
            "sources": sources
        }

    except HTTPException:
        raise

    except Exception as e:
        print("\nERROR:")
        print(type(e).__name__)
        print(str(e))

        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your question."
        )

# ============================================================

# RUN DIRECTLY

# ============================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api:app",
        host="127.0.0.1",
        port=8000,
        reload=False
    )
