from uuid import UUID

from app.core.dto.question import CreateQuestionData, QuestionData
from app.core.exceptions.question import QuestionNotFoundError
from app.core.exceptions.topic import TopicNotFoundError
from app.models import Question
from app.unit_of_work.base import UnitOfWork


class QuestionService:
    """Service for app level operations for questions."""

    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def get_question(self, question_id: UUID) -> QuestionData:
        """Return a question or raise if it does not exist."""

        async with self._uow:
            question = await self._get_question_or_raise(question_id)
            return self._to_question_data(question)

    async def list_questions_by_topic(
        self,
        topic_id: UUID,
    ) -> list[QuestionData]:
        """Return questions belonging to topic or raise if the topic does not exist."""

        async with self._uow:
            await self._ensure_topic_exists(topic_id)

            questions = await self._uow.questions.get_by_topic_id(topic_id)

            return [self._to_question_data(question) for question in questions]

    async def create_question(
        self,
        data: CreateQuestionData,
    ) -> QuestionData:
        """Create a question after validating its topic."""

        async with self._uow:
            await self._ensure_topic_exists(data.topic_id)

            entity = self._to_question_model(data)
            created = await self._uow.questions.add(entity)

            await self._uow.commit()

            return self._to_question_data(created)

    async def _get_question_or_raise(
        self,
        question_id: UUID,
    ) -> Question:
        question = await self._uow.questions.get_by_id(question_id)

        if question is None:
            raise QuestionNotFoundError(question_id)

        return question

    async def _ensure_topic_exists(self, topic_id: UUID) -> None:
        topic = await self._uow.topics.get_by_id(topic_id)

        if topic is None:
            raise TopicNotFoundError(topic_id)

    @staticmethod
    def _to_question_data(question: Question) -> QuestionData:
        return QuestionData(
            id=question.id,
            topic_id=question.topic_id,
            question=question.question,
            answer=question.answer,
            difficulty=question.difficulty,
            created_at=question.created_at,
            updated_at=question.updated_at,
        )

    @staticmethod
    def _to_question_model(data: CreateQuestionData) -> Question:
        return Question(
            topic_id=data.topic_id,
            question=data.question,
            answer=data.answer,
            difficulty=data.difficulty,
        )
