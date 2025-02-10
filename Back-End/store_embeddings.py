import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

def load_and_clean_qa_dataset(file_path):
    """
    Load and clean the Q&A dataset.
    """
    logging.info(f"Loading Q&A dataset from {file_path}")
    qa_df = pd.read_csv(file_path, encoding='ISO-8859-1')
    qa_df['Question'] = qa_df['Question'].fillna('')
    qa_df['Answer'] = qa_df['Answer'].fillna('')
    qa_df['Type'] = qa_df['Type'].fillna('structured')
    qa_df = qa_df.drop_duplicates()
    logging.info("Q&A dataset cleaned and duplicates removed.")
    logging.debug(f"Q&A Dataset Preview:\n{qa_df.head()}")
    qa_df.to_csv('cleaned_question_and_answer.csv', index=False)
    logging.info("Q&A dataset saved as 'cleaned_question_and_answer.csv'")
    return qa_df


def load_and_clean_notes_dataset(file_path):
    """
    Load and clean the Notes dataset.
    """
    logging.info(f"Loading Notes dataset from {file_path}")
    notes_df = pd.read_csv(file_path, encoding='ISO-8859-1')
    notes_df['Text Content'] = notes_df['Text Content'].fillna('')
    notes_df['Combined Text'] = notes_df['Topic'] + " - " + notes_df['Sub-topic'] + "\n" + notes_df['Text Content']
    logging.info("Notes dataset cleaned.")
    logging.debug(f"Notes Dataset Preview:\n{notes_df.head()}")
    notes_df.to_csv('cleaned_Notes.csv', index=False)
    logging.info("Notes dataset saved as 'cleaned_Notes.csv'")
    return notes_df


def chunk_text(text, chunk_size=300, overlap=50):
    """
    Split long text into chunks of fixed size with overlap.
    """
    words = text.split()
    chunks = [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size - overlap)]
    logging.debug(f"Chunked text into {len(chunks)} chunks.")
    return chunks


def process_chunked_notes(notes_df, chunk_size=300, overlap=50):
    """
    Chunk the 'Combined Text' field in the Notes dataset.
    """
    logging.info("Processing chunked notes...")
    chunked_notes = []
    for _, row in notes_df.iterrows():
        chunks = chunk_text(row['Combined Text'], chunk_size, overlap)
        for chunk in chunks:
            chunked_notes.append({
                'Document ID': row['Document ID'],
                'Chunk': chunk
            })
    chunked_notes_df = pd.DataFrame(chunked_notes)
    logging.info("Chunking complete.")
    logging.debug(f"Chunked Notes Preview:\n{chunked_notes_df.head()}")
    return chunked_notes_df


def generate_embeddings(embedder, texts):
    """
    Generate embeddings for a list of texts using a SentenceTransformer model.
    """
    logging.info(f"Generating embeddings for {len(texts)} texts.")
    logging.info("Embeddings generated successfully.")
    return embedder.encode(texts)


def create_and_save_faiss_index(embeddings, file_path):
    """
    Initialize a FAISS index for L2 similarity, populate it with embeddings, and save to a file.
    """
    logging.info("Creating FAISS index...")
    embedding_dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(embedding_dim)
    
    # Populate the index
    index.add(embeddings)
    
    # Save the index
    faiss.write_index(index, file_path)
    logging.info(f"FAISS index created and saved to {file_path}")
    
    return index


def main():
    # File paths
    qa_file = 'questionanswer.csv'
    notes_file = 'Notes.csv'
    faiss_index_file = 'faiss_index.bin'

    try:
        # Load datasets
        qa_df = load_and_clean_qa_dataset(qa_file)
        notes_df = load_and_clean_notes_dataset(notes_file)

        # Chunk Notes dataset
        chunked_notes_df = process_chunked_notes(notes_df)

        # Load the embedding model
        logging.info("Loading SentenceTransformer model...")
        embedder = SentenceTransformer('sentence-transformers/multi-qa-mpnet-base-dot-v1')

        # Generate embeddings
        qa_embeddings = generate_embeddings(embedder, qa_df['Question'].tolist())
        notes_embeddings = generate_embeddings(embedder, chunked_notes_df['Chunk'].tolist())

        # Combine embeddings
        logging.info("Combining Q&A and Notes embeddings...")
        all_embeddings = np.vstack([qa_embeddings, notes_embeddings])

        # Create and save the FAISS index
        create_and_save_faiss_index(all_embeddings, faiss_index_file)

    except Exception as e:
        logging.error(f"An error occurred: {e}", exc_info=True)


if __name__ == "__main__":
    main()