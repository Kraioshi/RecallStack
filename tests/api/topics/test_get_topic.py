from datetime import datetime
from uuid import uuid4

from fastapi import status
from httpx import AsyncClient

from tests.api.types import TopicServiceOverride
from tests.unit.factories import make_topic


async def test_returns_existing_topic(
    api_client: AsyncClient,
    topic_service_override: TopicServiceOverride,
) -> None:
    topic = make_topic(description="Python topics")
    topic_service_override(topics=[topic])

    response = await api_client.get(f"/api/topics/{topic.id}")

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["created_at"] is not None
    assert body["updated_at"] is not None
    assert datetime.fromisoformat(body["created_at"]) == topic.created_at
    assert datetime.fromisoformat(body["updated_at"]) == topic.updated_at
    assert body["id"] == str(topic.id)
    assert body["parent_id"] is None
    assert body["name"] == topic.name
    assert body["slug"] == topic.slug
    assert body["description"] == "Python topics"


async def test_returns_404_when_topic_does_not_exist(
    api_client: AsyncClient,
    topic_service_override: TopicServiceOverride,
) -> None:
    topic_id = uuid4()
    topic_service_override()

    response = await api_client.get(f"/api/topics/{topic_id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": f"Topic '{topic_id}' was not found."}


async def test_returns_422_when_topic_id_is_invalid(
    api_client: AsyncClient,
    topic_service_override: TopicServiceOverride,
) -> None:
    topic_service_override()

    response = await api_client.get("/api/topics/not-a-uuid")

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
