from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Path
from starlette import status

from app.api.dependencies.services import TopicServiceDep

# Import mapper module as a namespace to keep mapping calls explicit
# without adding a stateless class
from app.api.topics import mappers as topic_mapper
from app.api.topics.schemas.request import CreateTopicRequest
from app.api.topics.schemas.response import TopicResponse

router = APIRouter(
    prefix="/topics",
    tags=["topics"],
)


@router.get(
    "/{topic_id}",
    response_model=TopicResponse,
    summary="Get a topic",
    response_description="The requested topic.",
    operation_id="get_topic",
    responses={
        404: {
            "description": "Topic not found.",
        },
    },
)
async def get_topic(
    topic_id: Annotated[
        UUID,
        Path(
            description="Unique identifier of the topic.",
        ),
    ],
    service: TopicServiceDep,
) -> TopicResponse:
    """
    Retrieve a single topic by its unique identifier.
    """
    topic = await service.get_topic(topic_id)

    return topic_mapper.to_topic_response(topic)


@router.post(
    "",
    response_model=TopicResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a topic",
    response_description="The newly created topic.",
    responses={
        404: {
            "description": "Parent topic not found.",
        },
        409: {
            "description": "A topic with this slug already exists under same parent.",
        },
    },
)
async def create_topic(
    request: CreateTopicRequest,
    service: TopicServiceDep,
) -> TopicResponse:
    data = topic_mapper.to_create_topic_data(request)
    topic = await service.create_topic(data)

    return topic_mapper.to_topic_response(topic)
