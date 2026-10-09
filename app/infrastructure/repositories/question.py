from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.core.dto.question import RandomQuestionCriteria
from app.core.enums.question import QuestionDifficulty
from app.models import Topic
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

    async def get_by_text(
        self, topic_id: UUID, question: str, exclude_id: UUID | None = None
    ) -> Question | None:
        """
        Comparison is case-insensitive and ignores leading/trailing spaces.
        Optionally exclude a question by ID (useful when updating questions).

        SELECT * FROM questions
        WHERE topic_id = :topic_id
            AND lower(btrim(question)) = lower(btrim(:question))
        LIMIT 1;
        """
        normalized_column = func.lower(func.btrim(Question.question))
        normalized_value = func.lower(func.btrim(question))

        stmt = select(Question).where(
            Question.topic_id == topic_id,
            normalized_column.bool_op("=")(normalized_value),
        )
        if exclude_id is not None:
            stmt = stmt.where(Question.id != exclude_id)

        result = await self._session.execute(stmt.limit(1))
        return result.scalar_one_or_none()

    async def add(self, question: Question) -> Question:
        self._session.add(question)
        await self._session.flush()

        return question

    async def delete(self, question: Question) -> None:
        await self._session.delete(question)

    async def count_by_topic(self) -> dict[UUID, int]:
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

    async def count_by_topic_and_difficulty(
        self,
    ) -> dict[UUID, dict[QuestionDifficulty, int]]:
        """
        Return question counts grouped by topic and difficulty.

        Topics without questions are not included in the result.
        Difficulties with zero questions are not included as well.

        SELECT
            questions.topic_id,
            questions.difficulty,
            COUNT(questions.id)
        FROM questions
        GROUP BY
            questions.topic_id,
            questions.difficulty;
        """
        stmt = select(
            Question.topic_id,
            Question.difficulty,
            func.count(Question.id),
        ).group_by(
            Question.topic_id,
            Question.difficulty,
        )
        result = await self._session.execute(stmt)

        counts: dict[UUID, dict[QuestionDifficulty, int]] = {}

        for topic_id, difficulty, count in result.all():
            counts.setdefault(topic_id, {})[difficulty] = count

        return counts

    async def get_random(self, criteria: RandomQuestionCriteria) -> Question | None:
        stmt = select(Question)

        if criteria.exclude_id is not None:
            stmt = stmt.where(Question.id != criteria.exclude_id)

        if criteria.difficulty is not None:
            stmt = stmt.where(Question.difficulty == criteria.difficulty)

        if criteria.topic_id is not None:
            if criteria.include_descendants:
                # WITH RECURSIVE topic_tree AS (
                #     SELECT id
                #     FROM topics
                #     WHERE id = :topic_id
                #
                #     UNION ALL
                #
                #     SELECT child.id
                #     FROM topics AS child
                #     JOIN topic_tree
                #         ON child.parent_id = topic_tree.topic_id
                # )
                #
                # Later used as:
                # WHERE questions.topic_id IN (SELECT topic_id FROM topic_tree)
                topic_tree = (
                    select(Topic.id.label("topic_id"))
                    .where(Topic.id == criteria.topic_id)
                    .cte("topic_tree", recursive=True)
                )

                child_topic = aliased(Topic)

                topic_tree = topic_tree.union_all(
                    select(child_topic.id).where(
                        child_topic.parent_id == topic_tree.c.topic_id,
                    )
                )

                stmt = stmt.where(
                    Question.topic_id.in_(
                        select(topic_tree.c.topic_id),
                    )
                )
            else:
                stmt = stmt.where(Question.topic_id == criteria.topic_id)

        stmt = stmt.order_by(func.random()).limit(1)

        result = await self._session.execute(stmt)

        return result.scalar_one_or_none()
