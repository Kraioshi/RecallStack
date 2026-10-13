from uuid import uuid4

from fastapi import status
from httpx import AsyncClient

from tests.api.types import TopicServiceOverride
from tests.unit.factories import make_topic


async def test_returns_only_direct_children(
    api_client: AsyncClient,
    topic_service_override: TopicServiceOverride,
) -> None:
    parent = make_topic(name="Python", slug="python")
    child = make_topic(name="Asyncio", slug="asyncio", parent_id=parent.id)
    grandchild = make_topic(name="Tasks", slug="tasks", parent_id=child.id)
    unrelated = make_topic(name="SQL", slug="sql")
    topic_service_override(topics=[parent, child, grandchild, unrelated])

    response = await api_client.get(f"/api/topics/{parent.id}/children")

    assert response.status_code == status.HTTP_200_OK
    assert [item["id"] for item in response.json()] == [str(child.id)]


async def test_returns_empty_list_when_topic_has_no_children(
    api_client: AsyncClient,
    topic_service_override: TopicServiceOverride,
) -> None:
    topic = make_topic()
    topic_service_override(topics=[topic])

    response = await api_client.get(f"/api/topics/{topic.id}/children")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


async def test_returns_404_when_parent_does_not_exist(
    api_client: AsyncClient,
    topic_service_override: TopicServiceOverride,
) -> None:
    topic_id = uuid4()
    topic_service_override()

    response = await api_client.get(f"/api/topics/{topic_id}/children")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": f"Topic '{topic_id}' was not found."}


async def test_returns_422_when_parent_id_is_invalid(
    api_client: AsyncClient,
    topic_service_override: TopicServiceOverride,
) -> None:
    topic_service_override()

    response = await api_client.get("/api/topics/not-a-uuid/children")

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
