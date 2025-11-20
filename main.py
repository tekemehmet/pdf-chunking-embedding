# main.py
from fastapi import FastAPI, UploadFile, File, HTTPException,Form
from fastapi.responses import JSONResponse
import shutil
import os
from pydantic import BaseModel
from typing import Optional

# === Define models directly here to avoid import issues ===
class IngestionRequest(BaseModel):
    doc_id: str

# If you still want to keep models.py, just add this fallback:
try:
    from models import IngestionRequest as _ModelCheck
except ImportError:
    pass  # We're using the local definition above
# ============================================================

from ingest import ingest_pdf
import chromadb

app = FastAPI(title="PDF Ingestion API with OCR & Vector Indexing")

# Initialize Chroma collection
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="pdf_documents")

UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/ingest")
async def ingest_document(
    doc_id: str = Form(...),                  # ← text field
    file: UploadFile = File(...)              # ← file upload
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are allowed")

    # Save uploaded file
    file_path = os.path.join(UPLOAD_DIR, f"{doc_id}_{file.filename}")
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        ingest_pdf(doc_id, file_path)
        return JSONResponse({
            "status": "success",
            "doc_id": doc_id,
            "filename": file.filename,
            "chunks_added": len(collection.get(ids=collection.get()["ids"]))  # rough count
        })
    except Exception as e:
        raise HTTPException(500, f"Ingestion failed: {str(e)}")

@app.get("/search")
async def search(query: str, top_k: int = 5):
    from embedding import model
    query_emb = model.encode([query])[0]

    results = collection.query(
        query_embeddings=[query_emb.tolist()],
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )

    return {
        "query": query,
        "results": [
            {
                "text": doc,
                "metadata": meta,
                "score": round(dist, 4)
            }
            for doc, meta, dist in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0]
            )
        ]
    }

@app.get("/")
async def root():
    return {"message": "PDF RAG Ingestion API is running! POST to /ingest"}