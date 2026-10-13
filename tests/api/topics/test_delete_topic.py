from uuid import uuid4

from fastapi import status
from httpx import AsyncClient

from tests.api.types import TopicServiceOverride
from tests.unit.factories import make_topic


async def test_deletes_leaf_topic(
    api_client: AsyncClient,
    topic_service_override: TopicServiceOverride,
) -> None:
    topic = make_topic()
    _, uow = topic_service_override(topics=[topic])

    response = await api_client.delete(f"/api/topics/{topic.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert response.content == b""
    assert await uow.topics.get_by_id(topic.id) is None
    assert uow.committed is True


async def test_returns_404_when_topic_does_not_exist(
    api_client: AsyncClient,
    topic_service_override: TopicServiceOverride,
) -> None:
    topic_id = uuid4()
    topic_service_override()

    response = await api_client.delete(f"/api/topics/{topic_id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": f"Topic '{topic_id}' was not found."}


async def test_returns_409_when_topic_has_children(
    api_client: AsyncClient,
    topic_service_override: TopicServiceOverride,
) -> None:
    parent = make_topic()
    child = make_topic(parent_id=parent.id, name="Asyncio", slug="asyncio")
    _, uow = topic_service_override(topics=[parent, child])

    response = await api_client.delete(f"/api/topics/{parent.id}")

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json() == {
        "detail": f"Topic '{parent.id}' cannot be deleted while it has child topics."
    }
    assert await uow.topics.get_by_id(parent.id) is not None
    assert uow.committed is False


async def test_returns_422_when_topic_id_is_invalid(
    api_client: AsyncClient,
    topic_service_override: TopicServiceOverride,
) -> None:
    topic_service_override()

    response = await api_client.delete("/api/topics/not-a-uuid")

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
