from uuid import UUID

from app.models.topic import Topic

type TopicsByParent = dict[UUID | None, list[Topic]]
type TopicsById = dict[UUID, Topic]
