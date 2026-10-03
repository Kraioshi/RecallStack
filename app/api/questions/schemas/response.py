from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.core.enums.question import QuestionDifficulty


class QuestionResponse(BaseModel):
    """HTTP response representation of a question."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    topic_id: UUID
    question: str
    answer: str
    difficulty: QuestionDifficulty
    created_at: datetime
    updated_at: datetime
