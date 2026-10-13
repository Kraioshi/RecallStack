from fastapi import status
from httpx import AsyncClient

from tests.api.types import TopicServiceOverride
from tests.unit.factories import make_topic


async def test_returns_only_root_topics(
    api_client: AsyncClient,
    topic_service_override: TopicServiceOverride,
) -> None:
    python = make_topic(name="Python", slug="python")
    sql = make_topic(name="SQL", slug="sql")
    child = make_topic(name="Asyncio", slug="asyncio", parent_id=python.id)
    topic_service_override(topics=[python, sql, child])

    response = await api_client.get("/api/topics")

    assert response.status_code == status.HTTP_200_OK
    assert {item["id"] for item in response.json()} == {
        str(python.id),
        str(sql.id),
    }


async def test_returns_empty_list_when_no_topics_exist(
    api_client: AsyncClient,
    topic_service_override: TopicServiceOverride,
) -> None:
    topic_service_override()

    response = await api_client.get("/api/topics")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []
