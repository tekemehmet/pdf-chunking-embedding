import pymupdf as fitz
import chromadb
from pdf2image import convert_from_path
from PIL import Image
import pytesseract
import re
import os
from typing import List
from embedding import get_embeddings
from chunking import split_into_semantic_chunks

chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="pdf_documents")

# ingest.py  ← REPLACE THE ENTIRE ingest_pdf FUNCTION
def ingest_pdf(doc_id: str, pdf_path: str):
    doc = fitz.open(pdf_path)
    full_text = ""
    page_texts = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        
        # If page has almost no text → it's probably scanned → OCR
        if len(text.strip()) < 100:
            print(f"Page {page_num+1} is scanned → running OCR...")
            images = convert_from_path(pdf_path, dpi=300, first_page=page_num+1, last_page=page_num+1)
            text = pytesseract.image_to_string(images[0], lang='eng')

        # Very light header/footer removal
        lines = text.split("\n")
        if len(lines) > 10:
            lines = lines[3:-3]  # drop top/bottom lines
        clean_text = "\n".join(lines).strip()

        # Add page marker for later detection
        clean_text_with_page = f"[Page {page_num + 1}]\n{clean_text}"
        page_texts.append(clean_text)
        full_text += clean_text_with_page + "\n\n"

    doc.close()  # Clean up

    # Detect sections (improved pattern)
    section_pattern = re.compile(r'(Chapter|Section)[\s\d\.:-]+(.+?)(?=\n[A-Z]|$)', re.DOTALL | re.IGNORECASE)
    sections = section_pattern.findall(full_text)

    # Chunk the full text
    chunks = split_into_semantic_chunks(full_text, max_tokens=400)
    if not chunks:
        raise Exception("No valid chunks extracted from PDF")

    # Extract figures (simple heuristic)
    figure_refs = re.findall(r'(Figure|Fig\.|Table)[\s\d\.:]+[\d]+', full_text)

    # Embed
    embeddings = get_embeddings(chunks)

    # Store each chunk
    added_count = 0
    for i, (chunk_text, embedding) in enumerate(zip(chunks, embeddings)):
        chunk_id = f"{doc_id}_chunk_{i}"

        # Extract page from chunk (now reliable with [Page X] marker)
        page_match = re.search(r'\[Page (\d+)\]', chunk_text)
        page_str = page_match.group(1) if page_match else str(i + 1)  # Fallback to chunk index

        # Extract section title
        section_title = ""
        for sec_type, title in sections:
            if title.strip().lower() in chunk_text.lower()[:300]:  # Loose match
                section_title = title.strip()[:100]  # Truncate if too long
                break

        # BUILD METADATA: ALL VALUES ARE STRINGS (no None, no "unknown")
        metadata = {
            "doc_id": doc_id,
            "page": page_str,  # Always a string number
            "section_title": section_title,  # "" if missing
            "has_figures": "true" if len(figure_refs) > 0 else "false",  # String bool
            "source": os.path.basename(pdf_path),
            "chunk_index": str(i)
        }

        # Debug print (remove in production)
        print(f"Adding chunk {i}: page={metadata['page']}, section={metadata['section_title'][:50]}...")

        # Add to ChromaDB
        collection.add(
            ids=[chunk_id],
            embeddings=[embedding.tolist()],
            documents=[chunk_text],
            metadatas=[metadata]  # Now 100% valid
        )
        added_count += 1

    print(f"Successfully ingested {doc_id} → {added_count} chunks stored in ChromaDB")