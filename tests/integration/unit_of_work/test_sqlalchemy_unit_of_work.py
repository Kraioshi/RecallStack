import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.infrastructure.unit_of_work.sqlalchemy import SQLAlchemyUnitOfWork
from app.models.topic import Topic


class TestSQLAlchemyUnitOfWork:
    async def test_commit_persists_changes(
        self,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        uow = SQLAlchemyUnitOfWork(session_factory)

        async with uow:
            topic = Topic(
                name="Python",
                slug="python",
            )

            result = await uow.topics.add(topic)

            assert result.id is not None
            topic_id = result.id

            await uow.commit()

        # Use a new session to check if the committed row
        # is really visible outside the Unit of Work.
        async with session_factory() as session:
            persisted_topic = await session.get(Topic, topic_id)

        assert persisted_topic is not None
        assert persisted_topic.name == "Python"
        assert persisted_topic.slug == "python"

    async def test_rollback_discards_changes(
        self,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        uow = SQLAlchemyUnitOfWork(session_factory)

        async with uow:
            topic = Topic(
                name="Python",
                slug="python",
            )

            result = await uow.topics.add(topic)

            assert result.id is not None
            topic_id = result.id

            await uow.rollback()

        async with session_factory() as session:
            persisted_topic = await session.get(Topic, topic_id)

        assert persisted_topic is None

    async def test_exit_without_commit_rolls_back_changes(
        self,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        uow = SQLAlchemyUnitOfWork(session_factory)

        async with uow:
            topic = Topic(
                name="Python",
                slug="python",
            )

            result = await uow.topics.add(topic)

            assert result.id is not None
            topic_id = result.id

            # No commit here!

        async with session_factory() as session:
            persisted_topic = await session.get(Topic, topic_id)

        assert persisted_topic is None

    async def test_exception_rolls_back_changes(
        self,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        uow = SQLAlchemyUnitOfWork(session_factory)

        topic = Topic(
            name="Python",
            slug="python",
        )

        with pytest.raises(RuntimeError, match="Something went wrong"):
            async with uow:
                result = await uow.topics.add(topic)

                assert result.id is not None

                raise RuntimeError("Something went wrong")

        assert topic.id is not None

        async with session_factory() as session:
            persisted_topic = await session.get(Topic, topic.id)

        assert persisted_topic is None
