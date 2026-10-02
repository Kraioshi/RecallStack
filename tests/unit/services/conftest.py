from typing import Protocol

import pytest

from app.models.topic import Topic
from app.services.topic import TopicService
from tests.unit.test_doubles.repositories import FakeTopicRepository
from tests.unit.test_doubles.unit_of_work import FakeUnitOfWork


class TopicServiceFactory(Protocol):
    def __call__(
        self,
        topics: list[Topic] | None = None,
    ) -> tuple[TopicService, FakeUnitOfWork]: ...


@pytest.fixture
def topic_service_factory() -> TopicServiceFactory:
    """Build a TopicService with an in-memory repository and fake UoW."""

    def create_service(
        topics: list[Topic] | None = None,
    ) -> tuple[TopicService, FakeUnitOfWork]:
        repository = FakeTopicRepository(topics)
        uow = FakeUnitOfWork(repository)
        service = TopicService(uow)

        return service, uow

    return create_service
