from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.mcq_routes import router as mcq_router
from routes.adaptive_quiz_routes import router as adaptive_quiz_router
from routes.response_routes import router as response_router
from routes.topic_based_quiz_routes import router as topic_router
from routes.explanation_routes import router as explanation_router

app = FastAPI()

#  Correct CORS Middleware Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://20.193.152.91",
        "http://127.0.0.1:3000",
        "http://localhost:3000",
    ],  #  Allow both localhost & 127.0.0.1
    allow_credentials=True,  #  Allows cookies (refresh token)
    allow_methods=["*"],  #  Allow all HTTP methods
    allow_headers=["*"],  #  Allow all headers
)

#  Include routers AFTER CORS middleware
app.include_router(mcq_router, prefix="/mcqs", tags=["MCQ Generation"])
app.include_router(
    adaptive_quiz_router, prefix="/quiz", tags=["Adaptive MCQ Generation"]
)
app.include_router(response_router, prefix="/responses", tags=["User Responses"])
app.include_router(topic_router, prefix="/topic", tags=["Topic based quiz"])
app.include_router(explanation_router, prefix="/explanations", tags=["MCQ Explanation"])


@app.get("/")
def home():
    return {"message": "Welcome to the FastAPI Backend"}
