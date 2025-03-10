from fastapi import FastAPI
from routes.user_routes import router as user_router
from routes.mcq_routes import router as mcq_router
from routes.adaptive_quiz_routes import router as adaptive_quiz_router
from routes.response_routes import router as response_router

app = FastAPI()

# Include routes
app.include_router(user_router, prefix="/users", tags=["Users"])
app.include_router(mcq_router, prefix="/mcqs", tags=["MCQ Generation"])
app.include_router(adaptive_quiz_router, prefix="/quiz", tags=["Adaptive MCQ Generation"])
app.include_router(response_router, prefix="/responses", tags=["User Responses"])

@app.get("/")
def home():
    return {"message": "Welcome to the FastAPI Backend"}
