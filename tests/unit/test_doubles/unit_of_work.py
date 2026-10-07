from types import TracebackType
from typing import Self

from app.repositories.question import QuestionRepository
from app.repositories.topic import TopicRepository
from tests.unit.test_doubles.repositories import (
    FakeQuestionRepository,
    FakeTopicRepository,
)


class FakeUnitOfWork:
    """In-memory UnitOfWork implementation for service unit tests.

    Tracks commit and rollback calls so tests can verify transactions
    without creating a real db session.
    """

    def __init__(
        self,
        topics: FakeTopicRepository,
        questions: FakeQuestionRepository,
    ) -> None:
        self.topics: TopicRepository = topics
        self.questions: QuestionRepository = questions

        # keep fake references for assertions
        self.fake_topics: FakeTopicRepository = topics
        self.fake_questions: FakeQuestionRepository = questions

        self.committed = False
        self.rolled_back = False
        self.entered = False
        self.exited = False

    async def __aenter__(self) -> Self:
        self.entered = True
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.exited = True

        if not self.committed:
            await self.rollback()

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        self.rolled_back = True
