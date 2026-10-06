from uuid import uuid4

from httpx import AsyncClient

from app.core.enums.question import QuestionDifficulty
from tests.api.types import TopicServiceOverride
from tests.unit.factories import make_question, make_topic


class TestGetTopicContextTree:
    async def test_returns_topic_context_tree(
        self,
        api_client: AsyncClient,
        topic_service_override: TopicServiceOverride,
    ) -> None:
        python = make_topic(
            name="Python",
            slug="python",
        )
        frameworks = make_topic(
            name="Frameworks",
            slug="frameworks",
            parent_id=python.id,
        )
        django = make_topic(
            name="Django",
            slug="django",
            parent_id=frameworks.id,
        )
        fastapi = make_topic(
            name="FastAPI",
            slug="fastapi",
            parent_id=frameworks.id,
        )
        core = make_topic(
            name="Core Concepts",
            slug="core-concepts",
            parent_id=fastapi.id,
        )
        routing = make_topic(
            name="Routing",
            slug="routing",
            parent_id=fastapi.id,
        )

        core_easy = make_question(
            topic_id=core.id,
            difficulty=QuestionDifficulty.EASY,
        )
        core_hard = make_question(
            topic_id=core.id,
            difficulty=QuestionDifficulty.HARD,
        )

        topic_service_override(
            topics=[
                python,
                frameworks,
                django,
                fastapi,
                core,
                routing,
            ],
            questions=[
                core_easy,
                core_hard,
            ],
        )

        response = await api_client.get(
            f"/api/topics/{fastapi.id}/tree",
        )

        assert response.status_code == 200
        assert response.json() == {
            "id": str(python.id),
            "name": "Python",
            "slug": "python",
            "description": python.description,
            "question_counts": {
                "easy": 0,
                "medium": 0,
                "hard": 0,
                "total": 0,
            },
            "children": [
                {
                    "id": str(frameworks.id),
                    "name": "Frameworks",
                    "slug": "frameworks",
                    "description": frameworks.description,
                    "question_counts": {
                        "easy": 0,
                        "medium": 0,
                        "hard": 0,
                        "total": 0,
                    },
                    "children": [
                        {
                            "id": str(fastapi.id),
                            "name": "FastAPI",
                            "slug": "fastapi",
                            "description": fastapi.description,
                            "question_counts": {
                                "easy": 0,
                                "medium": 0,
                                "hard": 0,
                                "total": 0,
                            },
                            "children": [
                                {
                                    "id": str(core.id),
                                    "name": "Core Concepts",
                                    "slug": "core-concepts",
                                    "description": core.description,
                                    "question_counts": {
                                        "easy": 1,
                                        "medium": 0,
                                        "hard": 1,
                                        "total": 2,
                                    },
                                    "children": [],
                                },
                                {
                                    "id": str(routing.id),
                                    "name": "Routing",
                                    "slug": "routing",
                                    "description": routing.description,
                                    "question_counts": {
                                        "easy": 0,
                                        "medium": 0,
                                        "hard": 0,
                                        "total": 0,
                                    },
                                    "children": [],
                                },
                            ],
                        },
                    ],
                },
            ],
        }

    async def test_returns_404_when_topic_does_not_exist(
        self,
        api_client: AsyncClient,
        topic_service_override: TopicServiceOverride,
    ) -> None:
        topic_service_override()

        response = await api_client.get(
            f"/api/topics/{uuid4()}/tree",
        )

        assert response.status_code == 404
