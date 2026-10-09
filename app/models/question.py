from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import (
    DateTime,
    Enum,
    FetchedValue,
    ForeignKey,
    Index,
    Text,
    Uuid,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums.question import QuestionDifficulty
from app.database.base import Base

if TYPE_CHECKING:
    from app.models.topic import Topic

QUESTION_UNIQUE_INDEX_NAME = "uq_questions_topic_normalized_text"


class Question(Base):
    __tablename__ = "questions"

    # Same question text cannot appear twice inside one topic.
    # Lower + btrim keeps comparison case-insensitive and ignores edge whitespace.
    __table_args__ = (
        Index(
            QUESTION_UNIQUE_INDEX_NAME,
            "topic_id",
            text("lower(btrim(question))"),
            unique=True,
        ),
    )

    __mapper_args__ = {
        "eager_defaults": True,
    }

    id: Mapped[UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid4,
    )

    # no auto index creation on FK cols
    topic_id: Mapped[UUID] = mapped_column(
        ForeignKey("topics.id"),
        nullable=False,
        index=True,
    )

    question: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    answer: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    difficulty: Mapped[QuestionDifficulty] = mapped_column(
        Enum(
            QuestionDifficulty,
            name="question_difficulty",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        server_onupdate=FetchedValue(),
    )

    topic: Mapped["Topic"] = relationship(
        back_populates="questions",
    )
