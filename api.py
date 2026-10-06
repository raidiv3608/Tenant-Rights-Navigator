import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.embeddings import EmbeddingModel
from src.vector_store import VectorStore
from src.llm import GeminiLLM


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="Tenant Rights Navigator API",
    description="Backend API for the Tenant Rights Navigator",
    version="1.0.0"
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


    try:

        print("\n----------------------------------------------")
        print("QUESTION")
        print("----------------------------------------------")

        print(question)


        # ====================================================
        # EMBED USER QUESTION
        # ====================================================

        print("\nSearching legal database...")

        query_embedding = embedding_model.embed_text(
            question
        )


        # ====================================================
        # SEARCH CHROMADB
        # ====================================================

        results = vector_store.search(
            question,
            query_embedding,
            n_results=5
        )


        if not results:

            return {
                "answer": (
                    "The available legal database did not "
                    "return any relevant material for this question."
                ),
                "sources": []
            }


        # ====================================================
        # BUILD LEGAL CONTEXT
        # ====================================================

        context_parts = []

        for result in results:

            metadata = result["metadata"]

            context_parts.append(
                f"""
Source: {metadata.get('source', 'Unknown source')}
Jurisdiction: {metadata.get('jurisdiction', 'Unknown')}
Page: {metadata.get('page', 'Unknown')}

Legal Text:
{result['text']}
"""
            )


        context = (
            "\n-----------------------------\n"
            .join(context_parts)
        )


        # ====================================================
        # GENERATE GROUNDED ANSWER
        # ====================================================

        print("\nGenerating grounded legal answer...")

        answer = llm.generate_answer(
            question,
            context
        )


        # ====================================================
        # PREPARE SOURCES
        # ====================================================

        sources = []

        for result in results:

            metadata = result["metadata"]

            sources.append(
                {
                    "source": metadata.get(
                        "source",
                        "Unknown source"
                    ),

                    "jurisdiction": metadata.get(
                        "jurisdiction",
                        "Unknown"
                    ),

                    "page": metadata.get(
                        "page",
                        "Unknown"
                    ),

                    "text": result["text"]
                }
            )


        print("\nAnswer generated successfully.")


        # ====================================================
        # RETURN RESPONSE
        # ====================================================

        return {
            "answer": answer,
            "sources": sources
        }


    except Exception as e:

        print("\nERROR:")
        print(type(e).__name__)
        print(str(e))

        raise HTTPException(
            status_code=500,
            detail=str(e)
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
        reload=True
    )