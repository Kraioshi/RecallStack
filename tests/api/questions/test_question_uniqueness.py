from fastapi import status
from httpx import AsyncClient

from tests.api.types import QuestionServiceOverride
from tests.unit.factories import make_question, make_topic


async def test_returns_409_when_creating_duplicate_question(
    api_client: AsyncClient,
    question_service_override: QuestionServiceOverride,
) -> None:
    topic = make_topic()
    existing = make_question(topic_id=topic.id, question="What is the GIL?")
    _, uow = question_service_override(topics=[topic], questions=[existing])

    response = await api_client.post(
        "/api/questions",
        json={
            "topic_id": str(topic.id),
            "question": "  WHAT IS THE GIL?  ",
            "answer": "Something else",
            "difficulty": "easy",
        },
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"].startswith("Question '")
    assert uow.committed is False


async def test_returns_409_when_updating_to_existing_question_text(
    api_client: AsyncClient,
    question_service_override: QuestionServiceOverride,
) -> None:
    topic = make_topic()
    existing = make_question(topic_id=topic.id, question="What is the GIL?")
    other = make_question(topic_id=topic.id, question="What is asyncio?")
    _, uow = question_service_override(topics=[topic], questions=[existing, other])

    response = await api_client.patch(
        f"/api/questions/{other.id}", json={"question": existing.question}
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert other.question == "What is asyncio?"
    assert uow.committed is False


async def test_allows_same_question_text_in_another_topic(
    api_client: AsyncClient,
    question_service_override: QuestionServiceOverride,
) -> None:
    first = make_topic(name="Python", slug="python")
    second = make_topic(name="SQL", slug="sql")
    existing = make_question(topic_id=first.id, question="What is an index?")
    question_service_override(topics=[first, second], questions=[existing])

    response = await api_client.post(
        "/api/questions",
        json={
            "topic_id": str(second.id),
            "question": existing.question,
            "answer": "Some answer",
            "difficulty": "medium",
        },
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["topic_id"] == str(second.id)
