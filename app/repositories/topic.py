from typing import Protocol
from uuid import UUID

from app.models.topic import Topic


class TopicRepository(Protocol):
    """
    Persistence contract for topics.

    Protocol instead of ABC is used to keep repository implementations
    structurally typed: an implementation satisfies this contract by
    providing the required methods, without explicit inheritance.

    This keeps the service layer dependent on the repository contract
    instead of a specific persistence implementation.
    """

    async def get_by_id(self, topic_id: UUID) -> Topic | None: ...

    async def get_roots(self) -> list[Topic]: ...

    async def get_children(self, parent_id: UUID) -> list[Topic]: ...

    async def add(self, topic: Topic) -> Topic: ...

    async def get_by_slug(self, slug: str, parent_id: UUID | None) -> Topic | None: ...
