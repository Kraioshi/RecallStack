from uuid import uuid4

import pytest

from app.core.dto.topic import TopicData
from app.core.exceptions.topic import TopicNotFoundError
from app.core.helpers.dates import now
from app.models.topic import Topic
from tests.unit.factories import make_topic
from tests.unit.services.conftest import TopicServiceFactory


class TestGetTopic:
    async def test_returns_existing_topic(
        self,
        topic_service_factory: TopicServiceFactory,
    ) -> None:
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

        service, uow = topic_service_factory([topic])

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

    async def test_raises_when_topic_does_not_exist(
        self,
        topic_service_factory: TopicServiceFactory,
    ) -> None:
        topic_id = uuid4()

        service, uow = topic_service_factory()

        with pytest.raises(TopicNotFoundError) as exc_info:
            await service.get_topic(topic_id)

        assert exc_info.value.topic_id == topic_id
        assert uow.entered is True
        assert uow.exited is True


class TestListRootTopics:
    async def test_returns_only_root_topics(
        self,
        topic_service_factory: TopicServiceFactory,
    ) -> None:
        python = make_topic(
            name="Python",
            slug="python",
        )
        sql = make_topic(
            name="SQL",
            slug="sql",
        )
        asyncio_topic = make_topic(
            name="Asyncio",
            slug="asyncio",
            parent_id=python.id,
        )

        service, _ = topic_service_factory([python, sql, asyncio_topic])

        result = await service.list_root_topics()

        assert all(isinstance(topic, TopicData) for topic in result)

        result_ids = {topic.id for topic in result}

        assert result_ids == {
            python.id,
            sql.id,
        }

    async def test_returns_empty_list_when_no_topics_exist(
        self,
        topic_service_factory: TopicServiceFactory,
    ) -> None:
        service, _ = topic_service_factory()

        result = await service.list_root_topics()

        assert result == []
