from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.question import Question


class SQLAlchemyQuestionRepository:
    """
    SQLAlchemy implementation of QuestionRepository.

    Keeps SQLAlchemy-specific database logic out of the service layer.
    The repository can flush changes, but does NOT commit them.
    The caller is responsible for the transaction boundary.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, question_id: UUID) -> Question | None:
        stmt = select(Question).where(Question.id == question_id)
        result = await self._session.execute(stmt)

        return result.scalar_one_or_none()

    async def get_by_topic_id(self, topic_id: UUID) -> list[Question]:
        stmt = select(Question).where(Question.topic_id == topic_id)
        result = await self._session.execute(stmt)

        return list(result.scalars().all())

    async def add(self, question: Question) -> Question:
        self._session.add(question)
        await self._session.flush()

        return question

    async def delete(self, question: Question) -> None:
        await self._session.delete(question)

    async def count_by_topic(self):
        """
        SELECT
            questions.topic_id,
            COUNT(questions.id)
        FROM questions
        GROUP BY questions.topic_id;
        """
        stmt = select(Question.topic_id, func.count(Question.id)).group_by(
            Question.topic_id
        )

        result = await self._session.execute(stmt)

        return {topic_id: count for topic_id, count in result.all()}
