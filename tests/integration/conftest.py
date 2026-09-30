from collections.abc import AsyncGenerator

import pytest_asyncio
from pydantic_settings import SettingsConfigDict
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from app.core.config import Settings


class IntegrationSettings(Settings):
    """App settings for integration test env."""

    model_config = SettingsConfigDict(env_file=".env.test", env_file_encoding="utf-8")


test_settings = IntegrationSettings()

if test_settings.POSTGRES_DB != "recallstack_test":
    raise RuntimeError("Refusing to run integration tests against a non-test database.")


@pytest_asyncio.fixture(scope="session")
async def engine() -> AsyncGenerator[AsyncEngine, None]:
    """
    Shared async sqlalchemy engine for integration tests.

    Engine is created once per session and connects only to test database.
    Connection pool is disposed after all tests have finished.
    """
    engine = create_async_engine(test_settings.database_url)

    yield engine

    # Release poooled db connections after test session
    await engine.dispose()
