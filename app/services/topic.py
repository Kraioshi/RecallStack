from uuid import UUID

from app.core.exceptions.topic import TopicNotFoundError
from app.models.topic import Topic
from app.unit_of_work.base import UnitOfWork


class TopicService:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def get_topic(self, topic_id: UUID) -> Topic:
        """Return a topic or raise if it does not exist."""

        async with self._uow:
            topic = await self._uow.topics.get_by_id(topic_id)

            if topic is None:
                raise TopicNotFoundError(topic_id)

            return topic
