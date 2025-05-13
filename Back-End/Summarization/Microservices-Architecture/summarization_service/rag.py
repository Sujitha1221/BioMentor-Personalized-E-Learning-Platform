import logging
import pandas as pd
from sentence_transformers import SentenceTransformer
import faiss
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from autocorrect import Speller
import language_tool_python
import re


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class RAGModel:
    def __init__(self, model_path, embedding_model_name, dataset_paths, max_tokens=512):
        """
        Initialize the Retrieval-Augmented Generation (RAG) Model.
        """
        try:
            # Load model and tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(model_path)
            self.embedder = SentenceTransformer(embedding_model_name)
            self.spell_checker = Speller(lang="en")
            self.grammar_tool = language_tool_python.LanguageTool("en-US")
            self.max_tokens = max_tokens
            logging.info("RAG Model components loaded successfully.")

            # Load datasets and initialize FAISS index
            self.long_texts, self.notes_content = self._load_data(
                dataset_paths)
            self.faiss_index = self._initialize_faiss(
                self.long_texts, self.notes_content
            )
            logging.info("FAISS index initialized successfully.")

        except Exception as e:
            logging.error(f"Error initializing RAG Model: {e}")
            raise

    def _load_data(self, dataset_paths):
        """
        Load and preprocess datasets from given file paths.
        """
        long_texts = []
        notes_content = []
        try:
            for dataset_path in dataset_paths:
                try:
                    df = pd.read_csv(dataset_path, encoding="ISO-8859-1")
                    if "Long Text" in df.columns:
                        long_texts.extend(df["Long Text"].tolist())
                    if "Text Content" in df.columns:
                        notes_content.extend(df["Text Content"].tolist())
                except FileNotFoundError:
                    logging.error(f"Dataset not found: {dataset_path}")
                    continue
                except pd.errors.EmptyDataError:
                    logging.error(f"Empty dataset at path: {dataset_path}")
                    continue

            if not long_texts and not notes_content:
                raise ValueError("No valid data found in datasets.")

            logging.info("Datasets loaded successfully.")
            return long_texts, notes_content

        except Exception as e:
            logging.error(f"Error loading datasets: {e}")
            raise

    def _initialize_faiss(self, long_texts, notes_content):
        """
        Initialize FAISS index with embeddings from long texts and notes.
        """
        try:
            embeddings = self.embedder.encode(long_texts + notes_content).astype(
                "float32"
            )
            index = faiss.IndexFlatL2(embeddings.shape[1])
            index.add(embeddings)
            logging.info("FAISS index created and populated successfully.")
            return index

        except Exception as e:
            logging.error(f"Error initializing FAISS index: {e}")
            raise

    def retrieve_relevant_content(self, query, k=3):
        """
        Retrieve top-k relevant content for a given query using FAISS.
        Ensures the query does not contain inappropriate words and is biology-related.
        """
        try:
            

            if not hasattr(self, "embedder") or not hasattr(self, "faiss_index"):
                logging.error(
                    "FAISS model or embedder not initialized properly.")
                return "Error: FAISS model is not properly initialized."

            query_embedding = self.embedder.encode([query]).astype("float32")
            distances, indices = self.faiss_index.search(query_embedding, k)

            if not hasattr(self, "long_texts") or not hasattr(self, "notes_content"):
                logging.error(
                    "Data lists (long_texts or notes_content) are missing.")
                return "Error: Data lists not found."

            all_content = self.long_texts + self.notes_content
            relevant_content = [
                all_content[idx] for idx in indices[0] if idx < len(all_content)
            ]

            if not relevant_content:
                logging.info(f"No relevant content found for query: {query}")
                return "No relevant content found"

            logging.info(
                f"Retrieved {len(relevant_content)} relevant content items for query: {query}"
            )
            return relevant_content

        except Exception as e:
            logging.error(f"Error retrieving relevant content: {e}")
            return "Error retrieving content"

    def _correct_and_format_text(self, text):
        """
        Correct grammar, spelling, remove semantic repetition, and format sentences.
        """
        try:
            # Step 1: Correct spelling
            corrected_text = self.spell_checker(text)

            # Step 2: Correct grammar
            matches = self.grammar_tool.check(corrected_text)
            corrected_text = language_tool_python.utils.correct(
                corrected_text, matches)

            # Step 3: Split text into sentences
            sentences = corrected_text.split(". ")

            # Step 4: Process each sentence to remove redundant phrases and words
            processed_sentences = []
            seen_phrases = set()

            for sentence in sentences:
                # Tokenize the sentence into words
                words = re.split(r"\s+", sentence)

                # Remove consecutive duplicate words and create a filtered sentence
                filtered_words = []
                last_word = None
                for word in words:
                    if word.lower() != last_word:
                        filtered_words.append(word)
                        last_word = word.lower()

                # Rejoin words to form the sentence
                filtered_sentence = " ".join(filtered_words)

                # Avoid adding semantically duplicate sentences
                if filtered_sentence.lower() not in seen_phrases:
                    processed_sentences.append(filtered_sentence.capitalize())
                    seen_phrases.add(filtered_sentence.lower())

            # Step 5: Combine processed sentences into formatted text
            formatted_text = ". ".join(processed_sentences).strip()

            # Ensure the text ends with proper punctuation
            if formatted_text and formatted_text[-1] not in ".!?":
                formatted_text += "."

            logging.info("Text successfully corrected and formatted.")
            return formatted_text
        except Exception as e:
            logging.error(f"Error correcting and formatting text: {e}")
            raise

    def postprocess_summary(self, summary):
        """
        Capitalize the first letter of each sentence, remove irrelevant spaces, repeating words,
        and ensure proper punctuation.
        """
        try:
            # Step 1: Strip unnecessary spaces and split into sentences
            summary = " ".join(summary.split())  # Remove extra spaces
            sentences = re.split(r"(?<=[.!?])\s+", summary.strip())

            processed_sentences = []
            for sentence in sentences:
                # Remove repeating words (e.g., "the the", "is is")
                words = sentence.split()
                filtered_words = []
                last_word = None
                for word in words:
                    if word.lower() != last_word:
                        filtered_words.append(word)
                        last_word = word.lower()

                # Capitalize first letter of the sentence
                processed_sentence = " ".join(filtered_words).capitalize()
                processed_sentences.append(processed_sentence)

            # Combine sentences and ensure proper punctuation
            formatted_summary = " ".join(processed_sentences).strip()
            if formatted_summary and formatted_summary[-1] not in ".!?":
                formatted_summary += "."

            logging.info("Summary successfully postprocessed.")
            return formatted_summary
        except Exception as e:
            logging.error(f"Error during summary postprocessing: {e}")
            raise

    @staticmethod
    def truncate_to_word_count(text, max_words):
        """
        Ensure the summary fits within the desired word count range.
        """
        try:
            words = text.split()
            if len(words) > max_words:
                truncated_text = " ".join(words[:max_words])
                for i in range(len(truncated_text) - 1, -1, -1):
                    if truncated_text[i] in ".!?":
                        return truncated_text[: i + 1]
                return " ".join(words[: max_words - 1]).strip()
            return text
        except Exception as e:
            logging.error(f"Error truncating text: {e}")
            raise

    def generate_summary_for_long_text(self, long_text, min_words=100, max_words=250):
        """
        Generate a summary for a given long text.
        """
        try:

            def chunk_text(text, max_tokens=500):
                """
                Helper function to chunk text into smaller parts.
                """
                words = text.split()
                return [
                    " ".join(words[i: i + max_tokens])
                    for i in range(0, len(words), max_tokens)
                ]

            max_input_words = 390
            if len(long_text.split()) > max_input_words:
                chunks = chunk_text(long_text, max_tokens=max_input_words)
                summaries = [
                    self.generate_summary_for_long_text(
                        chunk, min_words, max_words)
                    for chunk in chunks
                ]
                combined_summary = " ".join(summaries)
                return self.truncate_to_word_count(combined_summary, max_words)

            prompt = (
                f"Generate a concise, well-structured, and grammatically correct summary for the following content:\n\n"
                f"{long_text}\n\nSummary:"
            )
            inputs = self.tokenizer(
                prompt, return_tensors="pt", max_length=512, truncation=True
            )
            summary_ids = self.model.generate(
                inputs["input_ids"],
                max_length=max_words * 2,
                min_length=min_words,
                length_penalty=1.2,
                num_beams=4,
                repetition_penalty=2.0,
                early_stopping=True,
            )
            summary = self.tokenizer.decode(
                summary_ids[0], skip_special_tokens=True)
            summary = self.postprocess_summary(summary)
            return self.truncate_to_word_count(summary, max_words)
        except Exception as e:
            logging.error(f"Error generating summary: {e}")
            raise
