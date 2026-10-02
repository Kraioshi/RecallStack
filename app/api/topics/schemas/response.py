from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


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
