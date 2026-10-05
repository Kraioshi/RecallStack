from typing import Protocol
from uuid import UUID

from app.models.question import Question


class QuestionRepository(Protocol):
    """
    Persistence contract for questions.

    Protocol instead of ABC is used to keep repository implementations
    structurally typed: an implementation satisfies this contract by
    providing the required methods, without explicit inheritance.

    This keeps the service layer dependent on the repository contract
    instead of a specific persistence implementation.
    """

    async def get_by_id(self, question_id: UUID) -> Question | None: ...

    async def get_by_topic_id(self, topic_id: UUID) -> list[Question]: ...

    async def add(self, question: Question) -> Question: ...

    async def delete(self, question: Question) -> None: ...

    async def count_by_topic(self) -> dict[UUID, int]: ...
