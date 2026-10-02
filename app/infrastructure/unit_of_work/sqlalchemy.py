from types import TracebackType
from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.infrastructure.repositories.topic import SQLAlchemyTopicRepository
from app.repositories.topic import TopicRepository


class SQLAlchemyUnitOfWork:
    """
    SQLAlchemy implementation of UoW pattern.

    A UoW represents one app-level transaction.

    It owns SQLAlchemy session used during transaction
    and creates repositories bound to that session.
    This means that changes made through different repositories can be later
    commited or rolled back together as one atomic operation.

    Service layer should NOT work with AsyncSession directly.
    It should only talk to repositories exposed by the UoW and decide when
    the operation should be commited.

    Entering the context creates a fresh session and repo instances.
    Exiting the context rolls back any work that is not committed yet
    and ALWAYS closes the session.
    """

    # Expose the repo via its abstraction instead of SQLAlchemyTopicRepository
    # This implementation is infrastructure detail and caller should not depend on it.
    topics: TopicRepository

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        # Store fActory instead of already created session.
        # New AsyncSession will be cerated of every UoW context.
        # One UoW instance represents one transaction lifecycle
        self._session_factory = session_factory

    async def __aenter__(self) -> Self:
        """Start a new Unit of Work and prepare its repositories."""

        self._session = self._session_factory()
        # Every repo created here gets the same session.
        # Because of that all repo operations in the same transaction
        # can be commited or rolled back together
        self.topics = SQLAlchemyTopicRepository(self._session)

        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Safely exit Unit of Work and release database resources."""
        try:
            # If a transaction is still active here, commit() was not
            # called or more DB work happened after the last commit.
            #
            # Rolling it back makes the default behavior safe:
            # forgetting to commit does not accidentally persist changes.
            if self._session.in_transaction():
                await self.rollback()
        finally:
            # Closing the session must happen even if rollback itself fails.
            await self._session.close()

    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()
