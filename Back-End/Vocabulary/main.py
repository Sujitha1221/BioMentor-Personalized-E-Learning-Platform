from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.flashcards import router as flashcards_router
from routes.leaderboard import router as leaderboard_router  # ✅ Import Leaderboard Router
from database import load_vocab_into_db

app = FastAPI(title="Flashcard API")

# ✅ Ensure CORS middleware is added
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_db():
    """Load vocabulary into MongoDB when the API starts."""
    await load_vocab_into_db()

# ✅ Ensure Leaderboard Router is included
app.include_router(flashcards_router, prefix="/flashcards", tags=["Flashcards"])
app.include_router(leaderboard_router, prefix="/leaderboard", tags=["Leaderboard"])  # ✅ Add Leaderboard Router

@app.get("/")
async def root():
    return {"message": "Welcome to the Vocabulary Flashcard API"}
