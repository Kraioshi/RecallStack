from types import TracebackType
from typing import Protocol, Self

from app.repositories.question import QuestionRepository
from app.repositories.topic import TopicRepository


class UnitOfWork(Protocol):
    """
    Group repositories working on one transaction.

    Services should know nothing about AsyncSession or SQLAlchemy.
    Services should use the Unit Of Work instead of working with DB session directly.
    This keeps transaction management outside service layer and
    allows several repository operations succeed or fail as one unit.

    Concrete implementations are responsible for handling transaction lifecycle.
    Service only decides when the work should be committed or rolled back.
    """

    topics: TopicRepository
    questions: QuestionRepository

    async def __aenter__(self) -> Self:
        """Enter UoW and prepare its transaction resources."""
        ...

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Exit UoW and safely cleanup transaction resources."""
        ...

    async def commit(self) -> None: ...

    async def rollback(self) -> None: ...
