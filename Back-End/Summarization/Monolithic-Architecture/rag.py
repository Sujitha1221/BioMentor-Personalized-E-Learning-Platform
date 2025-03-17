from utils.dangerous_keywords import DANGEROUS_KEYWORDS
import logging
import pandas as pd
from sentence_transformers import SentenceTransformer
import faiss
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from autocorrect import Speller
import language_tool_python
import re
from better_profanity import profanity
import joblib
from textblob import TextBlob
from nltk.corpus import words, wordnet
import nltk
import asyncio
from deep_translator import GoogleTranslator
import textwrap


nltk.download("words")
nltk.download("wordnet")
ENGLISH_WORDS = set(words.words())


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

    @staticmethod
    def contains_inappropriate_content(query):
        """
        Detects inappropriate content using:
        - Profanity detection (`better-profanity`)
        - Keyword matching (manual list of dangerous topics)
        - Sentiment analysis (to catch highly negative messages)
        - Checks if the query contains valid English words
        """

        def is_valid_word(word):
            """Checks if a word is a valid English or scientific term."""
            return word in ENGLISH_WORDS or wordnet.synsets(word)

        # Step 1: Check for explicit words using `better-profanity`
        if profanity.contains_profanity(query):
            logging.warning(f"Inappropriate language detected: {query}")
            return "Your input contains inappropriate words. Please rephrase."

        # Step 2: Check for harmful intent using keyword matching
        for keyword in DANGEROUS_KEYWORDS:
            if re.search(rf"\b{re.escape(keyword)}\b", query, re.IGNORECASE):
                logging.warning(f"Query flagged for dangerous intent: {query}")
                return (
                    "Your topic/keyword is flagged as inappropriate or unsafe. Please rephrase."
                )

        # Step 3: Check for highly negative sentiment (e.g., self-harm, extreme anger)
        sentiment_score = TextBlob(query).sentiment.polarity
        if sentiment_score < -0.6:  # Negative sentiment threshold
            logging.warning(f"Highly negative sentiment detected: {query}")
            return "Your topic/keyword seems inappropriate. Please rephrase."

        # Step 4: Check if query contains only valid English words
        # Extract words from query
        query_words = re.findall(r"\b\w+\b", query.lower())

        invalid_words = [
            word for word in query_words if not is_valid_word(word)]
        if invalid_words:
            logging.warning(
                f"Query contains gibberish or non-English words: {query}")
            return "Your query contains invalid or gibberish words. Please enter proper Biology-related terms."

        # If all checks pass, return False (query is safe)
        return False

    def retrieve_relevant_content(self, query, k=3):
        """
        Retrieve top-k relevant content for a given query using FAISS.
        Ensures the query does not contain inappropriate words and is biology-related.
        """
        try:
            if self.contains_inappropriate_content(query):
                logging.warning(
                    f"Query contains inappropriate content: {query}")
                return "Your input contains inappropriate words. Please rephrase."

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

    def chunk_text(self, text: str, max_tokens: int = 512):
        """
        Splits text into chunks that fit within the model's token limit.
        Ensures chunking happens at sentence boundaries (full stops).
        """
        import re

        if max_tokens is None:
            max_tokens = self.max_tokens  # Default to initialized max_tokens

        # Split text into sentences
        # Splits at full stops, question marks, exclamation marks
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())

        chunks = []
        current_chunk = []
        token_count = 0

        for i, sentence in enumerate(sentences):
            if not sentence.strip():  # Ignore empty sentences
                continue

            # Tokenize the current sentence and check token count
            sentence_tokens = self.tokenizer(
                sentence, return_tensors="pt")["input_ids"]
            sentence_token_count = len(sentence_tokens[0])

            if token_count + sentence_token_count <= max_tokens:
                current_chunk.append(sentence)
                token_count += sentence_token_count
                # Update last full stop index

            else:
                chunks.append(" ".join(current_chunk))
                current_chunk = [sentence]
                token_count = sentence_token_count

        # Append the last chunk
        if current_chunk:
            chunks.append(" ".join(current_chunk))

        logging.info(f"Total {len(chunks)} chunks created for processing.")

        return chunks

    def generate_structured_notes(self, text: str, topic: str) -> str:
        """
        Uses the fine-tuned Flan-T5 model to structure notes from raw text.
        Processes chunked text sequentially.
        """
        text_chunks = self.chunk_text(text, self.max_tokens)
        structured_notes_list = []

        for i, chunk in enumerate(text_chunks):
            logging.info(f"Processing chunk {i+1}/{len(text_chunks)}...")

            prompt = f"Structure the following notes on {topic} with headings and bullet points:\n\n{chunk}"

            inputs = self.tokenizer(
                prompt, return_tensors="pt", max_length=1024, truncation=True
            )
            output = self.model.generate(
                **inputs, max_length=1024, do_sample=True, temperature=0.7, top_p=0.9
            )

            structured_notes = self.tokenizer.decode(
                output[0], skip_special_tokens=True
            )

            # Log the structured output for debugging
            logging.info(
                f"Chunk {i+1} processed with {len(structured_notes.split())} words."
            )

            structured_notes_list.append(structured_notes)

        # Merge all structured outputs
        full_notes = "\n".join(structured_notes_list)
        logging.info("full otes")

        logging.info(
            f"Final structured notes length: {len(full_notes.split())} words.")

        return full_notes

    async def translate_text(self, text, lang):
        """
        Translate text into Tamil ('ta') or Sinhala ('si') using deep_translator (Google backend).
        """
        target_lang = "ta" if lang == "ta" else "si"

        # Google Translate limit is 5000 characters
        max_chars = 4500
        translated_chunks = []

        try:

            text_chunks = textwrap.wrap(
                text, width=max_chars, break_long_words=False, replace_whitespace=False)

            for chunk in text_chunks:
                translated_chunk = await asyncio.to_thread(
                    GoogleTranslator(
                        source="auto", target=target_lang).translate, chunk
                )
                translated_chunks.append(translated_chunk)

            return " ".join(translated_chunks)

        except Exception as e:
            print(f"Translation failed: {e}")
            return text  # Fallback to original text if translation fails
