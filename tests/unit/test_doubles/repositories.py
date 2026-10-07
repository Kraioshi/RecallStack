from uuid import UUID, uuid4

from app.core.dto.question import RandomQuestionCriteria
from app.core.enums.question import QuestionDifficulty
from app.core.helpers.dates import now
from app.models import Question, Topic


class FakeTopicRepository:
    """
    In-memory TopicRepository implementation for service unit tests.
    """

    def __init__(self, topics: list[Topic] | None = None) -> None:
        self._topics = list(topics or [])

    async def get_by_id(self, topic_id: UUID) -> Topic | None:
        return next(
            (topic for topic in self._topics if topic.id == topic_id),
            None,
        )

    async def get_roots(self) -> list[Topic]:
        return [topic for topic in self._topics if topic.parent_id is None]

    async def get_children(self, parent_id: UUID) -> list[Topic]:
        return [topic for topic in self._topics if topic.parent_id == parent_id]

    async def get_by_slug(
        self,
        slug: str,
        parent_id: UUID | None,
    ) -> Topic | None:
        return next(
            (
                topic
                for topic in self._topics
                if topic.slug == slug and topic.parent_id == parent_id
            ),
            None,
        )

    async def add(self, topic: Topic) -> Topic:
        # PostgreSQL normally populates database-generated fields during flush().
        # The fake has no database, so it simulates the values the service relies on.
        timestamp = now()
        if topic.id is None:
            topic.id = uuid4()

        if topic.created_at is None:
            topic.created_at = timestamp

        if topic.updated_at is None:
            topic.updated_at = timestamp

        self._topics.append(topic)

        return topic

    async def delete(self, topic: Topic) -> None:
        self._topics.remove(topic)

    async def get_all(self) -> list[Topic]:
        return list(self._topics)


class FakeQuestionRepository:
    """
    In-memory QuestionRepository implementation for service unit tests.
    """

    def __init__(self, questions: list[Question] | None = None) -> None:
        self._questions = list(questions or [])
        self.last_random_criteria: RandomQuestionCriteria | None = None

    async def get_by_id(self, question_id: UUID) -> Question | None:
        return next(
            (question for question in self._questions if question.id == question_id),
            None,
        )

    async def get_by_topic_id(self, topic_id: UUID) -> list[Question]:
        return [
            question for question in self._questions if question.topic_id == topic_id
        ]

    async def add(self, question: Question) -> Question:
        # PostgreSQL normally populates database-generated fields during flush().
        # The fake has no database, so it simulates the values the service relies on.
        timestamp = now()

        if question.id is None:
            question.id = uuid4()

        if question.created_at is None:
            question.created_at = timestamp

        if question.updated_at is None:
            question.updated_at = timestamp

        self._questions.append(question)

        return question

    async def delete(self, question: Question) -> None:
        self._questions.remove(question)

    async def count_by_topic(self) -> dict[UUID, int]:
        counts: dict[UUID, int] = {}

        for question in self._questions:
            counts[question.topic_id] = counts.get(question.topic_id, 0) + 1

        return counts

    async def count_by_topic_and_difficulty(
        self,
    ) -> dict[UUID, dict[QuestionDifficulty, int]]:
        counts: dict[UUID, dict[QuestionDifficulty, int]] = {}

        for question in self._questions:
            topic_counts = counts.setdefault(question.topic_id, {})

            topic_counts[question.difficulty] = (
                topic_counts.get(question.difficulty, 0) + 1
            )

        return counts

    async def get_random(
        self,
        criteria: RandomQuestionCriteria,
    ) -> Question | None:
        self.last_random_criteria = criteria

        return self._questions[0] if self._questions else None
