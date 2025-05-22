# utils/rag_biology_helper.py

import os
import pandas as pd
import torch
import faiss
from utils.model_loader import embedding_model

DATASET_PATH = "dataset/explanation/syllubus_dataset.csv"
EMBEDDING_PATH = "dataset/explanation/rag_bio_embeddings.pt"
METADATA_PATH = "dataset/explanation/rag_bio_metadata.pkl"
FAISS_INDEX_PATH = "dataset/explanation/rag_bio_index.faiss"

def build_rag_index():
    if not os.path.exists(DATASET_PATH):
        raise FileNotFoundError(f"❌ Dataset not found at {DATASET_PATH}")

    print("🔍 Loading dataset...")
    df = pd.read_csv(DATASET_PATH, encoding='ISO-8859-1')
    df["Text Content"] = df["Text Content"].fillna("")

    model = embedding_model
    print("🧠 Encoding textbook content...")
    texts = df["Text Content"].tolist()
    embeddings = model.encode(texts, convert_to_tensor=True, normalize_embeddings=True)

    print("💾 Saving embeddings and metadata...")
    torch.save(embeddings, EMBEDDING_PATH)
    df.to_pickle(METADATA_PATH)

    emb_np = embeddings.cpu().numpy().astype("float32")
    index = faiss.IndexFlatIP(emb_np.shape[1])
    index.add(emb_np)
    faiss.write_index(index, FAISS_INDEX_PATH)

    print("✅ RAG index built and saved.")

class RAGBiology:
    def __init__(self):
        if not (os.path.exists(METADATA_PATH) and os.path.exists(FAISS_INDEX_PATH)):
            print("⚠️ Index not found. Rebuilding RAG index...")
            build_rag_index()

        print("🚀 Loading RAG components...")
        self.model = embedding_model
        self.df = pd.read_pickle(METADATA_PATH)
        self.index = faiss.read_index(FAISS_INDEX_PATH)

    def get_context(self, query: str, top_k: int = 3, max_total_words: int = 250) -> list:
        if not query.strip():
            return []

        query_emb = self.model.encode([query], convert_to_tensor=True, normalize_embeddings=True)
        query_np = query_emb.cpu().numpy().astype("float32")
        D, I = self.index.search(query_np, top_k)

        all_texts = self.df.iloc[I[0]]["Text Content"].tolist()

        selected = []
        total_words = 0
        for text in all_texts:
            word_count = len(text.split())
            if total_words + word_count > max_total_words:
                break
            selected.append(text)
            total_words += word_count

        return selected

