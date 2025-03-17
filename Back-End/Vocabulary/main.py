import asyncio
from fastapi import FastAPI
from routes.flashcards import router as flashcards_router
from database import load_vocab_into_db

app = FastAPI(title="Flashcard API")

@app.on_event("startup")
async def startup_db():
    """Load vocabulary into MongoDB when the API starts."""
    await load_vocab_into_db()

# Include routes
app.include_router(flashcards_router, prefix="/flashcards", tags=["Flashcards"])

@app.get("/")
async def root():
    return {"message": "Welcome to the Vocabulary Flashcard API"}
