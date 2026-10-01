from uuid import uuid4

import pytest

from app.core.dto.topic import TopicData
from app.core.exceptions.topic import TopicNotFoundError
from app.core.helpers.dates import now
from app.models.topic import Topic
from app.services.topic import TopicService
from tests.unit.test_doubles.repositories import FakeTopicRepository
from tests.unit.test_doubles.unit_of_work import FakeUnitOfWork


class TestGetTopic:
    async def test_returns_existing_topic(self) -> None:
        topic_id = uuid4()
        current_time = now()

        topic = Topic(
            id=topic_id,
            name="Python",
            slug="python",
            description="Python topic",
            created_at=current_time,
            updated_at=current_time,
        )

        repository = FakeTopicRepository([topic])
        uow = FakeUnitOfWork(repository)
        service = TopicService(uow)

        result = await service.get_topic(topic_id)

        assert isinstance(result, TopicData)
        assert result is not topic

        assert result.id == topic.id
        assert result.name == topic.name
        assert result.slug == topic.slug
        assert result.parent_id == topic.parent_id
        assert result.description == topic.description
        assert result.created_at == topic.created_at
        assert result.updated_at == topic.updated_at

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
