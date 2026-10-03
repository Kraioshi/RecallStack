from uuid import UUID

from pydantic import BaseModel, Field, model_validator

from app.core.enums.question import QuestionDifficulty


class CreateQuestionRequest(BaseModel):
    topic_id: UUID
    question: str = Field(min_length=1)
    answer: str = Field(min_length=1)
    difficulty: QuestionDifficulty


class UpdateQuestionRequest(BaseModel):
    """Partial question update payload.

    Fields omitted from the request are left unchanged.
    All fields are optional so they may be omitted, but none may
    explicitly be set to null.
    """

    topic_id: UUID | None = None
    question: str | None = Field(default=None, min_length=1)
    answer: str | None = Field(default=None, min_length=1)
    difficulty: QuestionDifficulty | None = None

    @model_validator(mode="after")
    def validate_update_fields(self) -> "UpdateQuestionRequest":
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided")

        if "topic_id" in self.model_fields_set and self.topic_id is None:
            raise ValueError("topic_id cannot be null")

        if "question" in self.model_fields_set and self.question is None:
            raise ValueError("question cannot be null")

        if "answer" in self.model_fields_set and self.answer is None:
            raise ValueError("answer cannot be null")

        if "difficulty" in self.model_fields_set and self.difficulty is None:
            raise ValueError("difficulty cannot be null")

        return self
