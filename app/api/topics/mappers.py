"""
Mapping helpers for Topics API layer.

Functions translate between HTTP-facing Pydantic schemas and app layer DTOs.

This allows:
- API schemas to remain simple validation/transport
- App DTOs to stay independent of Fastapi/Pydantic request models
- Routers to focus on HTTP orchestration without any data transformation
- API and app models change independently

Explicit mapping instead of `model_dump()` to avoid coupling models by field name.
"""

from app.api.topics.schemas.request import CreateTopicRequest
from app.api.topics.schemas.response import TopicResponse
from app.core.dto.topic import CreateTopicData, TopicData


def to_create_topic_data(
    request: CreateTopicRequest,
) -> CreateTopicData:
    """Map an HTTP create-topic request to the service input DTO."""
    return CreateTopicData(
        name=request.name,
        slug=request.slug,
        description=request.description,
        parent_id=request.parent_id,
    )


def to_topic_response(
    data: TopicData,
) -> TopicResponse:
    """Map application topic data to the public API response schema."""
    return TopicResponse.model_validate(data)
