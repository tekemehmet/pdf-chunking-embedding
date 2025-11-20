import re
from typing import List, Dict 

def split_into_semantic_chunks(text: str, max_tokens: int = 500) -> List[str]:
    # Split by sections first
    sections = re.split(r'\n(?=Chapter|Section|[\d]+\.[\d]*\s)', text)
    chunks = []

    current_chunk = ""
    for section in sections:
        if len(current_chunk.split()) + len(section.split()) > max_tokens:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = section
        else:
            current_chunk += "\n" + section

        if len(current_chunk.split()) > max_tokens:
            # Fallback: split by paragraphs
            paragraphs = current_chunk.split("\n\n")
            temp = ""
            for p in paragraphs:
                if len(temp.split()) + len(p.split()) > max_tokens:
                    if temp:
                        chunks.append(temp.strip())
                    temp = p
                else:
                    temp += "\n\n" + p
            current_chunk = temp

    if current_chunk:
        chunks.append(current_chunk.strip())

    return [c for c in chunks if len(c.strip()) > 50]