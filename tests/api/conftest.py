from collections.abc import AsyncIterator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.api.dependencies.services import get_question_service
from app.main import app
from app.models.question import Question
from app.models.topic import Topic
from app.services.question import QuestionService
from tests.api.types import QuestionServiceOverride
from tests.unit.test_doubles.repositories import (
    FakeQuestionRepository,
    FakeTopicRepository,
)
from tests.unit.test_doubles.unit_of_work import FakeUnitOfWork


@pytest_asyncio.fixture
async def api_client() -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def question_service_override() -> QuestionServiceOverride:
    def override(
        topics: list[Topic] | None = None,
        questions: list[Question] | None = None,
    ) -> tuple[QuestionService, FakeUnitOfWork]:
        topic_repository = FakeTopicRepository(topics)
        question_repository = FakeQuestionRepository(questions)

        uow = FakeUnitOfWork(
            topics=topic_repository,
            questions=question_repository,
        )

        service = QuestionService(uow)

        app.dependency_overrides[get_question_service] = lambda: service

        return service, uow

    return override
