from uuid import uuid4

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dto.question import RandomQuestionCriteria
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


class TestCountByTopic:
    async def test_returns_question_counts_grouped_by_topic(
        self,
        question_repository: SQLAlchemyQuestionRepository,
        topic_factory: TopicFactory,
        question_factory: QuestionFactory,
    ) -> None:
        python = await topic_factory(
            name="Python",
            slug="python",
        )
        sql = await topic_factory(
            name="SQL",
            slug="sql",
        )

        await question_factory(
            topic=python,
            question="What is a decorator?",
            answer="...",
            difficulty=QuestionDifficulty.MEDIUM,
        )
        await question_factory(
            topic=python,
            question="What is a generator?",
            answer="...",
            difficulty=QuestionDifficulty.MEDIUM,
        )
        await question_factory(
            topic=sql,
            question="What is an index?",
            answer="...",
            difficulty=QuestionDifficulty.MEDIUM,
        )

        result = await question_repository.count_by_topic()

        assert result == {
            python.id: 2,
            sql.id: 1,
        }

    async def test_returns_empty_mapping_when_no_questions_exist(
        self,
        question_repository: SQLAlchemyQuestionRepository,
    ) -> None:
        result = await question_repository.count_by_topic()

        assert result == {}


class TestGetRandom:
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

        first_question = await question_factory(
            topic=topic,
            question="What is the GIL?",
            answer="Global Interpreter Lock.",
            difficulty=QuestionDifficulty.MEDIUM,
        )

        second_question = await question_factory(
            topic=topic,
            question="What is a decorator?",
            answer="A callable that modifies another callable.",
            difficulty=QuestionDifficulty.EASY,
        )

        result = await question_repository.get_random(RandomQuestionCriteria())

        assert result is not None
        assert result.id in {
            first_question.id,
            second_question.id,
        }

    async def test_returns_none_when_no_questions_exist(
        self,
        question_repository: SQLAlchemyQuestionRepository,
    ) -> None:
        result = await question_repository.get_random(RandomQuestionCriteria())

        assert result is None

    async def test_excludes_requested_question(
        self,
        topic_factory: TopicFactory,
        question_factory: QuestionFactory,
        question_repository: SQLAlchemyQuestionRepository,
    ) -> None:
        topic = await topic_factory(
            name="Python",
            slug="python",
        )

        excluded_question = await question_factory(
            topic=topic,
            question="What is the GIL?",
            answer="Global Interpreter Lock.",
            difficulty=QuestionDifficulty.MEDIUM,
        )

        expected_question = await question_factory(
            topic=topic,
            question="What is a decorator?",
            answer="...",
            difficulty=QuestionDifficulty.EASY,
        )

        result = await question_repository.get_random(
            RandomQuestionCriteria(
                exclude_id=excluded_question.id,
            )
        )

        assert result is not None
        assert result.id == expected_question.id

    async def test_returns_none_when_only_question_is_excluded(
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

        result = await question_repository.get_random(
            RandomQuestionCriteria(
                exclude_id=question.id,
            )
        )

        assert result is None

    async def test_returns_question_with_requested_difficulty(
        self,
        topic_factory: TopicFactory,
        question_factory: QuestionFactory,
        question_repository: SQLAlchemyQuestionRepository,
    ) -> None:
        topic = await topic_factory(
            name="Python",
            slug="python",
        )

        hard_question = await question_factory(
            topic=topic,
            question="Explain Python's descriptor protocol.",
            answer="...",
            difficulty=QuestionDifficulty.HARD,
        )

        await question_factory(
            topic=topic,
            question="What is a list?",
            answer="...",
            difficulty=QuestionDifficulty.EASY,
        )

        result = await question_repository.get_random(
            RandomQuestionCriteria(
                difficulty=QuestionDifficulty.HARD,
            )
        )

        assert result is not None
        assert result.id == hard_question.id
        assert result.difficulty == QuestionDifficulty.HARD

    async def test_returns_none_when_no_question_matches_difficulty(
        self,
        topic_factory: TopicFactory,
        question_factory: QuestionFactory,
        question_repository: SQLAlchemyQuestionRepository,
    ) -> None:
        topic = await topic_factory(
            name="Python",
            slug="python",
        )

        await question_factory(
            topic=topic,
            question="What is a list?",
            answer="...",
            difficulty=QuestionDifficulty.EASY,
        )

        result = await question_repository.get_random(
            RandomQuestionCriteria(
                difficulty=QuestionDifficulty.HARD,
            )
        )

        assert result is None

    async def test_combines_difficulty_and_exclusion(
        self,
        topic_factory: TopicFactory,
        question_factory: QuestionFactory,
        question_repository: SQLAlchemyQuestionRepository,
    ) -> None:
        topic = await topic_factory(
            name="Python",
            slug="python",
        )

        excluded = await question_factory(
            topic=topic,
            question="Hard question one",
            answer="...",
            difficulty=QuestionDifficulty.HARD,
        )

        expected = await question_factory(
            topic=topic,
            question="Hard question two",
            answer="...",
            difficulty=QuestionDifficulty.HARD,
        )

        await question_factory(
            topic=topic,
            question="Easy question",
            answer="...",
            difficulty=QuestionDifficulty.EASY,
        )

        result = await question_repository.get_random(
            RandomQuestionCriteria(
                exclude_id=excluded.id,
                difficulty=QuestionDifficulty.HARD,
            )
        )

        assert result is not None
        assert result.id == expected.id

    async def test_returns_question_from_requested_topic(
        self,
        topic_factory: TopicFactory,
        question_factory: QuestionFactory,
        question_repository: SQLAlchemyQuestionRepository,
    ) -> None:
        python = await topic_factory(
            name="Python",
            slug="python",
        )
        sql = await topic_factory(
            name="SQL",
            slug="sql",
        )

        expected = await question_factory(
            topic=python,
            question="What is the GIL?",
            answer="Global Interpreter Lock.",
            difficulty=QuestionDifficulty.MEDIUM,
        )

        await question_factory(
            topic=sql,
            question="What is a JOIN?",
            answer="...",
            difficulty=QuestionDifficulty.MEDIUM,
        )

        result = await question_repository.get_random(
            RandomQuestionCriteria(
                topic_id=python.id,
            )
        )

        assert result is not None
        assert result.id == expected.id

    async def test_returns_none_when_topic_has_no_questions(
        self,
        topic_factory: TopicFactory,
        question_repository: SQLAlchemyQuestionRepository,
    ) -> None:
        topic = await topic_factory(
            name="Python",
            slug="python",
        )

        result = await question_repository.get_random(
            RandomQuestionCriteria(
                topic_id=topic.id,
            )
        )

        assert result is None

    async def test_combines_topic_and_difficulty(
        self,
        topic_factory: TopicFactory,
        question_factory: QuestionFactory,
        question_repository: SQLAlchemyQuestionRepository,
    ) -> None:
        python = await topic_factory(
            name="Python",
            slug="python",
        )
        sql = await topic_factory(
            name="SQL",
            slug="sql",
        )

        expected = await question_factory(
            topic=python,
            question="Explain descriptors.",
            answer="...",
            difficulty=QuestionDifficulty.HARD,
        )

        await question_factory(
            topic=python,
            question="What is a list?",
            answer="...",
            difficulty=QuestionDifficulty.EASY,
        )

        await question_factory(
            topic=sql,
            question="Explain query planning.",
            answer="...",
            difficulty=QuestionDifficulty.HARD,
        )

        result = await question_repository.get_random(
            RandomQuestionCriteria(
                topic_id=python.id,
                difficulty=QuestionDifficulty.HARD,
            )
        )

        assert result is not None
        assert result.id == expected.id

    async def test_does_not_include_descendants_by_default(
        self,
        topic_factory: TopicFactory,
        question_factory: QuestionFactory,
        question_repository: SQLAlchemyQuestionRepository,
    ) -> None:
        python = await topic_factory(
            name="Python",
            slug="python",
        )

        fastapi = await topic_factory(
            name="FastAPI",
            slug="fastapi",
            parent=python,
        )

        await question_factory(
            topic=fastapi,
            question="What is dependency injection?",
            answer="...",
            difficulty=QuestionDifficulty.MEDIUM,
        )

        result = await question_repository.get_random(
            RandomQuestionCriteria(
                topic_id=python.id,
            )
        )

        assert result is None

    async def test_includes_all_descendants_when_requested(
        self,
        topic_factory: TopicFactory,
        question_factory: QuestionFactory,
        question_repository: SQLAlchemyQuestionRepository,
    ) -> None:
        python = await topic_factory(
            name="Python",
            slug="python",
        )

        frameworks = await topic_factory(
            name="Frameworks",
            slug="frameworks",
            parent=python,
        )

        fastapi = await topic_factory(
            name="FastAPI",
            slug="fastapi",
            parent=frameworks,
        )

        expected = await question_factory(
            topic=fastapi,
            question="What is dependency injection?",
            answer="...",
            difficulty=QuestionDifficulty.MEDIUM,
        )

        sql = await topic_factory(
            name="SQL",
            slug="sql",
        )

        await question_factory(
            topic=sql,
            question="What is a JOIN?",
            answer="...",
            difficulty=QuestionDifficulty.MEDIUM,
        )

        result = await question_repository.get_random(
            RandomQuestionCriteria(
                topic_id=python.id,
                include_descendants=True,
            )
        )

        assert result is not None
        assert result.id == expected.id

    async def test_combines_descendants_and_difficulty(
        self,
        topic_factory: TopicFactory,
        question_factory: QuestionFactory,
        question_repository: SQLAlchemyQuestionRepository,
    ) -> None:
        python = await topic_factory(
            name="Python",
            slug="python",
        )
        frameworks = await topic_factory(
            name="Frameworks",
            slug="frameworks",
            parent=python,
        )
        fastapi = await topic_factory(
            name="FastAPI",
            slug="fastapi",
            parent=frameworks,
        )

        expected = await question_factory(
            topic=fastapi,
            question="Explain FastAPI dependency injection.",
            answer="...",
            difficulty=QuestionDifficulty.HARD,
        )

        await question_factory(
            topic=fastapi,
            question="What is a path parameter?",
            answer="...",
            difficulty=QuestionDifficulty.EASY,
        )

        sql = await topic_factory(
            name="SQL",
            slug="sql",
        )

        await question_factory(
            topic=sql,
            question="Explain query planning.",
            answer="...",
            difficulty=QuestionDifficulty.HARD,
        )

        result = await question_repository.get_random(
            RandomQuestionCriteria(
                topic_id=python.id,
                include_descendants=True,
                difficulty=QuestionDifficulty.HARD,
            )
        )

        assert result is not None
        assert result.id == expected.id


class TestGetByText:
    async def test_returns_question_with_normalized_text(
        self,
        topic_factory: TopicFactory,
        question_factory: QuestionFactory,
        question_repository: SQLAlchemyQuestionRepository,
    ) -> None:
        # Arrange
        topic = await topic_factory(
            name="Python",
            slug="python",
        )

        existing = await question_factory(
            topic=topic,
            question="What is the GIL?",
            answer="Global Interpreter Lock.",
            difficulty=QuestionDifficulty.MEDIUM,
        )

        # Act
        result = await question_repository.get_by_text(
            topic_id=topic.id,
            question="  WHAT IS THE GIL?  ",
        )

        # Assert
        assert result is not None
        assert result.id == existing.id

    async def test_returns_none_when_question_is_in_different_topic(
        self,
        topic_factory: TopicFactory,
        question_factory: QuestionFactory,
        question_repository: SQLAlchemyQuestionRepository,
    ) -> None:
        # Arrange
        python = await topic_factory(
            name="Python",
            slug="python",
        )
        sql = await topic_factory(
            name="SQL",
            slug="sql",
        )

        await question_factory(
            topic=python,
            question="What is concurrency?",
            answer="...",
            difficulty=QuestionDifficulty.MEDIUM,
        )

        # Act
        result = await question_repository.get_by_text(
            topic_id=sql.id,
            question="What is concurrency?",
        )

        # Assert
        assert result is None

    async def test_excludes_question_by_id(
        self,
        topic_factory: TopicFactory,
        question_factory: QuestionFactory,
        question_repository: SQLAlchemyQuestionRepository,
    ) -> None:
        # Arrange
        topic = await topic_factory(
            name="Python",
            slug="python",
        )

        existing = await question_factory(
            topic=topic,
            question="What is the GIL?",
            answer="...",
            difficulty=QuestionDifficulty.MEDIUM,
        )

        # Act
        result = await question_repository.get_by_text(
            topic_id=topic.id,
            question="What is the GIL?",
            exclude_id=existing.id,
        )

        # Assert
        assert result is None


class TestQuestionUniquenessConstraint:
    async def test_database_rejects_duplicate_question(
        self,
        topic_factory: TopicFactory,
        question_factory: QuestionFactory,
        question_repository: SQLAlchemyQuestionRepository,
    ) -> None:
        # Arrange
        topic = await topic_factory(
            name="Python",
            slug="python",
        )

        await question_factory(
            topic=topic,
            question="What is the GIL?",
            answer="Global Interpreter Lock.",
            difficulty=QuestionDifficulty.MEDIUM,
        )

        duplicate = Question(
            topic_id=topic.id,
            question="  WHAT IS THE GIL?  ",
            answer="Another explanation.",
            difficulty=QuestionDifficulty.HARD,
        )

        # Act / Assert
        with pytest.raises(IntegrityError):
            await question_repository.add(duplicate)
