from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from pydantic_settings import SettingsConfigDict
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app.core.config import Settings
from app.database.base import Base

# Explicit import registers required models in Base.metadata.
# FIXME: Consider central model registration via app/models/__init__.py.
from app.models.topic import Topic  # noqa: F401


class IntegrationSettings(Settings):
    """App settings for integration test env."""

    model_config = SettingsConfigDict(env_file=".env.test", env_file_encoding="utf-8")


test_settings = IntegrationSettings()

if test_settings.POSTGRES_DB != "recallstack_test":
    raise RuntimeError("Refusing to run integration tests against a non-test database.")


@pytest_asyncio.fixture(scope="session")
async def engine() -> AsyncGenerator[AsyncEngine, None]:
    """
    Shared async SQLAlchemy engine for integration tests.

    The engine is created once per test session and connects only to the test database.
    NullPool prevents asyncpg connections from being reused
    across async test contexts.
    """
    engine = create_async_engine(test_settings.database_url, poolclass=NullPool)

    # Create test schema from SQLAlchemy models
    #
    # `create_all` is part of sync metadata API, so `run_sync()`
    # acts like a SQLAlchemy's bridge to sync metadata API
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    yield engine

    # Remove test schema and dispose of engine resources.
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)

    await engine.dispose()


# NOTE: This rollback strategy assumes code under test does not call session.commit().
#
# If that changes, use nested transactions/save points to keep test isolation.
@pytest_asyncio.fixture
async def db_session(engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """Provide isolated db session for each integration test."""
    # Transaction should live outside the AsyncSession, so
    # the fixture will be able to roll back everything after the test.
    #
    # Start the transaction OUTSIDE AsyncSession so the fixture controls its
    # lifetime independently of the session.
    #
    # Otherwise, using session = AsyncSession(engine) directly would let the session
    # acquire and manage own connections instead.
    async with engine.connect() as connection:
        transaction = await connection.begin()

        # Bind the session to this specific connection.
        # Without this session will get own connection and ops
        # wouldn't necessarily belong to the transaction above.
        #
        # expire_on_commit - keep orm objects usable after a commit
        # without SQLAlchemy expiring their loaded attrs.
        session = AsyncSession(
            bind=connection,
            expire_on_commit=False,
        )

        try:
            yield session
        finally:
            if transaction.is_active:
                await transaction.rollback()

            await session.close()


@pytest.fixture
def session_factory(
    engine: AsyncEngine,
) -> async_sessionmaker[AsyncSession]:
    """Provide AsyncSession factory bound to the integration test DB."""

    return async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
    )
