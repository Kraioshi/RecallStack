from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums.question import QuestionDifficulty
from app.infrastructure.repositories.question import SQLAlchemyQuestionRepository
from app.models import Question
from tests.integration.repositories.factories import QuestionFactory, TopicFactory


class TestGetById:
    async def test_returns_existing_question(
        self,
        topic_factory: TopicFactory,
        question_factory: QuestionFactory,
        question_repository: SQLAlchemyQuestionRepository,
    ) -> None:
        topic = await topic_factory(
            name="Python",
            slug="python",
        )

        question = await question_factory(
            topic=topic,
            question="What is the GIL?",
            answer="Global Interpreter Lock.",
            difficulty=QuestionDifficulty.MEDIUM,
        )

        result = await question_repository.get_by_id(question.id)

        assert result is not None
        assert result.id == question.id
        assert result.topic_id == topic.id
        assert result.question == "What is the GIL?"
        assert result.answer == "Global Interpreter Lock."
        assert result.difficulty == "medium"

    async def test_returns_none_when_question_does_not_exist(
        self,
        question_repository: SQLAlchemyQuestionRepository,
    ) -> None:
        result = await question_repository.get_by_id(uuid4())

        assert result is None


class TestGetByTopicId:
    async def test_returns_only_questions_from_requested_topic(
        self,
        topic_factory: TopicFactory,
        question_factory: QuestionFactory,
        question_repository: SQLAlchemyQuestionRepository,
    ) -> None:
        python_topic = await topic_factory(
            name="Python",
            slug="python",
        )
        sql_topic = await topic_factory(
            name="SQL",
            slug="sql",
        )

        gil_question = await question_factory(
            topic=python_topic,
            question="What is the GIL?",
            answer="Global Interpreter Lock.",
            difficulty=QuestionDifficulty.MEDIUM,
        )

        async_question = await question_factory(
            topic=python_topic,
            question="What is asyncio?",
            answer="Python's asynchronous I/O framework.",
            difficulty=QuestionDifficulty.MEDIUM,
        )

        await question_factory(
            topic=sql_topic,
            question="What is a JOIN?",
            answer="A way to combine rows from multiple tables.",
            difficulty=QuestionDifficulty.MEDIUM,
        )

        result = await question_repository.get_by_topic_id(python_topic.id)

        result_ids = {question.id for question in result}

        assert result_ids == {
            gil_question.id,
            async_question.id,
        }

    async def test_returns_empty_list_when_topic_has_no_questions(
        self,
        topic_factory: TopicFactory,
        question_repository: SQLAlchemyQuestionRepository,
    ) -> None:
        topic = await topic_factory(
            name="Python",
            slug="python",
        )

        result = await question_repository.get_by_topic_id(topic.id)

        assert result == []


class TestAdd:
    async def test_persists_question(
        self,
        db_session: AsyncSession,
        topic_factory: TopicFactory,
        question_repository: SQLAlchemyQuestionRepository,
    ) -> None:
        topic = await topic_factory(
            name="Python",
            slug="python",
        )

        question = Question(
            topic_id=topic.id,
            question="What is the GIL?",
            answer="Global Interpreter Lock.",
            difficulty="medium",
        )

        result = await question_repository.add(question)

        assert result.id is not None
        question_id = result.id

        db_session.expunge(result)

        persisted_question = await question_repository.get_by_id(question_id)

        assert persisted_question is not None
        assert persisted_question.id == question_id
        assert persisted_question.topic_id == topic.id
        assert persisted_question.question == "What is the GIL?"
        assert persisted_question.answer == "Global Interpreter Lock."


class TestDelete:
    async def test_deletes_question(
        self,
        db_session: AsyncSession,
        topic_factory: TopicFactory,
        question_factory: QuestionFactory,
        question_repository: SQLAlchemyQuestionRepository,
    ) -> None:
        topic = await topic_factory(
            name="Python",
            slug="python",
        )

        question = await question_factory(
            topic=topic,
            question="What is the GIL?",
            answer="Global Interpreter Lock.",
            difficulty=QuestionDifficulty.MEDIUM,
        )

        question_id = question.id

        await question_repository.delete(question)
        await db_session.flush()

        result = await question_repository.get_by_id(question_id)

        assert result is None
