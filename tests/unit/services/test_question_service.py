from uuid import uuid4

import pytest

from app.core.dto.question import CreateQuestionData, QuestionData
from app.core.enums.question import QuestionDifficulty
from app.core.exceptions.question import QuestionNotFoundError
from app.core.exceptions.topic import TopicNotFoundError
from app.core.helpers.dates import now
from app.models import Question
from tests.unit.factories import make_question, make_topic
from tests.unit.services.conftest import QuestionServiceFactory


class TestGetQuestion:
    async def test_returns_existing_question(
        self,
        question_service_factory: QuestionServiceFactory,
    ) -> None:
        # Arrange
        topic_id = uuid4()
        current_time = now()

        question = Question(
            question="What is the GIL?",
            answer="Global Interpreter Lock.",
            difficulty=QuestionDifficulty.MEDIUM,
            topic_id=topic_id,
            created_at=current_time,
        )

        # Act
        service, uow = question_service_factory(questions=[question])
        result = await service.get_question(question.id)

        # Assert
        assert isinstance(result, QuestionData)
        assert result is not question
        assert result.id == question.id
        assert result.question == question.question
        assert result.answer == question.answer
        assert result.difficulty == QuestionDifficulty.MEDIUM
        assert result.topic_id == topic_id
        assert result.topic_id == question.topic_id

        assert uow.entered is True
        assert uow.exited is True

    async def test_raises_when_question_does_not_exist(
        self,
        question_service_factory: QuestionServiceFactory,
    ) -> None:
        # Arrange
        question_id = uuid4()
        service, uow = question_service_factory()

        # Act / Assert
        with pytest.raises(QuestionNotFoundError) as exc_info:
            await service.get_question(question_id)

        assert exc_info.value.question_id == question_id
        assert uow.entered is True
        assert uow.exited is True
        assert uow.rolled_back is True


class TestListQuestionsByTopic:
    async def test_returns_questions_belonging_to_topic(
        self,
        question_service_factory: QuestionServiceFactory,
    ) -> None:
        # Arrange
        python = make_topic(
            name="Python",
            slug="python",
        )
        sql = make_topic(
            name="SQL",
            slug="sql",
        )

        py_question_one = make_question(topic_id=python.id)
        py_question_two = make_question(topic_id=python.id)
        sql_question = make_question(topic_id=sql.id)

        service, _ = question_service_factory(
            topics=[python, sql],
            questions=[
                py_question_one,
                py_question_two,
                sql_question,
            ],
        )

        # Act
        python_result = await service.list_questions_by_topic(python.id)
        sql_result = await service.list_questions_by_topic(sql.id)

        # Assert
        python_question_ids = {question.id for question in python_result}
        sql_question_ids = {question.id for question in sql_result}

        assert python_question_ids == {
            py_question_one.id,
            py_question_two.id,
        }

        assert sql_question_ids == {
            sql_question.id,
        }

    async def test_returns_empty_list_when_topic_has_no_questions(
        self,
        question_service_factory: QuestionServiceFactory,
    ) -> None:
        # Arrange
        topic = make_topic()

        service, _ = question_service_factory(topics=[topic])

        # Act
        result = await service.list_questions_by_topic(topic.id)

        # Assert
        assert result == []

    async def test_raises_when_topic_does_not_exist(
        self,
        question_service_factory: QuestionServiceFactory,
    ) -> None:
        # Arrange
        topic = make_topic()
        service, _ = question_service_factory()

        # Act / Assert
        with pytest.raises(TopicNotFoundError) as exc_info:
            await service.list_questions_by_topic(topic.id)

        assert exc_info.value.topic_id == topic.id


class TestCreateQuestion:
    async def test_creates_question(
        self,
        question_service_factory: QuestionServiceFactory,
    ) -> None:
        # Arrange
        topic = make_topic()
        service, _ = question_service_factory(
            topics=[topic],
        )

        question = CreateQuestionData(
            topic_id=topic.id,
            question="What is the GIL?",
            answer="Global Interpreter Lock.",
            difficulty=QuestionDifficulty.MEDIUM,
        )
        # Act
        result = await service.create_question(question)

        # Assert
        assert isinstance(result, QuestionData)

        assert result.id is not None
        assert result.topic_id == topic.id
        assert result.question == question.question
        assert result.answer == question.answer
        assert result.difficulty == question.difficulty

    async def test_commits_unit_of_work(
        self,
        question_service_factory: QuestionServiceFactory,
    ) -> None:
        # Arrange
        topic = make_topic()

        service, uow = question_service_factory(
            topics=[topic],
        )

        question_data = CreateQuestionData(
            topic_id=topic.id,
            question="What is Love?",
            answer="Baby don't hurt me.",
            difficulty=QuestionDifficulty.MEDIUM,
        )

        # Act
        await service.create_question(question_data)

        # Assert
        assert uow.committed is True

    async def test_raises_when_topic_does_not_exist(
        self,
        question_service_factory: QuestionServiceFactory,
    ) -> None:
        # Arrange
        topic_id = uuid4()

        service, _ = question_service_factory()

        question_data = CreateQuestionData(
            topic_id=topic_id,
            question="Do androids dream of electric sheep?",
            answer="Yes.",
            difficulty=QuestionDifficulty.MEDIUM,
        )

        # Act / Assert
        with pytest.raises(TopicNotFoundError) as exc_info:
            await service.create_question(question_data)

        assert exc_info.value.topic_id == topic_id

    async def test_does_not_commit_when_topic_does_not_exist(
        self,
        question_service_factory: QuestionServiceFactory,
    ) -> None:
        # Arrange
        topic_id = uuid4()

        service, uow = question_service_factory()

        question_data = CreateQuestionData(
            topic_id=topic_id,
            question=(
                "Can you hear the silence? "
                "Can you see the dark? "
                "Can you fix the broken?"
            ),
            answer="Can you feel my heart?",
            difficulty=QuestionDifficulty.MEDIUM,
        )

        # Act
        with pytest.raises(TopicNotFoundError):
            await service.create_question(question_data)

        # Assert
        assert uow.committed is False
        assert uow.rolled_back is True
