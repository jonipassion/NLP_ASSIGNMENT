# src/api/schemas.py
from pydantic import BaseModel, validator
from typing import Optional, List

ALLOWED_DIFFICULTIES = {"easy", "medium", "hard"}
FORBIDDEN_WORDS = ["gambling", "politics", "violence", "porn", "drugs"]

class QuizRequest(BaseModel):
    topic: str
    difficulties: Optional[List[str]] = ["medium"]
    hide_answers: Optional[bool] = False
    session_id: Optional[str] = None

    # -----------------------------
    # Validators
    # -----------------------------
    @validator("topic")
    def topic_must_be_nonempty_and_safe(cls, v):
        if not v.strip():
            raise ValueError("Topic cannot be empty")
        if len(v) > 100:
            raise ValueError("Topic too long (max 100 characters)")
        if any(word in v.lower() for word in FORBIDDEN_WORDS):
            raise ValueError("Topic contains non-educational content")
        return v.strip()

    @validator("difficulties", each_item=True)
    def validate_difficulties(cls, v):
        if v.lower() not in ALLOWED_DIFFICULTIES:
            raise ValueError(f"Invalid difficulty '{v}'. Allowed: {ALLOWED_DIFFICULTIES}")
        return v.lower()


class QuizQuestion(BaseModel):
    question: str
    type: str  # "multiple-choice" or "short-answer"
    options: Optional[List[str]] = None
    answer: str
    difficulty: Optional[str] = None
    show_answer: Optional[bool] = True


class QuizResponse(BaseModel):
    topic: str
    quiz: List[QuizQuestion]
    session_id: str
