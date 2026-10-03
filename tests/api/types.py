from typing import Protocol

from app.models.question import Question
from app.models.topic import Topic
from app.services.question import QuestionService
from tests.unit.test_doubles.unit_of_work import FakeUnitOfWork


class QuestionServiceOverride(Protocol):
    def __call__(
        self,
        topics: list[Topic] | None = None,
        questions: list[Question] | None = None,
    ) -> tuple[QuestionService, FakeUnitOfWork]: ...
