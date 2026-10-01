# 🏠 Tenant Rights Navigator

An AI-powered legal-information assistant designed to help tenants understand rental agreements, tenancy laws, and common rental disputes in clear, simple language.

> **Current Status:** 🚧 Early Development — Karnataka V1

## 🎯 Project Overview

Tenant Rights Navigator combines **document processing, semantic search, vector databases, and generative AI** to provide grounded information from official tenancy legislation.

The first version focuses on the **Karnataka Rent Act, 1999**.

The long-term goal is to build a jurisdiction-aware platform that can help tenants:

* Understand relevant tenancy provisions
* Identify potentially important clauses in rental agreements
* Find relevant sections of tenancy legislation
* Understand rental-dispute issues in simple language
* Generate structured, formal communication drafts
* Trace answers back to their underlying legal sources

## 🧠 Current Architecture

```text
User Question
      ↓
Query Embedding
      ↓
ChromaDB
      ↓
Relevant Legal Chunks
      ↓
Gemini
      ↓
Grounded Legal Information
```

### Current RAG Pipeline

```text
Official Karnataka Legislation
          ↓
PDF Extraction
          ↓
Custom PDF Encoding Decoder
          ↓
Page-Aware Chunking
          ↓
Embeddings
          ↓
ChromaDB
          ↓
Semantic Retrieval
```

## 🛠️ Technology Stack

* **Python**
* **Google Gemini API**
* **ChromaDB**
* **Sentence-transformer embeddings**
* **pypdf**
* **Git / GitHub**
* **VS Code**

## 📂 Project Structure

```text
Tenant-Rights-Navigator/
│
├── app.py
├── requirements.txt
├── README.md
│
├── data/
│   └── legislation/
│       └── karnataka/
│           └── 34 of 2001 (E).pdf
│
└── src/
    ├── __init__.py
    ├── chunker.py
    ├── embeddings.py
    ├── llm.py
    ├── pdf_loader.py
    ├── pipeline.py
    ├── prompts.py
    └── vector_store.py
```

## ✅ Current Progress

* [x] Python project environment
* [x] Gemini API connection
* [x] PDF text extraction
* [x] Custom decoding for the Karnataka legislation PDF
* [x] Page-aware document chunking
* [x] Embedding generation
* [x] ChromaDB vector storage
* [x] Semantic retrieval
* [x] Karnataka legal-source metadata
* [ ] Retrieval precision improvements
* [ ] Gemini + RAG integration
* [ ] Source/citation display
* [ ] Tenant lease PDF analysis
* [ ] Red-flag clause detection
* [ ] Formal notice generation
* [ ] Streamlit interface
* [ ] Multi-jurisdiction support
* [ ] Production deployment

## ⚖️ Legal Disclaimer

Tenant Rights Navigator is intended to provide **general legal information and educational assistance**. It is not a substitute for advice from a qualified lawyer or legal professional.

The system should rely on authoritative legal sources and clearly identify the jurisdiction and source of information wherever possible.

## 🚀 Future Vision

The project is being developed initially as a college and portfolio project, with the architecture designed to potentially evolve into a broader tenant-support platform.

Future versions may support:

* Multiple Indian states and jurisdictions
* Rental agreement analysis
* Deposit and deduction disputes
* Notice and eviction information
* Automated document analysis
* Source-linked legal explanations
* Tenant-landlord communication assistance
* A user-friendly web application

---

**Built as an independent software engineering project focused on AI, RAG, legal-information retrieval, and practical problem solving.**
