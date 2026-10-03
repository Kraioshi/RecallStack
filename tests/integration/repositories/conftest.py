import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.repositories.question import SQLAlchemyQuestionRepository
from app.infrastructure.repositories.topic import SQLAlchemyTopicRepository
from tests.integration.repositories.factories import QuestionFactory, TopicFactory


@pytest.fixture
def topic_factory(
    db_session: AsyncSession,
) -> TopicFactory:
    """Provide a TopicFactory bound to the current integration test session."""

    return TopicFactory(db_session)


@pytest.fixture
def topic_repository(db_session: AsyncSession) -> SQLAlchemyTopicRepository:
    """Provide a topic repository bound to the current integration test session."""

    return SQLAlchemyTopicRepository(db_session)


@pytest.fixture
def question_factory(
    db_session: AsyncSession,
) -> QuestionFactory:

    return QuestionFactory(db_session)


@pytest.fixture
def question_repository(db_session: AsyncSession) -> SQLAlchemyQuestionRepository:
    """Provide a question repository bound to the current integration test session."""

    return SQLAlchemyQuestionRepository(db_session)
