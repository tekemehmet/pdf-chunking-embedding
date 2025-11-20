# Adaptive AI Quiz Generator (RAG + PDF Ingestion Pipeline)

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-success)](https://fastapi.tiangolo.com/)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-Local_Vector_DB-orange)](https://www.trychroma.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A **production-ready PDF ingestion + RAG pipeline** that extracts text (with OCR for scanned docs), chunks intelligently, embeds with `sentence-transformers`, and stores in **ChromaDB** — ready for building adaptive quizzes, chatbots, or document Q&A systems.

Currently powers an upcoming **Adaptive AI Quiz Generator** that creates personalized difficulty-adjusted questions from any textbook or research paper.

## Features

- PDF text extraction + OCR fallback (PyMuPDF + Tesseract)
- Smart header/footer removal & section detection
- Semantic + recursive chunking
- Rich metadata (page, section, figures, doc_id)
- Embeddings with `all-MiniLM-L6-v2` (fast & accurate)
- Persistent ChromaDB vector store
- FastAPI backend with file upload & search endpoint
- 100% local, offline-first (no OpenAI keys needed)

## Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/yourusername/adaptive-ai-quiz-vector.git
cd adaptive-ai-quiz-vector
python -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run the API

uvicorn main:app --reload

Server will be live at → http://127.0.0.1:8000
Interactive docs → http://127.0.0.1:8000/docs

### 3. Ingest a PDF

Using Swagger UI (recommended for testing):

1.Go to http://127.0.0.1:8000/docs
2.POST /ingest
3.Enter doc_id → e.g., physics_101
4.Upload your PDF

```bash
curl -X POST "http://127.0.0.1:8000/ingest" \
  -F "doc_id=quantum_mechanics" \
  -F "file=@./textbook.pdf"
```

### 4. Search (Test the RAG)
```bash
curl "http://127.0.0.1:8000/search?query=Explain quantum entanglement"
```
