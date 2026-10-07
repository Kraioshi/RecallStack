from uuid import uuid4

from fastapi import status
from httpx import AsyncClient

from app.core.enums.question import QuestionDifficulty
from tests.api.types import QuestionServiceOverride
from tests.unit.factories import make_question, make_topic


class TestGetRandom:
    async def test_returns_random_question(
        self,
        api_client: AsyncClient,
        question_service_override: QuestionServiceOverride,
    ) -> None:
        # Arrange
        question = make_question()

        question_service_override(
            questions=[question],
        )

        # Act
        response = await api_client.get("/api/questions/random")

        # Assert
        assert response.status_code == status.HTTP_200_OK

        body = response.json()

        assert body["id"] == str(question.id)
        assert body["topic_id"] == str(question.topic_id)
        assert body["question"] == question.question
        assert body["answer"] == question.answer
        assert body["difficulty"] == question.difficulty.value

    async def test_maps_query_parameters_to_selection_criteria(
        self,
        api_client: AsyncClient,
        question_service_override: QuestionServiceOverride,
    ) -> None:
        # Arrange
        topic = make_topic()
        question = make_question(topic_id=topic.id)
        excluded_question_id = uuid4()

        _, uow = question_service_override(
            topics=[topic],
            questions=[question],
        )

        # Act
        response = await api_client.get(
            "/api/questions/random",
            params={
                "topic_id": str(topic.id),
                "difficulty": QuestionDifficulty.HARD.value,
                "include_descendants": "true",
                "exclude_id": str(excluded_question_id),
            },
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK

        criteria = uow.fake_questions.last_random_criteria

        assert criteria is not None
        assert criteria.topic_id == topic.id
        assert criteria.difficulty == QuestionDifficulty.HARD
        assert criteria.include_descendants is True
        assert criteria.exclude_id == excluded_question_id

    async def test_uses_default_query_values(
        self,
        api_client: AsyncClient,
        question_service_override: QuestionServiceOverride,
    ) -> None:
        # Arrange
        question = make_question()

        _, uow = question_service_override(
            questions=[question],
        )

        # Act
        response = await api_client.get("/api/questions/random")

        # Assert
        assert response.status_code == status.HTTP_200_OK

        criteria = uow.fake_questions.last_random_criteria

        assert criteria is not None
        assert criteria.topic_id is None
        assert criteria.difficulty is None
        assert criteria.exclude_id is None
        assert criteria.include_descendants is False

    async def test_returns_404_when_topic_does_not_exist(
        self,
        api_client: AsyncClient,
        question_service_override: QuestionServiceOverride,
    ) -> None:
        # Arrange
        topic_id = uuid4()

        question_service_override()

        # Act
        response = await api_client.get(
            "/api/questions/random",
            params={
                "topic_id": str(topic_id),
            },
        )

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {
            "detail": f"Topic '{topic_id}' was not found.",
        }

    async def test_returns_404_when_no_question_matches(
        self,
        api_client: AsyncClient,
        question_service_override: QuestionServiceOverride,
    ) -> None:
        # Arrange
        question_service_override()

        # Act
        response = await api_client.get(
            "/api/questions/random",
            params={
                "difficulty": QuestionDifficulty.HARD,
            },
        )

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {
            "detail": "No question matches the requested criteria.",
        }

    async def test_returns_422_when_difficulty_is_invalid(
        self,
        api_client: AsyncClient,
        question_service_override: QuestionServiceOverride,
    ) -> None:
        # Arrange
        question_service_override()

        # Act
        response = await api_client.get(
            "/api/questions/random",
            params={
                "difficulty": "legendary",
            },
        )

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    async def test_returns_422_when_topic_id_is_invalid(
        self,
        api_client: AsyncClient,
        question_service_override: QuestionServiceOverride,
    ) -> None:
        # Arrange
        question_service_override()

        # Act
        response = await api_client.get(
            "/api/questions/random",
            params={
                "topic_id": "not-a-valid-uuid",
            },
        )

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    async def test_returns_422_when_exclude_id_is_invalid(
        self,
        api_client: AsyncClient,
        question_service_override: QuestionServiceOverride,
    ) -> None:
        # Arrange
        question_service_override()

        # Act
        response = await api_client.get(
            "/api/questions/random",
            params={
                "exclude_id": "not-a-valid-uuid",
            },
        )

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
