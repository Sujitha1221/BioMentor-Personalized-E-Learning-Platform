from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.flashcards import router as flashcards_router
from routes.leaderboard import router as leaderboard_router
from database import load_vocab_into_db
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    await load_vocab_into_db()
    yield
    # You can also add shutdown logic here if needed

app = FastAPI(title="Flashcard API", lifespan=lifespan)

# ✅ Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Include routers
app.include_router(flashcards_router, prefix="/flashcards", tags=["Flashcards"])
app.include_router(leaderboard_router, prefix="/leaderboard", tags=["Leaderboard"])

@app.get("/")
async def root():
    return {"message": "Welcome to the Vocabulary Flashcard API"}