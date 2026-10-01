from uuid import UUID

from fastapi import APIRouter

from app.api.dependencies.services import TopicServiceDep
from app.api.topics.schemas.response import TopicResponse

router = APIRouter(
    prefix="/topics",
    tags=["topics"],
)


@router.get(
    "/{topic_id}",
    response_model=TopicResponse,
)
async def get_topic(
    topic_id: UUID,
    service: TopicServiceDep,
) -> TopicResponse:
    topic = await service.get_topic(topic_id)

    return TopicResponse.model_validate(topic)
