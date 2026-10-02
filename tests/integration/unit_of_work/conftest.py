from collections.abc import AsyncGenerator

import pytest_asyncio
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.models.topic import Topic


@pytest_asyncio.fixture(autouse=True)
async def clean_topics(
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[None, None]:
    """Keep committed UoW test data from leaking between tests."""

    async def cleanup() -> None:
        async with session_factory() as session:
            await session.execute(delete(Topic))
            await session.commit()

    # Also clean before the test in case a previous interrupted test run
    # left committed data in the test database.
    await cleanup()

    yield

    await cleanup()
