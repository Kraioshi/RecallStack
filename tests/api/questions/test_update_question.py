from uuid import uuid4

import pytest
from fastapi import status
from httpx import AsyncClient

from app.core.enums.question import QuestionDifficulty
from tests.api.types import QuestionServiceOverride
from tests.unit.factories import make_question, make_topic


async def test_updates_question_partially(
    api_client: AsyncClient,
    question_service_override: QuestionServiceOverride,
) -> None:
    # Arrange
    topic = make_topic()
    question = make_question(topic_id=topic.id)

    original_answer = question.answer
    original_difficulty = question.difficulty

    question_service_override(
        topics=[topic],
        questions=[question],
    )

    payload = {
        "question": "Why am I even writing API tests?",
    }

    # Act
    response = await api_client.patch(
        f"/api/questions/{question.id}",
        json=payload,
    )

    # Assert
    assert response.status_code == status.HTTP_200_OK

    body = response.json()

    assert body["id"] == str(question.id)
    assert body["topic_id"] == str(topic.id)
    assert body["question"] == payload["question"]
    assert body["answer"] == original_answer
    assert body["difficulty"] == original_difficulty.value


async def test_updates_multiple_question_fields(
    api_client: AsyncClient,
    question_service_override: QuestionServiceOverride,
) -> None:
    # Arrange
    topic = make_topic()
    question = make_question(topic_id=topic.id)

    question_service_override(
        topics=[topic],
        questions=[question],
    )

    payload = {
        "question": "What does the GIL actually do?",
        "answer": "It restricts execution of Python bytecode to one thread at a time.",
        "difficulty": "hard",
    }

    # Act
    response = await api_client.patch(
        f"/api/questions/{question.id}",
        json=payload,
    )

    # Assert
    assert response.status_code == status.HTTP_200_OK

    body = response.json()

    assert body["question"] == payload["question"]
    assert body["answer"] == payload["answer"]
    assert body["difficulty"] == payload["difficulty"]
    assert body["topic_id"] == str(topic.id)


async def test_moves_question_to_another_topic(
    api_client: AsyncClient,
    question_service_override: QuestionServiceOverride,
) -> None:
    # Arrange
    original_topic = make_topic(
        name="Python",
        slug="python",
    )
    new_topic = make_topic(
        name="Concurrency",
        slug="concurrency",
    )

    question = make_question(
        topic_id=original_topic.id,
    )

    question_service_override(
        topics=[original_topic, new_topic],
        questions=[question],
    )

    payload = {
        "topic_id": str(new_topic.id),
    }

    # Act
    response = await api_client.patch(
        f"/api/questions/{question.id}",
        json=payload,
    )

    # Assert
    assert response.status_code == status.HTTP_200_OK

    body = response.json()

    assert body["id"] == str(question.id)
    assert body["topic_id"] == str(new_topic.id)


async def test_returns_404_when_question_does_not_exist(
    api_client: AsyncClient,
    question_service_override: QuestionServiceOverride,
) -> None:
    # Arrange
    question_id = uuid4()

    question_service_override()

    payload = {
        "question": "Updated question",
    }

    # Act
    response = await api_client.patch(
        f"/api/questions/{question_id}",
        json=payload,
    )

    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": f"Question '{question_id}' was not found."}


async def test_returns_404_when_destination_topic_does_not_exist(
    api_client: AsyncClient,
    question_service_override: QuestionServiceOverride,
) -> None:
    # Arrange
    question = make_question()
    missing_topic_id = uuid4()

    question_service_override(
        questions=[question],
    )

    payload = {
        "topic_id": str(missing_topic_id),
    }

    # Act
    response = await api_client.patch(
        f"/api/questions/{question.id}",
        json=payload,
    )

    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": f"Topic '{missing_topic_id}' was not found."}


async def test_returns_422_when_request_body_is_empty(
    api_client: AsyncClient,
    question_service_override: QuestionServiceOverride,
) -> None:
    # Arrange
    question = make_question()

    question_service_override(
        questions=[question],
    )

    # Act
    response = await api_client.patch(
        f"/api/questions/{question.id}",
        json={},
    )

    # Assert
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


@pytest.mark.parametrize(
    "payload",
    [
        {"topic_id": None},
        {"question": None},
        {"answer": None},
        {"difficulty": None},
    ],
)
async def test_returns_422_when_field_is_explicitly_null(
    api_client: AsyncClient,
    question_service_override: QuestionServiceOverride,
    payload: dict[str, object],
) -> None:
    # Arrange
    question = make_question()

    question_service_override(
        questions=[question],
    )

    # Act
    response = await api_client.patch(
        f"/api/questions/{question.id}",
        json=payload,
    )

    # Assert
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_returns_422_when_difficulty_is_invalid(
    api_client: AsyncClient,
    question_service_override: QuestionServiceOverride,
) -> None:
    # Arrange
    question = make_question()

    question_service_override(
        questions=[question],
    )

    payload = {
        "difficulty": "legendary",
    }

    # Act
    response = await api_client.patch(
        f"/api/questions/{question.id}",
        json=payload,
    )

    # Assert
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_returns_422_when_question_id_is_invalid(
    api_client: AsyncClient,
    question_service_override: QuestionServiceOverride,
) -> None:
    # Arrange
    question_service_override()

    payload = {
        "difficulty": QuestionDifficulty.HARD.value,
    }

    # Act
    response = await api_client.patch(
        "/api/questions/not-a-valid-uuid",
        json=payload,
    )

    # Assert
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
