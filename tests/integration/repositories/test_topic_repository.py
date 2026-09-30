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


async def test_get_roots_returns_only_root_topics(
    db_session: AsyncSession,
) -> None:
    # Arrange
    python = Topic(
        name="Python",
        slug="python",
    )
    sql = Topic(
        name="SQL",
        slug="sql",
    )

    db_session.add_all([python, sql])
    await db_session.flush()

    asyncio_topic = Topic(
        name="Asyncio",
        slug="asyncio",
        parent_id=python.id,
    )

    db_session.add(asyncio_topic)
    await db_session.flush()

    repository = SQLAlchemyTopicRepository(db_session)

    # Act
    result = await repository.get_roots()

    # Assert
    result_ids = {topic.id for topic in result}
    assert result_ids == {python.id, sql.id}


async def test_get_roots_returns_empty_if_no_root_topics(
    db_session: AsyncSession,
) -> None:
    repository = SQLAlchemyTopicRepository(db_session)

    result = await repository.get_roots()
    assert result == []


async def test_get_children_returns_only_direct_children_of_parent(
    db_session: AsyncSession,
) -> None:
    # root topics first
    python = Topic(
        name="Python",
        slug="python",
    )
    sql = Topic(
        name="SQL",
        slug="sql",
    )

    db_session.add_all([python, sql])
    await db_session.flush()

    # Create direct children
    asyncio_topic = Topic(
        name="Asyncio",
        slug="asyncio",
        parent_id=python.id,
    )
    data_structures = Topic(
        name="Data Structures",
        slug="data-structures",
        parent_id=python.id,
    )
    joins = Topic(
        name="JOINs",
        slug="joins",
        parent_id=sql.id,
    )

    db_session.add_all([asyncio_topic, data_structures, joins])
    await db_session.flush()

    # Create a grandchild of Python.
    # It must NOT be returned because get_children() returns direct children only.
    tasks = Topic(
        name="Tasks",
        slug="tasks",
        parent_id=asyncio_topic.id,
    )

    db_session.add(tasks)
    await db_session.flush()

    repository = SQLAlchemyTopicRepository(db_session)

    result = await repository.get_children(python.id)

    result_ids = {topic.id for topic in result}

    assert result_ids == {
        asyncio_topic.id,
        data_structures.id,
    }
