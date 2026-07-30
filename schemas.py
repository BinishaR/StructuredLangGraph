# schemas.py
from typing import Optional

from pydantic import BaseModel, Field


class UserQuery(BaseModel):
    """Request body for asking a question."""

    question: str = Field(
        description="Customer question for the bank assistant",
        min_length=3,
        max_length=500,
        examples=["What is mobile money?"],
    )
    session_id: Optional[str] = Field(
        default=None,
        description="Session ID for conversation memory. Same ID = remembers context.",
        examples=["customer-001"],
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "question": "What is mobile money?",
                "session_id": None,
            }
        }
    }


class BotResponse(BaseModel):
    """Successful response from the bank assistant."""

    status: str = Field(default="success")
    question: str = Field(description="Original question asked")
    answer: str = Field(description="Answer from the FAQ database")
    session_id: Optional[str] = Field(
        default=None,
        description="Session ID used",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "success",
                "question": "What is mobile money?",
                "answer": "Mobile Money is a convenient banking channel...",
                "session_id": None,
            }
        }
    }


class ErrorResponse(BaseModel):
    """Error response."""

    status: str = "error"
    message: str
    detail: Optional[str] = None
    
class UpdateVectorstoreResponse(BaseModel):
    """Response after a vectorstore rebuild."""

    status: str = Field(default="success")
    message: str
    vector_count: int