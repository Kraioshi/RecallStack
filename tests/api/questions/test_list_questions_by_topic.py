from uuid import uuid4

from httpx import AsyncClient
from starlette import status

from tests.api.conftest import QuestionServiceOverride
from tests.unit.factories import make_question, make_topic


async def test_returns_existing_questions_by_topic(
    api_client: AsyncClient,
    question_service_override: QuestionServiceOverride,
) -> None:
    # Arrange
    topic = make_topic()
    side_topic = make_topic()

    question = make_question(topic_id=topic.id)
    side_question = make_question(topic_id=side_topic.id)

    question_service_override(
        topics=[topic, side_topic],
        questions=[question, side_question],
    )

    # Act
    response = await api_client.get(f"/api/questions?topic_id={topic.id}")

    # Assert
    assert response.status_code == status.HTTP_200_OK

    body = response.json()

    assert len(body) == 1
    assert body[0]["id"] == str(question.id)
    assert body[0]["topic_id"] == str(topic.id)


async def test_returns_empty_list_when_topic_has_no_questions(
    api_client: AsyncClient,
    question_service_override: QuestionServiceOverride,
) -> None:
    # Arrange
    topic = make_topic()

    question_service_override(
        topics=[topic],
    )

    # Act
    response = await api_client.get(f"/api/questions?topic_id={topic.id}")

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


async def test_returns_404_when_topic_does_not_exist(
    api_client: AsyncClient,
    question_service_override: QuestionServiceOverride,
) -> None:
    # Arrange
    topic_id = uuid4()

    question_service_override()

    # Act
    response = await api_client.get(f"/api/questions?topic_id={topic_id}")

    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": f"Topic '{topic_id}' was not found."}


async def test_returns_422_when_topic_id_is_missing(
    api_client: AsyncClient,
    question_service_override: QuestionServiceOverride,
) -> None:
    # Arrange
    question_service_override()

    # Act
    response = await api_client.get("/api/questions")

    # Assert
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_returns_422_when_topic_id_is_invalid(
    api_client: AsyncClient,
    question_service_override: QuestionServiceOverride,
) -> None:
    # Arrange
    question_service_override()

    # Act
    response = await api_client.get("/api/questions?topic_id=not-a-valid-uuid")

    # Assert
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
