from sentence_transformers import SentenceTransformer
import pandas as pd
import numpy as np
import faiss
from sklearn.cluster import KMeans

# Load original dataset
dataset = pd.read_csv("merged_mcq_dataset.csv", encoding="latin1").fillna("")

# Ensure required columns exist
required_columns = ["Question Text", "Option 1", "Option 2", "Option 3", "Option 4", "Option 5", "Correct Answer", "Difficulty Level"]
for col in required_columns:
    if col not in dataset.columns:
        raise ValueError(f"Missing column in dataset: {col}")

# Combine question, options, and correct answer for better context representation
dataset["Combined"] = (
    dataset["Question Text"] + " " +
    dataset["Option 1"] + " " +
    dataset["Option 2"] + " " +
    dataset["Option 3"] + " " +
    dataset["Option 4"] + " " +
    dataset["Option 5"] + " " +
    "Correct Answer: " + dataset["Correct Answer"]
)

# Load Sentence Transformer model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Generate embeddings
dataset["embeddings"] = dataset["Combined"].apply(lambda x: embedding_model.encode(x).tolist())

# Convert embeddings to NumPy array
embeddings_matrix = np.array(dataset["embeddings"].tolist()).astype("float32")

# Save dataset with embeddings **including Difficulty Level (as separate column)**
dataset.to_csv("question_dataset_with_embeddings.csv", index=False)

# Create FAISS index
index = faiss.IndexFlatL2(embeddings_matrix.shape[1])
index.add(embeddings_matrix)

# Save FAISS index
faiss.write_index(index, "question_embeddings.index")
np.save("question_embeddings.npy", embeddings_matrix)

# **Topic-Based Clustering** (Ensures diverse question selection)
NUM_CLUSTERS = 10
kmeans = KMeans(n_clusters=NUM_CLUSTERS, random_state=42, n_init=10)
dataset["Cluster"] = kmeans.fit_predict(embeddings_matrix)

# Save dataset with Clusters & Difficulty Level for retrieval
dataset.to_csv("question_dataset_with_clusters.csv", index=False)

print(" Embeddings, FAISS index, and Topic Clusters created successfully!")
