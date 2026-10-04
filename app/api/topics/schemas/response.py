from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TopicResponse(BaseModel):
    """HTTP response representation of a topic."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    parent_id: UUID | None
    name: str
    slug: str
    description: str | None
    created_at: datetime
    updated_at: datetime


class TopicTreeResponse(BaseModel):
    """HTTPS response representation of the tree of topics."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    slug: str
    description: str | None
    children: list["TopicTreeResponse"] = Field(default_factory=list)
