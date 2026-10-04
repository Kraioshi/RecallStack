from fastapi import APIRouter, status

from app.api.dependencies.services import TopicServiceDep

# Import mapper module as a namespace to keep mapping calls explicit
# without adding a stateless class.
from app.api.topics import mappers as topic_mapper
from app.api.topics.params import TopicIdPath
from app.api.topics.schemas.request import CreateTopicRequest, UpdateTopicRequest
from app.api.topics.schemas.response import TopicResponse, TopicTreeResponse

router = APIRouter(
    prefix="/topics",
    tags=["topics"],
)


# Topic collection
@router.get(
    "",
    response_model=list[TopicResponse],
    summary="List root topics",
    response_description="The root-level topics.",
)
async def list_root_topics(
    service: TopicServiceDep,
) -> list[TopicResponse]:
    """Retrieve all root-level topics."""
    topics = await service.list_root_topics()

    return topic_mapper.to_topic_responses(topics)


@router.get(
    "/tree",
    response_model=list[TopicTreeResponse],
    summary="Get full topic tree",
    response_description="Complete hierarchical topic tree",
)
async def get_topic_tree(
    service: TopicServiceDep,
) -> list[TopicTreeResponse]:
    tree = await service.get_tree()

    return topic_mapper.to_topic_tree_responses(tree)


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


# Single topic
@router.get(
    "/{topic_id}",
    response_model=TopicResponse,
    summary="Get a topic",
    response_description="The requested topic.",
    responses={
        404: {
            "description": "Topic not found.",
        },
    },
)
async def get_topic(
    topic_id: TopicIdPath,
    service: TopicServiceDep,
) -> TopicResponse:
    """Retrieve a single topic by its unique identifier."""
    topic = await service.get_topic(topic_id)

    return topic_mapper.to_topic_response(topic)


@router.get(
    "/{topic_id}/children",
    response_model=list[TopicResponse],
    summary="List topic children",
    response_description="The direct child topics.",
    responses={
        404: {
            "description": "Parent topic not found.",
        },
    },
)
async def list_topic_children(
    topic_id: TopicIdPath,
    service: TopicServiceDep,
) -> list[TopicResponse]:
    """Retrieve the direct children of a topic."""
    topics = await service.list_children(topic_id)

    return topic_mapper.to_topic_responses(topics)


@router.patch(
    "/{topic_id}",
    response_model=TopicResponse,
    summary="Update a topic",
    response_description="The updated topic.",
    responses={
        404: {
            "description": "Topic not found.",
        },
        409: {
            "description": "A topic with this slug already exists under same parent.",
        },
    },
)
async def update_topic(
    topic_id: TopicIdPath,
    request: UpdateTopicRequest,
    service: TopicServiceDep,
) -> TopicResponse:
    """Partially update an existing topic."""
    data = topic_mapper.to_update_topic_data(request)

    topic = await service.update_topic(topic_id, data)

    return topic_mapper.to_topic_response(topic)


@router.delete(
    "/{topic_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a topic",
    responses={
        404: {
            "description": "Topic not found.",
        },
        409: {
            "description": "Topic has children and cannot be deleted.",
        },
    },
)
async def delete_topic(
    topic_id: TopicIdPath,
    service: TopicServiceDep,
) -> None:
    await service.delete_topic(topic_id)
