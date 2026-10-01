from uuid import UUID, uuid4

from app.core.helpers.dates import now
from app.models.topic import Topic


def make_topic(
    *,
    name: str = "Python",
    slug: str = "python",
    topic_id: UUID | None = None,
    parent_id: UUID | None = None,
) -> Topic:
    current_time = now()

    return Topic(
        id=topic_id or uuid4(),
        name=name,
        slug=slug,
        parent_id=parent_id,
        created_at=current_time,
        updated_at=current_time,
    )
