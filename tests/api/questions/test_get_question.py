from uuid import uuid4

from httpx import AsyncClient
from starlette import status

from tests.api.conftest import QuestionServiceOverride
from tests.unit.factories import make_question, make_topic


async def test_returns_existing_question(
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

    # Act
    response = await api_client.get(f"/api/questions/{question.id}")

    # Assert
    assert response.status_code == status.HTTP_200_OK

    body = response.json()

    assert body["id"] == str(question.id)
    assert body["topic_id"] == str(topic.id)
    assert body["question"] == question.question
    assert body["answer"] == question.answer
    assert body["difficulty"] == question.difficulty.value


async def test_returns_404_when_question_does_not_exist(
    api_client: AsyncClient,
    question_service_override: QuestionServiceOverride,
) -> None:
    # Arrange
    question_id = uuid4()

    question_service_override()

    # Act
    response = await api_client.get(f"/api/questions/{question_id}")

    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND
    body = response.json()
    assert body["detail"] == f"Question '{question_id}' was not found."


async def test_returns_422_when_question_id_is_invalid(
    api_client: AsyncClient,
    question_service_override: QuestionServiceOverride,
) -> None:
    # Arrange
    question_service_override()

    # Act
    response = await api_client.get("/api/questions/not-a-valid-uuid")

    # Assert
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
