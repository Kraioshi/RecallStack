from uuid import uuid4

import pytest
from fastapi import status
from httpx import AsyncClient

from tests.api.types import TopicServiceOverride
from tests.unit.factories import make_topic


async def test_updates_only_provided_fields(
    api_client: AsyncClient,
    topic_service_override: TopicServiceOverride,
) -> None:
    topic = make_topic(description="Original description")
    _, uow = topic_service_override(topics=[topic])

    response = await api_client.patch(
        f"/api/topics/{topic.id}", json={"name": "Python 3"}
    )

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["id"] == str(topic.id)
    assert body["name"] == "Python 3"
    assert body["slug"] == "python"
    assert body["description"] == "Original description"
    assert uow.committed is True


async def test_clears_description_with_explicit_null(
    api_client: AsyncClient,
    topic_service_override: TopicServiceOverride,
) -> None:
    topic = make_topic(description="To be cleared")
    topic_service_override(topics=[topic])

    response = await api_client.patch(
        f"/api/topics/{topic.id}", json={"description": None}
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["description"] is None


async def test_returns_409_when_new_slug_conflicts_with_sibling(
    api_client: AsyncClient,
    topic_service_override: TopicServiceOverride,
) -> None:
    parent = make_topic()
    first = make_topic(slug="asyncio", parent_id=parent.id)
    second = make_topic(slug="typing", parent_id=parent.id)
    _, uow = topic_service_override(topics=[parent, first, second])

    response = await api_client.patch(
        f"/api/topics/{first.id}", json={"slug": second.slug}
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json() == {
        "detail": f"Topic with slug 'typing' already exists under parent '{parent.id}'."
    }
    assert first.slug == "asyncio"
    assert uow.committed is False


async def test_allows_keeping_own_slug(
    api_client: AsyncClient,
    topic_service_override: TopicServiceOverride,
) -> None:
    topic = make_topic()
    topic_service_override(topics=[topic])

    response = await api_client.patch(
        f"/api/topics/{topic.id}", json={"slug": topic.slug}
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["slug"] == topic.slug


async def test_returns_404_when_topic_does_not_exist(
    api_client: AsyncClient,
    topic_service_override: TopicServiceOverride,
) -> None:
    topic_id = uuid4()
    topic_service_override()

    response = await api_client.patch(
        f"/api/topics/{topic_id}", json={"name": "Python"}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": f"Topic '{topic_id}' was not found."}


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"name": None},
        {"slug": None},
        {"name": ""},
        {"slug": ""},
        {"name": "x" * 101},
    ],
)
async def test_returns_422_for_invalid_update_body(
    api_client: AsyncClient,
    topic_service_override: TopicServiceOverride,
    payload: dict[str, object],
) -> None:
    topic = make_topic()
    topic_service_override(topics=[topic])

    response = await api_client.patch(f"/api/topics/{topic.id}", json=payload)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_returns_422_when_topic_id_is_invalid(
    api_client: AsyncClient,
    topic_service_override: TopicServiceOverride,
) -> None:
    topic_service_override()

    response = await api_client.patch("/api/topics/not-a-uuid", json={"name": "Python"})

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
