from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.core.enums.question import QuestionDifficulty
from app.core.types import UNSET, _UnsetType


@dataclass(frozen=True)
class CreateQuestionData:
    topic_id: UUID
    question: str
    answer: str
    difficulty: QuestionDifficulty


@dataclass(frozen=True)
class UpdateQuestionData:
    topic_id: UUID | _UnsetType = UNSET
    question: str | _UnsetType = UNSET
    answer: str | _UnsetType = UNSET
    difficulty: QuestionDifficulty | _UnsetType = UNSET


@dataclass(frozen=True)
class QuestionData:
    id: UUID
    topic_id: UUID
    question: str
    answer: str
    difficulty: QuestionDifficulty
    created_at: datetime
    updated_at: datetime
