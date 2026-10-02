from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Path

from app.api.dependencies.services import TopicServiceDep
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

    return TopicResponse.model_validate(topic)
