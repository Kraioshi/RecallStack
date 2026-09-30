import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.repositories.topic import SQLAlchemyTopicRepository
from app.models.topic import Topic


async def test_get_by_id_returns_existing_topic(db_session: AsyncSession) -> None:
    topic = Topic(name="Integration", slug="integration")
    db_session.add(topic)
    await db_session.flush()

    repository = SQLAlchemyTopicRepository(db_session)

    result = await repository.get_by_id(topic.id)

    assert result is not None
    assert result.id == topic.id
    assert result.name == "Integration"
    assert result.slug == "integration"


async def test_get_by_id_returns_none_when_topic_does_not_exist(
    db_session: AsyncSession,
) -> None:
    topic_id = uuid.uuid4()
    repository = SQLAlchemyTopicRepository(db_session)

    result = await repository.get_by_id(topic_id)

    assert result is None
