from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.repositories.topic import SQLAlchemyTopicRepository
from app.models.topic import Topic
from tests.integration.repositories.factories import TopicFactory


class TestGetById:
    async def test_returns_existing_topic(
        self,
        topic_factory: TopicFactory,
        topic_repository: SQLAlchemyTopicRepository,
    ) -> None:
        topic = await topic_factory(
            name="SQL",
            slug="sql",
        )

        result = await topic_repository.get_by_id(topic.id)

        assert result is not None
        assert result.id == topic.id
        assert result.name == "SQL"
        assert result.slug == "sql"

    async def test_returns_none_when_topic_does_not_exist(
        self,
        topic_repository: SQLAlchemyTopicRepository,
    ) -> None:

        result = await topic_repository.get_by_id(uuid4())

        assert result is None


class TestGetRoots:
    async def test_returns_only_root_topics(
        self,
        topic_factory: TopicFactory,
        topic_repository: SQLAlchemyTopicRepository,
    ) -> None:
        python_topic = await topic_factory(
            name="Python",
            slug="python",
        )
        sql_topic = await topic_factory(
            name="SQL",
            slug="sql",
        )

        await topic_factory(
            name="Asyncio",
            slug="asyncio",
            parent=python_topic,
        )

        result = await topic_repository.get_roots()

        result_ids = {topic.id for topic in result}

        assert result_ids == {
            python_topic.id,
            sql_topic.id,
        }

    async def test_returns_empty_list_when_no_topics_exist(
        self,
        topic_repository: SQLAlchemyTopicRepository,
    ) -> None:
        result = await topic_repository.get_roots()

        assert result == []


class TestGetChildren:
    async def test_returns_only_direct_children_of_parent(
        self,
        topic_factory: TopicFactory,
        topic_repository: SQLAlchemyTopicRepository,
    ) -> None:
        python_topic = await topic_factory(
            name="Python",
            slug="python",
        )
        sql_topic = await topic_factory(
            name="SQL",
            slug="sql",
        )

        asyncio_topic = await topic_factory(
            name="Asyncio",
            slug="asyncio",
            parent=python_topic,
        )
        data_structures = await topic_factory(
            name="Data Structures",
            slug="data-structures",
            parent=python_topic,
        )

        await topic_factory(
            name="JOINs",
            slug="joins",
            parent=sql_topic,
        )

        await topic_factory(
            name="Tasks",
            slug="tasks",
            parent=asyncio_topic,
        )

        result = await topic_repository.get_children(python_topic.id)

        result_ids = {topic.id for topic in result}

        assert result_ids == {
            asyncio_topic.id,
            data_structures.id,
        }

    async def test_returns_empty_list_when_parent_has_no_children(
        self,
        topic_factory: TopicFactory,
        topic_repository: SQLAlchemyTopicRepository,
    ) -> None:
        python_topic = await topic_factory(
            name="Python",
            slug="python",
        )

        result = await topic_repository.get_children(python_topic.id)

        assert result == []


class TestAdd:
    async def test_persists_topic(
        self,
        db_session: AsyncSession,
        topic_repository: SQLAlchemyTopicRepository,
    ) -> None:
        topic = Topic(
            name="Python",
            slug="python",
        )

        result = await topic_repository.add(topic)

        assert result.id is not None
        topic_id = result.id

        db_session.expunge(result)

        persisted_topic = await topic_repository.get_by_id(topic_id)

        assert persisted_topic is not None
        assert persisted_topic.id == topic_id
        assert persisted_topic.name == "Python"
        assert persisted_topic.slug == "python"


class TestGetBySlug:
    async def test_returns_root_topic(
        self,
        topic_factory: TopicFactory,
        topic_repository: SQLAlchemyTopicRepository,
    ) -> None:
        topic = await topic_factory(
            name="Python",
            slug="python",
        )

        result = await topic_repository.get_by_slug(
            slug="python",
            parent_id=None,
        )

        assert result is not None
        assert result.id == topic.id
        assert result.slug == "python"
        assert result.parent_id is None

    async def test_returns_topic_under_requested_parent(
        self,
        topic_factory: TopicFactory,
        topic_repository: SQLAlchemyTopicRepository,
    ) -> None:
        parent = await topic_factory(
            name="Parent Python",
            slug="parent-python",
        )

        topic = await topic_factory(
            name="Python",
            slug="python",
            parent=parent,
        )

        result = await topic_repository.get_by_slug(
            slug="python",
            parent_id=parent.id,
        )

        assert result is not None
        assert result.id == topic.id
        assert result.slug == "python"
        assert result.parent_id == parent.id

    async def test_distinguishes_same_slug_under_different_parents(
        self,
        topic_factory: TopicFactory,
        topic_repository: SQLAlchemyTopicRepository,
    ) -> None:
        python_parent = await topic_factory(
            name="Python",
            slug="python",
        )
        sql_parent = await topic_factory(
            name="SQL",
            slug="sql",
        )

        python_basics = await topic_factory(
            name="Python Basics",
            slug="basics",
            parent=python_parent,
        )
        sql_basics = await topic_factory(
            name="SQL Basics",
            slug="basics",
            parent=sql_parent,
        )

        python_result = await topic_repository.get_by_slug(
            slug="basics",
            parent_id=python_parent.id,
        )
        sql_result = await topic_repository.get_by_slug(
            slug="basics",
            parent_id=sql_parent.id,
        )

        assert python_result is not None
        assert sql_result is not None

        assert python_result.id == python_basics.id
        assert python_result.parent_id == python_parent.id

        assert sql_result.id == sql_basics.id
        assert sql_result.parent_id == sql_parent.id

    async def test_returns_none_when_topic_does_not_exist(
        self,
        topic_repository: SQLAlchemyTopicRepository,
    ) -> None:
        result = await topic_repository.get_by_slug(
            slug="does-not-exist",
            parent_id=None,
        )

        assert result is None
