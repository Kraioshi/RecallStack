from uuid import uuid4

from fastapi import status
from httpx import AsyncClient

from tests.api.types import QuestionServiceOverride
from tests.unit.factories import make_question


async def test_deletes_existing_question(
    api_client: AsyncClient,
    question_service_override: QuestionServiceOverride,
) -> None:
    # Arrange
    question = make_question()

    question_service_override(
        questions=[question],
    )

    # Act
    response = await api_client.delete(f"/api/questions/{question.id}")

    # Assert
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert response.content == b""


async def test_returns_404_when_question_does_not_exist(
    api_client: AsyncClient,
    question_service_override: QuestionServiceOverride,
) -> None:
    # Arrange
    question_id = uuid4()

    question_service_override()

    # Act
    response = await api_client.delete(f"/api/questions/{question_id}")

    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": f"Question '{question_id}' was not found."}


async def test_returns_422_when_question_id_is_invalid(
    api_client: AsyncClient,
    question_service_override: QuestionServiceOverride,
) -> None:
    # Arrange
    question_service_override()

    # Act
    response = await api_client.delete("/api/questions/not-a-valid-uuid")

    # Assert
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
