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

from app.api.topics.schemas.request import CreateTopicRequest, UpdateTopicRequest
from app.api.topics.schemas.response import TopicResponse, TopicTreeResponse
from app.core.dto.topic import (
    CreateTopicData,
    TopicData,
    TopicTreeData,
    UpdateTopicData,
)
from app.core.types import UNSET


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


def to_topic_responses(
    data: list[TopicData],
) -> list[TopicResponse]:
    """Map application topic data to public API response schemas."""
    return [to_topic_response(topic) for topic in data]


def to_update_topic_data(
    request: UpdateTopicRequest,
) -> UpdateTopicData:
    """Map an HTTP update-topic request to the service input DTO."""
    fields = request.model_fields_set

    return UpdateTopicData(
        name=request.name if request.name is not None else UNSET,
        slug=request.slug if request.slug is not None else UNSET,
        description=request.description if "description" in fields else UNSET,
    )


def to_topic_tree_response(
    data: TopicTreeData,
) -> TopicTreeResponse:
    return TopicTreeResponse.model_validate(data)


def to_topic_tree_responses(
    data: list[TopicTreeData],
) -> list[TopicTreeResponse]:
    return [to_topic_tree_response(topic) for topic in data]
