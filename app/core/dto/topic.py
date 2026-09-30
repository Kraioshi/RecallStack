from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class CreateTopicData:
    """Application input for creating a topic."""

    name: str
    slug: str
    parent_id: UUID | None = None
