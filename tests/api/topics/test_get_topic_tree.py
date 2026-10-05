from httpx import AsyncClient

from app.core.enums.question import QuestionDifficulty
from tests.api.types import TopicServiceOverride
from tests.unit.factories import make_question, make_topic


class TestGetTopicTree:
    async def test_returns_empty_topic_tree(
        self,
        api_client: AsyncClient,
        topic_service_override: TopicServiceOverride,
    ) -> None:
        topic_service_override()

        response = await api_client.get("/api/topics/tree")

        assert response.status_code == 200
        assert response.json() == []

    async def test_returns_nested_topic_tree_with_question_counts(
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
        sql = make_topic(
            name="SQL",
            slug="sql",
        )

        core_easy_1 = make_question(
            topic_id=core.id,
            difficulty=QuestionDifficulty.EASY,
        )
        core_easy_2 = make_question(
            topic_id=core.id,
            difficulty=QuestionDifficulty.EASY,
        )
        core_medium = make_question(
            topic_id=core.id,
            difficulty=QuestionDifficulty.MEDIUM,
        )
        core_hard = make_question(
            topic_id=core.id,
            difficulty=QuestionDifficulty.HARD,
        )
        routing_medium = make_question(
            topic_id=routing.id,
            difficulty=QuestionDifficulty.MEDIUM,
        )

        topic_service_override(
            topics=[
                python,
                frameworks,
                fastapi,
                core,
                routing,
                sql,
            ],
            questions=[
                core_easy_1,
                core_easy_2,
                core_medium,
                core_hard,
                routing_medium,
            ],
        )

        response = await api_client.get("/api/topics/tree")

        assert response.status_code == 200
        assert response.json() == [
            {
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
                                            "easy": 2,
                                            "medium": 1,
                                            "hard": 1,
                                            "total": 4,
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
                                            "medium": 1,
                                            "hard": 0,
                                            "total": 1,
                                        },
                                        "children": [],
                                    },
                                ],
                            }
                        ],
                    }
                ],
            },
            {
                "id": str(sql.id),
                "name": "SQL",
                "slug": "sql",
                "description": sql.description,
                "question_counts": {
                    "easy": 0,
                    "medium": 0,
                    "hard": 0,
                    "total": 0,
                },
                "children": [],
            },
        ]
