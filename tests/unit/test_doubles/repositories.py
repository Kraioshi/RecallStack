from uuid import UUID, uuid4

from app.core.helpers.dates import now
from app.models.topic import Topic


class FakeTopicRepository:
    """
    In-memory TopicRepository implementation for service unit tests.
    """

    def __init__(self, topics: list[Topic] | None = None) -> None:
        self._topics = list(topics or [])

    async def get_by_id(self, topic_id: UUID) -> Topic | None:
        return next(
            (topic for topic in self._topics if topic.id == topic_id),
            None,
        )

    async def get_roots(self) -> list[Topic]:
        return [topic for topic in self._topics if topic.parent_id is None]

    async def get_children(self, parent_id: UUID) -> list[Topic]:
        return [topic for topic in self._topics if topic.parent_id == parent_id]

    async def get_by_slug(
        self,
        slug: str,
        parent_id: UUID | None,
    ) -> Topic | None:
        return next(
            (
                topic
                for topic in self._topics
                if topic.slug == slug and topic.parent_id == parent_id
            ),
            None,
        )

    async def add(self, topic: Topic) -> Topic:
        # PostgreSQL normally populates database-generated fields during flush().
        # The fake has no database, so it simulates the values the service relies on.
        timestamp = now()
        if topic.id is None:
            topic.id = uuid4()

        if topic.created_at is None:
            topic.created_at = timestamp

        if topic.updated_at is None:
            topic.updated_at = timestamp

        self._topics.append(topic)

        return topic
