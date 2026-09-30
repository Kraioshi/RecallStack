from uuid import uuid4

import pytest

from app.core.exceptions.topic import TopicNotFoundError
from app.models.topic import Topic
from app.services.topic import TopicService
from tests.unit.test_doubles.repositories import FakeTopicRepository
from tests.unit.test_doubles.unit_of_work import FakeUnitOfWork


class TestGetTopic:
    async def test_returns_existing_topic(self) -> None:
        topic_id = uuid4()

        topic = Topic(
            id=topic_id,
            name="Python",
            slug="python",
        )

        repository = FakeTopicRepository([topic])
        uow = FakeUnitOfWork(repository)
        service = TopicService(uow)

        result = await service.get_topic(topic_id)

        assert result is topic
        assert uow.entered is True
        assert uow.exited is True

    async def test_raises_when_topic_does_not_exist(self) -> None:
        topic_id = uuid4()

        repository = FakeTopicRepository()
        uow = FakeUnitOfWork(repository)
        service = TopicService(uow)

        with pytest.raises(TopicNotFoundError) as exc_info:
            await service.get_topic(topic_id)

        assert exc_info.value.topic_id == topic_id
        assert uow.entered is True
        assert uow.exited is True
