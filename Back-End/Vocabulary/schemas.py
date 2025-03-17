from pydantic import BaseModel
from datetime import datetime

class CardSchema(BaseModel):
    top: str
    bot: str

class AnswerRequest(BaseModel):
    user_answer: str

class ReviewResponse(BaseModel):
    card: str
    quality: int
    next_review: datetime
