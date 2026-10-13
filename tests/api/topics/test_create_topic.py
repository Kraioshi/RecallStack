from uuid import uuid4

import pytest
from fastapi import status
from httpx import AsyncClient

from tests.api.types import TopicServiceOverride
from tests.unit.factories import make_topic


async def test_creates_root_topic(
    api_client: AsyncClient,
    topic_service_override: TopicServiceOverride,
) -> None:
    _, uow = topic_service_override()
    payload = {
        "name": "Python",
        "slug": "python",
        "description": "Python interview questions",
    }

    response = await api_client.post("/api/topics", json=payload)

    assert response.status_code == status.HTTP_201_CREATED
    body = response.json()
    assert body["id"] is not None
    assert body["parent_id"] is None
    assert body["name"] == payload["name"]
    assert body["slug"] == payload["slug"]
    assert body["description"] == payload["description"]
    assert body["created_at"] is not None
    assert body["updated_at"] is not None
    assert uow.committed is True


async def test_creates_child_topic(
    api_client: AsyncClient,
    topic_service_override: TopicServiceOverride,
) -> None:
    parent = make_topic()
    topic_service_override(topics=[parent])

    response = await api_client.post(
        "/api/topics",
        json={
            "name": "Asyncio",
            "slug": "asyncio",
            "parent_id": str(parent.id),
        },
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["parent_id"] == str(parent.id)


async def test_returns_404_when_parent_does_not_exist(
    api_client: AsyncClient,
    topic_service_override: TopicServiceOverride,
) -> None:
    parent_id = uuid4()
    _, uow = topic_service_override()

    response = await api_client.post(
        "/api/topics",
        json={"name": "Asyncio", "slug": "asyncio", "parent_id": str(parent_id)},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": f"Topic '{parent_id}' was not found."}
    assert uow.committed is False


async def test_returns_409_when_root_slug_already_exists(
    api_client: AsyncClient,
    topic_service_override: TopicServiceOverride,
) -> None:
    existing = make_topic()
    _, uow = topic_service_override(topics=[existing])

    response = await api_client.post(
        "/api/topics",
        json={"name": "Python 2", "slug": existing.slug},
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json() == {
        "detail": f"Topic with slug '{existing.slug}' already exists at root level."
    }
    assert uow.committed is False


async def test_returns_409_when_sibling_slug_already_exists(
    api_client: AsyncClient,
    topic_service_override: TopicServiceOverride,
) -> None:
    parent = make_topic()
    existing = make_topic(slug="asyncio", parent_id=parent.id)
    topic_service_override(topics=[parent, existing])

    response = await api_client.post(
        "/api/topics",
        json={
            "name": "Another asyncio",
            "slug": "asyncio",
            "parent_id": str(parent.id),
        },
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json() == {
        "detail": (
            f"Topic with slug 'asyncio' already exists under parent '{parent.id}'."
        ),
    }


async def test_allows_same_slug_under_different_parents(
    api_client: AsyncClient,
    topic_service_override: TopicServiceOverride,
) -> None:
    python = make_topic(name="Python", slug="python")
    sql = make_topic(name="SQL", slug="sql")
    existing = make_topic(slug="basics", parent_id=python.id)
    topic_service_override(topics=[python, sql, existing])

    response = await api_client.post(
        "/api/topics",
        json={"name": "SQL Basics", "slug": "basics", "parent_id": str(sql.id)},
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["parent_id"] == str(sql.id)


@pytest.mark.parametrize(
    "invalid_field",
    [
        {"name": ""},
        {"slug": ""},
        {"name": "x" * 101},
        {"slug": "x" * 101},
        {"parent_id": "not-a-uuid"},
        {"name": None},
    ],
)
async def test_returns_422_for_invalid_fields(
    api_client: AsyncClient,
    topic_service_override: TopicServiceOverride,
    invalid_field: dict[str, object],
) -> None:
    topic_service_override()
    payload: dict[str, object] = {"name": "Python", "slug": "python"}
    payload.update(invalid_field)

    response = await api_client.post("/api/topics", json=payload)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
