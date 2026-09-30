from typing import Protocol

from app.repositories.topic import TopicRepository


class UnitOfWork(Protocol):
    """
    Group repositories working on one transaction.

    Services should know nothing about AsyncSession or SQLAlchemy.
    Services should use the Unit Of Work instead of working with DB session directly.
    This keeps transaction management outside service layer and
    allows several repository operation succeed or fail as one unit.

    Concrete implementations are responsible for handling transaction lifecycle.
    Service only decides when the work should be commited or rolled back.
    """

    topics: TopicRepository

    async def commit(self) -> None: ...

    async def rollback(self) -> None: ...
