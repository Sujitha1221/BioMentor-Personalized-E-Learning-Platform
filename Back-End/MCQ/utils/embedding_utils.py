import faiss
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

# Load Sentence Transformer model for embeddings
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

def load_dataset_with_embeddings(csv_path="dataset/question_dataset_with_embeddings.csv", index_path="dataset/question_embeddings.index"):
    """Loads the dataset and FAISS index for fast question retrieval."""
    try:
        dataset = pd.read_csv(csv_path, encoding="latin1").fillna("")
        index = faiss.read_index(index_path)
        return dataset, index
    except Exception as e:
        print(f"❌ Error loading dataset or FAISS index: {str(e)}")
        return None, None

def generate_text_embedding(text):
    """Generates an embedding for a given text input."""
    return embedding_model.encode([text]).astype("float32")
