from uuid import uuid4

from fastapi import status
from httpx import AsyncClient

from tests.api.types import QuestionServiceOverride
from tests.unit.factories import make_topic


async def test_creates_question(
    api_client: AsyncClient,
    question_service_override: QuestionServiceOverride,
) -> None:
    # Arrange
    topic = make_topic()

    question_service_override(
        topics=[topic],
    )

    payload = {
        "topic_id": str(topic.id),
        "question": "What is the GIL?",
        "answer": "Global Interpreter Lock.",
        "difficulty": "medium",
    }

    # Act
    response = await api_client.post(
        "/api/questions",
        json=payload,
    )

    # Assert
    assert response.status_code == status.HTTP_201_CREATED

    body = response.json()

    assert body["id"] is not None
    assert body["topic_id"] == str(topic.id)
    assert body["question"] == payload["question"]
    assert body["answer"] == payload["answer"]
    assert body["difficulty"] == payload["difficulty"]
    assert body["created_at"] is not None
    assert body["updated_at"] is not None


async def test_returns_404_when_topic_does_not_exist(
    api_client: AsyncClient,
    question_service_override: QuestionServiceOverride,
) -> None:
    # Arrange
    topic_id = uuid4()

    question_service_override()

    payload = {
        "topic_id": str(topic_id),
        "question": "What is the GIL?",
        "answer": "Global Interpreter Lock.",
        "difficulty": "medium",
    }

    # Act
    response = await api_client.post(
        "/api/questions",
        json=payload,
    )

    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": f"Topic '{topic_id}' was not found."}


async def test_returns_422_when_question_is_empty(
    api_client: AsyncClient,
    question_service_override: QuestionServiceOverride,
) -> None:
    # Arrange
    topic = make_topic()

    question_service_override(
        topics=[topic],
    )

    payload = {
        "topic_id": str(topic.id),
        "question": "",
        "answer": "Global Interpreter Lock.",
        "difficulty": "medium",
    }

    # Act
    response = await api_client.post(
        "/api/questions",
        json=payload,
    )

    # Assert
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_returns_422_when_answer_is_empty(
    api_client: AsyncClient,
    question_service_override: QuestionServiceOverride,
) -> None:
    # Arrange
    topic = make_topic()

    question_service_override(
        topics=[topic],
    )

    payload = {
        "topic_id": str(topic.id),
        "question": "What is the GIL?",
        "answer": "",
        "difficulty": "medium",
    }

    # Act
    response = await api_client.post(
        "/api/questions",
        json=payload,
    )

    # Assert
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_returns_422_when_difficulty_is_invalid(
    api_client: AsyncClient,
    question_service_override: QuestionServiceOverride,
) -> None:
    # Arrange
    topic = make_topic()

    question_service_override(
        topics=[topic],
    )

    payload = {
        "topic_id": str(topic.id),
        "question": "What is the GIL?",
        "answer": "Global Interpreter Lock.",
        "difficulty": "legendary",
    }

    # Act
    response = await api_client.post(
        "/api/questions",
        json=payload,
    )

    # Assert
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_returns_422_when_topic_id_is_invalid(
    api_client: AsyncClient,
    question_service_override: QuestionServiceOverride,
) -> None:
    # Arrange
    question_service_override()

    payload = {
        "topic_id": "not-a-valid-uuid",
        "question": "What is the GIL?",
        "answer": "Global Interpreter Lock.",
        "difficulty": "medium",
    }

    # Act
    response = await api_client.post(
        "/api/questions",
        json=payload,
    )

    # Assert
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_returns_422_when_required_field_is_missing(
    api_client: AsyncClient,
    question_service_override: QuestionServiceOverride,
) -> None:
    # Arrange
    topic = make_topic()

    question_service_override(
        topics=[topic],
    )

    payload = {
        "topic_id": str(topic.id),
        "question": "What is the GIL?",
        # answer deliberately omitted
        "difficulty": "medium",
    }

    # Act
    response = await api_client.post(
        "/api/questions",
        json=payload,
    )

    # Assert
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
