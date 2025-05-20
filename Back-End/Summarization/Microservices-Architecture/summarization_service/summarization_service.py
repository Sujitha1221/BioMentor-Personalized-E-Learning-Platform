import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from rag import RAGModel

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = FastAPI()

# Initialize the RAG Model
logging.info("Initializing RAG Model...")
try:
    rag_model = RAGModel(
        model_path="/app/flan_t5_finetuned_model",
        embedding_model_name="all-MiniLM-L6-v2",
        dataset_paths=["/app/datasets/bio_summary_keywords.csv", "/app/datasets/biology_information_retrieval_sample.csv"]

        
    )
    logging.info("RAG Model initialized successfully.")
except Exception as e:
    logging.error(f"Failed to initialize RAG Model: {e}")
    raise RuntimeError("RAG Model initialization failed.")

class QueryRequest(BaseModel):
    query: str

class SummarizationRequest(BaseModel):
    text: str
    word_count: int

@app.post("/summarize/")
async def summarize_text(request: SummarizationRequest):
    """
    Summarize a given text with a specified word count.
    """
    try:
        logging.info("Received summarization request.")


        summary = rag_model.generate_summary_for_long_text(request.text, max_words=request.word_count)
        logging.info("Summarization successful.")
        return {"summary": summary}
    
    except Exception as e:
        logging.error(f"Summarization failed: {e}")
        raise HTTPException(status_code=500, detail="Summarization failed.")


@app.post("/retrieve/")
async def retrieve_content(request: QueryRequest):
    """
    Retrieve relevant content for the given query.
    """
    try:
        logging.info(f"Processing retrieval request for query: {request.query}")


        relevant_texts = rag_model.retrieve_relevant_content(request.query)
        if not relevant_texts:
            logging.warning(f"No relevant content found for query: {request.query}")
            raise HTTPException(status_code=400, detail="No relevant content found.")

        logging.info(f"Retrieved {len(relevant_texts)} relevant texts for query: {request.query}")
        return {"texts": relevant_texts}

    except Exception as e:
        logging.error(f"Error retrieving content for query '{request.query}': {e}")
        raise HTTPException(status_code=500, detail="Retrieval failed.")


if __name__ == "__main__":
    logging.info("Starting Summarization Service on port 8002")
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
