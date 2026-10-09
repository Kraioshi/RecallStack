from uuid import UUID

from app.core.dto.question import (
    CreateQuestionData,
    QuestionData,
    RandomQuestionCriteria,
    UpdateQuestionData,
)
from app.core.exceptions.question import (
    QuestionAlreadyExistsError,
    QuestionNotFoundError,
    RandomQuestionNotFoundError,
)
from app.core.exceptions.topic import TopicNotFoundError
from app.core.types.common import is_set
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
        """Create a question after validating its topic and uniqueness."""

        async with self._uow:
            await self._ensure_topic_exists(data.topic_id)
            await self._ensure_question_is_unique(data.topic_id, data.question)

            entity = self._to_question_model(data)
            created = await self._uow.questions.add(entity)

            await self._uow.commit()

            return self._to_question_data(created)

    async def update_question(
        self,
        question_id: UUID,
        data: UpdateQuestionData,
    ) -> QuestionData:
        """Update a question or raise if it does not exist."""

        async with self._uow:
            question = await self._get_question_or_raise(question_id)

            topic_id = data.topic_id
            if is_set(topic_id) and topic_id != question.topic_id:
                await self._ensure_topic_exists(topic_id)

            if is_set(data.topic_id) or is_set(data.question):
                next_topic_id = (
                    data.topic_id if is_set(data.topic_id) else question.topic_id
                )
                next_text = (
                    data.question if is_set(data.question) else question.question
                )

                await self._ensure_question_is_unique(
                    next_topic_id,
                    next_text,
                    exclude_id=question.id,
                )

            self._apply_updates(question, data)

            await self._uow.commit()

            return self._to_question_data(question)

    async def delete_question(self, question_id: UUID) -> None:
        """Delete a question or raise if it does not exist."""

        async with self._uow:
            question = await self._get_question_or_raise(question_id)

            await self._uow.questions.delete(question)

            await self._uow.commit()

    async def get_random_question(
        self,
        criteria: RandomQuestionCriteria,
    ) -> QuestionData:
        async with self._uow as uow:
            if criteria.topic_id is not None:
                topic = await uow.topics.get_by_id(criteria.topic_id)

                if topic is None:
                    raise TopicNotFoundError(criteria.topic_id)

            question = await uow.questions.get_random(criteria)

            if question is None:
                raise RandomQuestionNotFoundError()

            return QuestionData(
                id=question.id,
                topic_id=question.topic_id,
                question=question.question,
                answer=question.answer,
                difficulty=question.difficulty,
                created_at=question.created_at,
                updated_at=question.updated_at,
            )

    async def _ensure_question_is_unique(
        self, topic_id: UUID, question_text: str, exclude_id: UUID | None = None
    ) -> None:
        existing = await self._uow.questions.get_by_text(
            topic_id, question_text, exclude_id=exclude_id
        )
        if existing is not None:
            raise QuestionAlreadyExistsError(topic_id, question_text)

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
    def _apply_updates(
        question: Question,
        data: UpdateQuestionData,
    ) -> None:
        topic_id = data.topic_id
        if is_set(topic_id):
            question.topic_id = topic_id

        question_text = data.question
        if is_set(question_text):
            question.question = question_text

        answer = data.answer
        if is_set(answer):
            question.answer = answer

        difficulty = data.difficulty
        if is_set(difficulty):
            question.difficulty = difficulty

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
