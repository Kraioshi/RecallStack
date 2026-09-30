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
    python_topic = Topic(
        name="Python",
        slug="python",
    )
    sql_topic = Topic(
        name="SQL",
        slug="sql",
    )

    db_session.add_all([python_topic, sql_topic])
    await db_session.flush()

    asyncio_topic = Topic(
        name="Asyncio",
        slug="asyncio",
        parent_id=python_topic.id,
    )

    db_session.add(asyncio_topic)
    await db_session.flush()

    repository = SQLAlchemyTopicRepository(db_session)

    # Act
    result = await repository.get_roots()

    # Assert
    result_ids = {topic.id for topic in result}
    assert result_ids == {python_topic.id, sql_topic.id}


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
    python_topic = Topic(
        name="Python",
        slug="python",
    )
    sql_topic = Topic(
        name="SQL",
        slug="sql",
    )

    db_session.add_all([python_topic, sql_topic])
    await db_session.flush()

    # Create direct children
    asyncio_topic = Topic(
        name="Asyncio",
        slug="asyncio",
        parent_id=python_topic.id,
    )
    data_structures = Topic(
        name="Data Structures",
        slug="data-structures",
        parent_id=python_topic.id,
    )
    joins = Topic(
        name="JOINs",
        slug="joins",
        parent_id=sql_topic.id,
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

    result = await repository.get_children(python_topic.id)

    result_ids = {topic.id for topic in result}

    assert result_ids == {
        asyncio_topic.id,
        data_structures.id,
    }


async def test_get_children_returns_empty_list_when_parent_has_no_children(
    db_session: AsyncSession,
) -> None:
    python_topic = Topic(
        name="Python",
        slug="python",
    )

    db_session.add(python_topic)
    await db_session.flush()

    repository = SQLAlchemyTopicRepository(db_session)

    result = await repository.get_children(python_topic.id)

    assert result == []


async def test_add_persists_topic(db_session: AsyncSession) -> None:
    python_topic = Topic(
        name="Python",
        slug="python",
    )

    repository = SQLAlchemyTopicRepository(db_session)

    result = await repository.add(python_topic)

    assert result.id is not None

    persisted_topic = await repository.get_by_id(result.id)

    assert persisted_topic is not None
    assert persisted_topic.id == result.id
    assert persisted_topic.name == "Python"
    assert persisted_topic.slug == "python"


async def test_get_by_slug_returns_root_topic(
    db_session: AsyncSession,
) -> None:
    topic = Topic(
        name="Python",
        slug="python",
    )

    db_session.add(topic)
    await db_session.flush()

    repository = SQLAlchemyTopicRepository(db_session)

    result = await repository.get_by_slug(
        slug="python",
        parent_id=None,
    )

    assert result is not None
    assert result.id == topic.id
    assert result.slug == "python"
    assert result.parent_id is None


async def test_get_by_slug_returns_topic_under_requested_parent(
    db_session: AsyncSession,
) -> None:
    parent = Topic(
        name="Parent Python",
        slug="parent-python",
    )

    db_session.add(parent)
    await db_session.flush()

    topic = Topic(
        name="Python",
        slug="python",
        parent_id=parent.id,
    )

    db_session.add(topic)
    await db_session.flush()

    repository = SQLAlchemyTopicRepository(db_session)

    result = await repository.get_by_slug(
        slug="python",
        parent_id=parent.id,
    )

    assert result is not None
    assert result.id == topic.id
    assert result.slug == "python"
    assert result.parent_id == parent.id


async def test_get_by_slug_distinguishes_same_slug_under_different_parents(
    db_session: AsyncSession,
) -> None:
    python_parent = Topic(
        name="Python",
        slug="python",
    )
    sql_parent = Topic(
        name="SQL",
        slug="sql",
    )

    db_session.add_all([python_parent, sql_parent])
    await db_session.flush()

    python_basics = Topic(
        name="Python Basics",
        slug="basics",
        parent_id=python_parent.id,
    )
    sql_basics = Topic(
        name="SQL Basics",
        slug="basics",
        parent_id=sql_parent.id,
    )

    db_session.add_all([python_basics, sql_basics])
    await db_session.flush()

    repository = SQLAlchemyTopicRepository(db_session)

    python_result = await repository.get_by_slug(
        slug="basics",
        parent_id=python_parent.id,
    )
    sql_result = await repository.get_by_slug(
        slug="basics",
        parent_id=sql_parent.id,
    )

    assert python_result is not None
    assert sql_result is not None

    assert python_result.id == python_basics.id
    assert python_result.parent_id == python_parent.id

    assert sql_result.id == sql_basics.id
    assert sql_result.parent_id == sql_parent.id


async def test_get_by_slug_returns_none_when_topic_does_not_exist(
    db_session: AsyncSession,
) -> None:
    repository = SQLAlchemyTopicRepository(db_session)

    result = await repository.get_by_slug(
        slug="does-not-exist",
        parent_id=None,
    )

    assert result is None
