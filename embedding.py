from sentence_transformers import SentenceTransformer
import torch
from typing import List

# Use a lightweight but powerful model
model = SentenceTransformer('all-MiniLM-L6-v2')

def get_embeddings(texts: List[str]):
    return model.encode(texts, batch_size=32, show_progress_bar=False, convert_to_numpy=True)