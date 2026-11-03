# NyayaSetu – Tenant Rights & Rental Dispute Navigator

An AI-powered legal information assistant designed to help tenants and landlords understand rental legislation and common tenancy-related disputes through natural-language questions.

**Version:** 1.0.0
**Initial Jurisdiction:** Karnataka, India
**Primary Legislation:** Karnataka Rent Act, 1999

## Project Overview

NyayaSetu is an AI-powered legal information platform that uses Retrieval-Augmented Generation (RAG) to provide answers grounded in official tenancy legislation.

The initial release focuses on the Karnataka Rent Act, 1999. Users can submit legal questions and receive explanations supported by relevant statutory provisions and source references.

## Key Features

* PDF-based legislation extraction.
* Custom PDF text decoding.
* Page-aware document chunking.
* Sentence-transformer embeddings.
* ChromaDB vector storage.
* Semantic legal document retrieval.
* Gemini-powered question answering.
* Source references with section and page information.
* FastAPI backend.
* Browser-based frontend.

## Technology Stack

| Component            | Technology            |
| -------------------- | --------------------- |
| Programming Language | Python                |
| Backend              | FastAPI               |
| AI Model             | Google Gemini         |
| Vector Database      | ChromaDB              |
| Embeddings           | Sentence Transformers |
| PDF Processing       | pypdf                 |
| Frontend             | HTML, CSS, JavaScript |
| API Server           | Uvicorn               |

## System Architecture

```text
User Question
      |
      v
FastAPI Backend
      |
      v
Query Embedding
      |
      v
ChromaDB Retrieval
      |
      v
Relevant Legal Passages
      |
      v
Gemini AI
      |
      v
Grounded Legal Response
      |
      v
Answer with Source References
```

## Document Processing Pipeline

```text
Official Karnataka Legislation PDF
              |
              v
         PDF Extraction
              |
              v
       Custom Text Decoding
              |
              v
        Document Chunking
              |
              v
       Embedding Generation
              |
              v
           ChromaDB
```

## Project Structure

```text
Tenant-Rights-Navigator/
|
|-- api.py
|-- app.py
|-- streamlit_app.py
|-- rebuild_database.py
|-- requirements.txt
|-- README.md
|-- .gitignore
|
|-- frontend/
|
|-- data/
|   |-- legislation/
|       |-- karnataka/
|
|-- chroma_db/
|
|-- src/
|   |-- __init__.py
|   |-- embeddings.py
|   |-- chunker.py
|   |-- pdf_loader.py
|   |-- llm.py
|   |-- vector_store.py
|
|-- tests/
```

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/raidiv3608/Tenant-Rights-Navigator.git
cd Tenant-Rights-Navigator
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_api_key_here
```

Never upload your actual API key to GitHub.

### 5. Add the legislation PDF

Place the Karnataka Rent Act legislation PDF in:

```text
data/legislation/karnataka/
```

### 6. Rebuild the vector database

```bash
python rebuild_database.py
```

### 7. Start the FastAPI backend

```bash
uvicorn api:app --reload
```

Open the API documentation:

```text
http://127.0.0.1:8000/docs
```

## Legal Disclaimer

NyayaSetu provides general legal information for educational and informational purposes. It is not a substitute for professional legal advice.

Users should consult a qualified legal professional for advice concerning their specific circumstances.

## Future Development – Version 2.0

Planned improvements include:

* Citizen-friendly natural-language problem descriptions.
* Automatic identification of relevant legal provisions.
* Category-based exploration of tenant rights.
* User registration and authentication.
* Subscription-based access plans.
* Payment gateway integration.
* Improved user experience.
* Expanded legal knowledge bases.

## Project Vision

**You don't need to know the law to understand your rights.**

NyayaSetu aims to make tenancy-related legal information more accessible, understandable and useful to ordinary citizens.

---

Developed as an independent software engineering project focused on AI, legal information retrieval and practical problem solving.
