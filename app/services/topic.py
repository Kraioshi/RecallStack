from uuid import UUID

from app.core.dto.topic import TopicData
from app.core.exceptions.topic import TopicNotFoundError
from app.models.topic import Topic
from app.unit_of_work.base import UnitOfWork


class TopicService:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def get_topic(self, topic_id: UUID) -> TopicData:
        """Return a topic or raise if it does not exist."""

        async with self._uow:
            topic = await self._uow.topics.get_by_id(topic_id)

            if topic is None:
                raise TopicNotFoundError(topic_id)

            return self._to_topic_data(topic)

    async def list_root_topics(self) -> list[TopicData]:
        """Return all root-level topics."""

        async with self._uow:
            roots = await self._uow.topics.get_roots()
            return [self._to_topic_data(root) for root in roots]

    @staticmethod
    def _to_topic_data(topic: Topic) -> TopicData:
        return TopicData(
            id=topic.id,
            parent_id=topic.parent_id,
            name=topic.name,
            slug=topic.slug,
            description=topic.description,
            created_at=topic.created_at,
            updated_at=topic.updated_at,
        )
