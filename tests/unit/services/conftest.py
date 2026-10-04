from typing import Protocol

import pytest

from app.core.builders.topic_tree import TopicTreeBuilder
from app.models import Question
from app.models.topic import Topic
from app.services.question import QuestionService
from app.services.topic import TopicService
from tests.unit.test_doubles.repositories import (
    FakeQuestionRepository,
    FakeTopicRepository,
)
from tests.unit.test_doubles.unit_of_work import FakeUnitOfWork


class TopicServiceFactory(Protocol):
    def __call__(
        self,
        topics: list[Topic] | None = None,
    ) -> tuple[TopicService, FakeUnitOfWork]: ...


@pytest.fixture
def topic_service_factory() -> TopicServiceFactory:
    """Build a TopicService with an in-memory repository and fake UoW."""

    def create_service(
        topics: list[Topic] | None = None,
    ) -> tuple[TopicService, FakeUnitOfWork]:
        topic_repository = FakeTopicRepository(topics)
        question_repository = FakeQuestionRepository()

        uow = FakeUnitOfWork(
            topics=topic_repository,
            questions=question_repository,
        )

        service = TopicService(
            uow=uow,
            tree_builder=TopicTreeBuilder(),
        )

        return service, uow

    return create_service


class QuestionServiceFactory(Protocol):
    def __call__(
        self,
        topics: list[Topic] | None = None,
        questions: list[Question] | None = None,
    ) -> tuple[QuestionService, FakeUnitOfWork]: ...


@pytest.fixture
def question_service_factory() -> QuestionServiceFactory:
    def create_service(
        topics: list[Topic] | None = None,
        questions: list[Question] | None = None,
    ) -> tuple[QuestionService, FakeUnitOfWork]:
        topic_repository = FakeTopicRepository(topics)
        question_repository = FakeQuestionRepository(questions)

        uow = FakeUnitOfWork(
            topics=topic_repository,
            questions=question_repository,
        )

        service = QuestionService(uow)

        return service, uow

    return create_service
