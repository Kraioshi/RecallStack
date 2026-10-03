from uuid import UUID, uuid4

from app.core.enums.question import QuestionDifficulty
from app.core.helpers.dates import now
from app.models import Question
from app.models.topic import Topic


def make_topic(
    *,
    name: str = "Python",
    slug: str = "python",
    topic_id: UUID | None = None,
    parent_id: UUID | None = None,
    description: str | None = None,
) -> Topic:
    current_time = now()

    return Topic(
        id=topic_id or uuid4(),
        name=name,
        slug=slug,
        parent_id=parent_id,
        description=description,
        created_at=current_time,
        updated_at=current_time,
    )


def make_question(
    *,
    question: str = "What is the GIL?",
    answer: str = "Global Interpreter Lock.",
    difficulty: QuestionDifficulty = QuestionDifficulty.MEDIUM,
    question_id: UUID | None = None,
    topic_id: UUID | None = None,
) -> Question:
    current_time = now()

    return Question(
        id=question_id or uuid4(),
        topic_id=topic_id or uuid4(),
        question=question,
        answer=answer,
        difficulty=difficulty,
        created_at=current_time,
        updated_at=current_time,
    )
