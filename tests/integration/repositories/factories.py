from sqlalchemy.ext.asyncio import AsyncSession

from app.models.topic import Topic


class TopicFactory:
    """Create and persist Topic test data using the current test session."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def __call__(
        self,
        *,
        name: str,
        slug: str,
        parent: Topic | None = None,
    ) -> Topic:
        topic = Topic(
            name=name,
            slug=slug,
            parent_id=parent.id if parent is not None else None,
        )

        self._session.add(topic)
        await self._session.flush()

        return topic
