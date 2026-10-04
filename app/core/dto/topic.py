from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.core.types import UNSET, _UnsetType


@dataclass(frozen=True, slots=True)
class CreateTopicData:
    """Application input for creating a topic."""

    name: str
    slug: str
    description: str | None = None
    parent_id: UUID | None = None


@dataclass(frozen=True, slots=True)
class UpdateTopicData:
    """Application input for updating a topic."""

    name: str | _UnsetType = UNSET
    slug: str | _UnsetType = UNSET
    description: str | None | _UnsetType = UNSET


@dataclass(frozen=True, slots=True)
class TopicData:
    """Application-level representation of a topic."""

    id: UUID
    parent_id: UUID | None
    name: str
    slug: str
    description: str | None
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True, slots=True)
class TopicTreeData:
    id: UUID
    name: str
    slug: str
    description: str | None
    children: tuple["TopicTreeData", ...] = ()
