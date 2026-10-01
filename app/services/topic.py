from uuid import UUID

from app.core.dto.topic import CreateTopicData, TopicData, UpdateTopicData
from app.core.exceptions.topic import TopicNotFoundError, TopicSlugAlreadyExistsError
from app.core.types import UNSET
from app.models.topic import Topic
from app.unit_of_work.base import UnitOfWork


class TopicService:
    """Service fr app level operations for topics."""

    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def get_topic(self, topic_id: UUID) -> TopicData:
        """Return a topic or raise if it does not exist."""

        async with self._uow:
            topic = await self._get_topic_or_raise(topic_id)
            return self._to_topic_data(topic)

    async def list_root_topics(self) -> list[TopicData]:
        """Return all root-level topics."""

        async with self._uow:
            roots = await self._uow.topics.get_roots()
            return [self._to_topic_data(root) for root in roots]

    async def list_children(
        self,
        parent_id: UUID,
    ) -> list[TopicData]:
        """Return direct children of a topic or raise if the parent does not exist."""

        async with self._uow:
            await self._get_topic_or_raise(parent_id)

            children = await self._uow.topics.get_children(parent_id)

            return [self._to_topic_data(child) for child in children]

    async def create_topic(self, data: CreateTopicData) -> TopicData:
        """Create a topic after validating its parent and sibling slug."""

        async with self._uow:
            await self._ensure_parent_exists(data)
            await self._ensure_sibling_slug_is_available(
                slug=data.slug, parent_id=data.parent_id
            )

            entity = self._to_topic_model(data)
            created = await self._uow.topics.add(entity)

            await self._uow.commit()

            return self._to_topic_data(created)

    async def update_topic(
        self,
        topic_id: UUID,
        data: UpdateTopicData,
    ) -> TopicData:
        """Update a topic or raise if it doesn't exist."""

        async with self._uow:
            topic = await self._get_topic_or_raise(topic_id)

            if data.slug is not UNSET and data.slug != topic.slug:
                await self._ensure_sibling_slug_is_available(
                    slug=data.slug,
                    parent_id=topic.parent_id,
                )

            self._apply_updates(topic, data)

            await self._uow.commit()

            return self._to_topic_data(topic)

    async def _get_topic_or_raise(
        self,
        topic_id: UUID,
    ) -> Topic:
        topic = await self._uow.topics.get_by_id(topic_id)

        if topic is None:
            raise TopicNotFoundError(topic_id)

        return topic

    async def _ensure_parent_exists(self, data: CreateTopicData) -> None:
        if data.parent_id is not None:
            await self._get_topic_or_raise(data.parent_id)

    async def _ensure_sibling_slug_is_available(
        self,
        slug: str,
        parent_id: UUID | None,
    ) -> None:
        existing = await self._uow.topics.get_by_slug(
            slug=slug,
            parent_id=parent_id,
        )

        if existing is not None:
            raise TopicSlugAlreadyExistsError(
                slug=slug,
                parent_id=parent_id,
            )

    @staticmethod
    def _apply_updates(
        topic: Topic,
        data: UpdateTopicData,
    ) -> None:
        if data.name is not UNSET:
            topic.name = data.name

        if data.slug is not UNSET:
            topic.slug = data.slug

        if data.description is not UNSET:
            topic.description = data.description

    @staticmethod
    def _to_topic_data(topic: Topic) -> TopicData:
        return TopicData(
            id=topic.id,
            parent_id=topic.parent_id,
            name=topic.name,
            slug=topic.slug,
            description=topic.description,
            created_at=topic.created_at,
            updated_at=topic.updated_at,
        )

    @staticmethod
    def _to_topic_model(data: CreateTopicData) -> Topic:
        return Topic(
            name=data.name,
            slug=data.slug,
            description=data.description,
            parent_id=data.parent_id,
        )
