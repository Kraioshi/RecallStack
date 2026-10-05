from uuid import uuid4

import pytest

from app.core.dto.topic import (
    CreateTopicData,
    TopicData,
    TopicQuestionCountData,
    TopicTreeData,
    UpdateTopicData,
)
from app.core.enums.question import QuestionDifficulty
from app.core.exceptions.topic import (
    TopicHasChildrenError,
    TopicNotFoundError,
    TopicSlugAlreadyExistsError,
)
from app.core.helpers.dates import now
from app.models.topic import Topic
from tests.unit.factories import make_question, make_topic
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


class TestListChildren:
    async def test_returns_only_direct_children(
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
        sql_joins = make_topic(
            name="JOINs",
            slug="joins",
            parent_id=sql.id,
        )

        service, _ = topic_service_factory([python, sql, asyncio_topic, sql_joins])

        result = await service.list_children(python.id)

        assert {topic.id for topic in result} == {asyncio_topic.id}

    async def test_returns_empty_list_when_parent_has_no_children(
        self,
        topic_service_factory: TopicServiceFactory,
    ) -> None:
        python = make_topic(
            name="Python",
            slug="python",
        )
        service, _ = topic_service_factory([python])

        result = await service.list_children(python.id)
        assert result == []

    async def test_raises_when_parent_does_not_exist(
        self, topic_service_factory: TopicServiceFactory
    ) -> None:
        missing_parent_id = uuid4()

        service, _ = topic_service_factory()

        with pytest.raises(TopicNotFoundError) as exc_info:
            await service.list_children(missing_parent_id)

        assert exc_info.value.topic_id == missing_parent_id


class TestCreateTopic:
    async def test_creates_root_topic(
        self,
        topic_service_factory: TopicServiceFactory,
    ) -> None:
        service, uow = topic_service_factory()

        data = CreateTopicData(
            name="Python",
            slug="python",
            description="Python topics",
        )

        result = await service.create_topic(data)

        assert isinstance(result, TopicData)
        assert result.id is not None
        assert result.name == "Python"
        assert result.slug == "python"
        assert result.description == "Python topics"
        assert result.parent_id is None
        assert result.created_at is not None
        assert result.updated_at is not None

        assert uow.committed is True

    async def test_creates_child_topic_under_existing_parent(
        self,
        topic_service_factory: TopicServiceFactory,
    ) -> None:
        parent = make_topic(
            name="Python",
            slug="python",
        )

        service, uow = topic_service_factory([parent])

        data = CreateTopicData(
            name="Asyncio",
            slug="asyncio",
            description=None,
            parent_id=parent.id,
        )

        result = await service.create_topic(data)

        assert result.name == "Asyncio"
        assert result.slug == "asyncio"
        assert result.parent_id == parent.id

        assert uow.committed is True

    async def test_raises_when_parent_does_not_exist(
        self,
        topic_service_factory: TopicServiceFactory,
    ) -> None:
        missing_parent_id = uuid4()

        service, uow = topic_service_factory()

        data = CreateTopicData(
            name="Asyncio",
            slug="asyncio",
            description=None,
            parent_id=missing_parent_id,
        )

        with pytest.raises(TopicNotFoundError) as exc_info:
            await service.create_topic(data)

        assert exc_info.value.topic_id == missing_parent_id
        assert uow.committed is False

    async def test_raises_when_root_slug_already_exists(
        self,
        topic_service_factory: TopicServiceFactory,
    ) -> None:
        existing = make_topic(
            name="Python",
            slug="python",
        )

        service, uow = topic_service_factory([existing])

        data = CreateTopicData(
            name="Another Python",
            slug="python",
            description=None,
        )

        with pytest.raises(TopicSlugAlreadyExistsError) as exc_info:
            await service.create_topic(data)

        assert exc_info.value.slug == "python"
        assert exc_info.value.parent_id is None
        assert uow.committed is False

    async def test_raises_when_sibling_slug_already_exists(
        self,
        topic_service_factory: TopicServiceFactory,
    ) -> None:
        parent = make_topic(
            name="Python",
            slug="python",
        )
        existing_child = make_topic(
            name="Python Basics",
            slug="basics",
            parent_id=parent.id,
        )

        service, uow = topic_service_factory([parent, existing_child])

        data = CreateTopicData(
            name="Other Basics",
            slug="basics",
            description=None,
            parent_id=parent.id,
        )

        with pytest.raises(TopicSlugAlreadyExistsError) as exc_info:
            await service.create_topic(data)

        assert exc_info.value.slug == "basics"
        assert exc_info.value.parent_id == parent.id
        assert uow.committed is False

    async def test_allows_same_slug_under_different_parent(
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
        python_basics = make_topic(
            name="Python Basics",
            slug="basics",
            parent_id=python.id,
        )

        service, uow = topic_service_factory([python, sql, python_basics])

        data = CreateTopicData(
            name="SQL Basics",
            slug="basics",
            description=None,
            parent_id=sql.id,
        )

        result = await service.create_topic(data)

        assert result.slug == "basics"
        assert result.parent_id == sql.id
        assert uow.committed is True


class TestUpdateTopic:
    async def test_updates_only_provided_fields(
        self,
        topic_service_factory: TopicServiceFactory,
    ) -> None:
        topic = make_topic(
            name="Python",
            slug="python",
            description="Python programming",
        )
        service, uow = topic_service_factory([topic])

        data = UpdateTopicData(
            name="Python 3",
        )

        result = await service.update_topic(topic.id, data)

        assert result.name == "Python 3"
        assert result.slug == "python"
        assert result.description == "Python programming"
        assert result.parent_id == topic.parent_id

        assert uow.committed is True

    async def test_clears_description_when_none_is_provided(
        self,
        topic_service_factory: TopicServiceFactory,
    ) -> None:
        topic = make_topic(
            name="Python",
            slug="python",
            description="Python programming",
        )
        service, uow = topic_service_factory([topic])

        data = UpdateTopicData(
            description=None,
        )

        result = await service.update_topic(topic.id, data)

        assert result.description is None
        assert result.name == "Python"
        assert result.slug == "python"

        assert uow.committed is True

    async def test_raises_when_topic_does_not_exist(
        self,
        topic_service_factory: TopicServiceFactory,
    ) -> None:
        missing_topic_id = uuid4()

        service, uow = topic_service_factory()

        data = UpdateTopicData(
            name="Python",
        )

        with pytest.raises(TopicNotFoundError) as exc_info:
            await service.update_topic(missing_topic_id, data)

        assert exc_info.value.topic_id == missing_topic_id
        assert uow.committed is False

    async def test_raises_when_new_slug_conflicts_with_sibling(
        self,
        topic_service_factory: TopicServiceFactory,
    ) -> None:
        parent = make_topic(
            name="Python",
            slug="python",
        )
        asyncio_topic = make_topic(
            name="Asyncio",
            slug="asyncio",
            parent_id=parent.id,
        )
        typing_topic = make_topic(
            name="Typing",
            slug="typing",
            parent_id=parent.id,
        )

        service, uow = topic_service_factory([parent, asyncio_topic, typing_topic])

        data = UpdateTopicData(
            slug="typing",
        )

        with pytest.raises(TopicSlugAlreadyExistsError) as exc_info:
            await service.update_topic(asyncio_topic.id, data)

        assert exc_info.value.slug == "typing"
        assert exc_info.value.parent_id == parent.id

        assert asyncio_topic.slug == "asyncio"
        assert uow.committed is False

    async def test_allows_keeping_current_slug(
        self,
        topic_service_factory: TopicServiceFactory,
    ) -> None:
        topic = make_topic(
            name="Python",
            slug="python",
            description="Old description",
        )
        service, uow = topic_service_factory([topic])

        data = UpdateTopicData(
            slug="python",
            description="New description",
        )

        result = await service.update_topic(topic.id, data)

        assert result.slug == "python"
        assert result.description == "New description"

        assert uow.committed is True

    async def test_allows_slug_used_under_different_parent(
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

        python_basics = make_topic(
            name="Python Basics",
            slug="basics",
            parent_id=python.id,
        )
        sql_joins = make_topic(
            name="SQL Joins",
            slug="joins",
            parent_id=sql.id,
        )

        service, uow = topic_service_factory([python, sql, python_basics, sql_joins])

        data = UpdateTopicData(
            slug="basics",
        )

        result = await service.update_topic(sql_joins.id, data)

        assert result.slug == "basics"
        assert result.parent_id == sql.id

        assert uow.committed is True


class TestDeleteTopic:
    async def test_deletes_leaf_topic(
        self,
        topic_service_factory: TopicServiceFactory,
    ) -> None:
        topic = make_topic(
            name="Python",
            slug="python",
        )

        service, uow = topic_service_factory([topic])

        await service.delete_topic(topic.id)

        assert await uow.topics.get_by_id(topic.id) is None
        assert uow.committed is True

    async def test_raises_when_topic_does_not_exist(
        self,
        topic_service_factory: TopicServiceFactory,
    ) -> None:
        missing_topic_id = uuid4()

        service, uow = topic_service_factory()

        with pytest.raises(TopicNotFoundError) as exc_info:
            await service.delete_topic(missing_topic_id)

        assert exc_info.value.topic_id == missing_topic_id
        assert uow.committed is False

    async def test_raises_when_topic_has_children(
        self,
        topic_service_factory: TopicServiceFactory,
    ) -> None:
        parent = make_topic(
            name="Python",
            slug="python",
        )
        child = make_topic(
            name="Asyncio",
            slug="asyncio",
            parent_id=parent.id,
        )

        service, uow = topic_service_factory([parent, child])

        with pytest.raises(TopicHasChildrenError) as exc_info:
            await service.delete_topic(parent.id)

        assert exc_info.value.topic_id == parent.id
        assert await uow.topics.get_by_id(parent.id) is not None
        assert await uow.topics.get_by_id(child.id) is not None
        assert uow.committed is False


class TestGetTree:
    async def test_returns_full_topic_tree(
        self,
        topic_service_factory: TopicServiceFactory,
    ) -> None:
        python = make_topic(
            name="Python",
            slug="python",
        )
        frameworks = make_topic(
            name="Frameworks",
            slug="frameworks",
            parent_id=python.id,
        )
        fastapi = make_topic(
            name="FastAPI",
            slug="fastapi",
            parent_id=frameworks.id,
        )
        core = make_topic(
            name="Core Concepts",
            slug="core-concepts",
            parent_id=fastapi.id,
        )
        routing = make_topic(
            name="Routing",
            slug="routing",
            parent_id=fastapi.id,
        )
        sql = make_topic(
            name="SQL",
            slug="sql",
        )

        service, _ = topic_service_factory(
            [
                python,
                frameworks,
                fastapi,
                core,
                routing,
                sql,
            ]
        )

        result = await service.get_tree()
        zero_counts = TopicQuestionCountData(easy=0, medium=0, hard=0, total=0)

        assert result == [
            TopicTreeData(
                id=python.id,
                name="Python",
                slug="python",
                description=python.description,
                question_counts=zero_counts,
                children=(
                    TopicTreeData(
                        id=frameworks.id,
                        name="Frameworks",
                        slug="frameworks",
                        description=frameworks.description,
                        question_counts=zero_counts,
                        children=(
                            TopicTreeData(
                                id=fastapi.id,
                                name="FastAPI",
                                slug="fastapi",
                                description=fastapi.description,
                                question_counts=zero_counts,
                                children=(
                                    TopicTreeData(
                                        id=core.id,
                                        name="Core Concepts",
                                        slug="core-concepts",
                                        description=core.description,
                                        question_counts=zero_counts,
                                    ),
                                    TopicTreeData(
                                        id=routing.id,
                                        name="Routing",
                                        slug="routing",
                                        description=routing.description,
                                        question_counts=zero_counts,
                                    ),
                                ),
                            ),
                        ),
                    ),
                ),
            ),
            TopicTreeData(
                id=sql.id,
                name="SQL",
                slug="sql",
                description=sql.description,
                question_counts=zero_counts,
            ),
        ]

    async def test_returns_full_topic_tree_with_question_counts_by_difficulty(
        self,
        topic_service_factory: TopicServiceFactory,
    ) -> None:
        python = make_topic(
            name="Python",
            slug="python",
        )
        frameworks = make_topic(
            name="Frameworks",
            slug="frameworks",
            parent_id=python.id,
        )
        fastapi = make_topic(
            name="FastAPI",
            slug="fastapi",
            parent_id=frameworks.id,
        )
        core = make_topic(
            name="Core Concepts",
            slug="core-concepts",
            parent_id=fastapi.id,
        )
        routing = make_topic(
            name="Routing",
            slug="routing",
            parent_id=fastapi.id,
        )
        sql = make_topic(
            name="SQL",
            slug="sql",
        )

        core_easy_1 = make_question(
            topic_id=core.id,
            difficulty=QuestionDifficulty.EASY,
        )
        core_easy_2 = make_question(
            topic_id=core.id,
            difficulty=QuestionDifficulty.EASY,
        )
        core_medium = make_question(
            topic_id=core.id,
            difficulty=QuestionDifficulty.MEDIUM,
        )
        core_hard = make_question(
            topic_id=core.id,
            difficulty=QuestionDifficulty.HARD,
        )

        routing_medium = make_question(
            topic_id=routing.id,
            difficulty=QuestionDifficulty.MEDIUM,
        )

        service, _ = topic_service_factory(
            topics=[
                python,
                frameworks,
                fastapi,
                core,
                routing,
                sql,
            ],
            questions=[
                core_easy_1,
                core_easy_2,
                core_medium,
                core_hard,
                routing_medium,
            ],
        )

        result = await service.get_tree()
        zero_counts = TopicQuestionCountData(
            easy=0,
            medium=0,
            hard=0,
            total=0,
        )

        assert result == [
            TopicTreeData(
                id=python.id,
                name="Python",
                slug="python",
                description=python.description,
                question_counts=zero_counts,
                children=(
                    TopicTreeData(
                        id=frameworks.id,
                        name="Frameworks",
                        slug="frameworks",
                        description=frameworks.description,
                        question_counts=zero_counts,
                        children=(
                            TopicTreeData(
                                id=fastapi.id,
                                name="FastAPI",
                                slug="fastapi",
                                description=fastapi.description,
                                question_counts=zero_counts,
                                children=(
                                    TopicTreeData(
                                        id=core.id,
                                        name="Core Concepts",
                                        slug="core-concepts",
                                        description=core.description,
                                        question_counts=TopicQuestionCountData(
                                            easy=2,
                                            medium=1,
                                            hard=1,
                                            total=4,
                                        ),
                                    ),
                                    TopicTreeData(
                                        id=routing.id,
                                        name="Routing",
                                        slug="routing",
                                        description=routing.description,
                                        question_counts=TopicQuestionCountData(
                                            easy=0,
                                            medium=1,
                                            hard=0,
                                            total=1,
                                        ),
                                    ),
                                ),
                            ),
                        ),
                    ),
                ),
            ),
            TopicTreeData(
                id=sql.id,
                name="SQL",
                slug="sql",
                description=sql.description,
                question_counts=zero_counts,
            ),
        ]

    async def test_returns_empty_list_when_no_topics_exist(
        self,
        topic_service_factory: TopicServiceFactory,
    ) -> None:
        service, _ = topic_service_factory()

        result = await service.get_tree()

        assert result == []
