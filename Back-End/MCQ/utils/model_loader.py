# utils/model_loader.py
from sentence_transformers import SentenceTransformer

# Load once at import
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
