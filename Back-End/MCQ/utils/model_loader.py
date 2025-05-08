from sentence_transformers import SentenceTransformer
from llama_cpp import Llama

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

llm = Llama(
    model_path="model/llama2-q8_0.gguf",
    n_ctx=2048,
    n_threads=4,
    verbose=False
)
