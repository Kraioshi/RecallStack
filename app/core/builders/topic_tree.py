from uuid import UUID

from app.core.dto.topic import TopicTreeData
from app.models.topic import Topic


class TopicTreeBuilder:
    """Build a hierarchical topic tree from a flat collection of topics."""

    def build(self, topics: list[Topic]) -> list[TopicTreeData]:
        children_by_parent: dict[UUID | None, list[Topic]] = {}

        for topic in topics:
            children_by_parent.setdefault(topic.parent_id, []).append(topic)

        roots = children_by_parent.get(None, [])

        return [self._build_node(root, children_by_parent) for root in roots]

    def _build_node(
        self,
        topic: Topic,
        children_by_parent: dict[UUID | None, list[Topic]],
    ) -> TopicTreeData:
        children = children_by_parent.get(topic.id, [])

        return TopicTreeData(
            id=topic.id,
            name=topic.name,
            slug=topic.slug,
            description=topic.description,
            children=tuple(
                self._build_node(child, children_by_parent) for child in children
            ),
        )
