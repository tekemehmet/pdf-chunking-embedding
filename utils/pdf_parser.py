import fitz  # PyMuPDF
import pymupdf as fitz
from typing import List, Tuple, Dict
import re

def extract_text_with_layout(pdf_path: str) -> List[Dict]:
    doc = fitz.open(pdf_path)
    pages = []

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        blocks = page.get_text("dict")["blocks"]
        lines = []

        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        lines.append({
                            "text": span["text"],
                            "bbox": span["bbox"],
                            "size": span["size"],
                            "font": span["font"],
                            "page": page_num + 1
                        })
        # Sort lines top to bottom
        lines.sort(key=lambda x: x["bbox"][1])
        pages.append({"page": page_num + 1, "lines": lines})

    return pages