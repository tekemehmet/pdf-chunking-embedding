from pydantic import BaseModel
from typing import List, Optional

class Chunk(BaseModel):
    text: str
    page_number: int
    doc_id: str
    section_title: Optional[str] = None
    chunk_id: str
    metadata: dict

class IngestionRequest(BaseModel):
    doc_id: str
    file_path: str  # or use file upload in production