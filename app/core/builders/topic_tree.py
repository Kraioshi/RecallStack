from uuid import UUID

from app.core.dto.topic import TopicTreeData
from app.models.topic import Topic


class TopicTreeBuilder:
    """
    Build a hierarchical topic tree from a flat list of topics.

    Topics are grouped by `parent_id`.
    Root topics are the ones with  `parent_id=None`.
    From there, child topics are added recursively.

    Question counts are passed in separately. Each count represents the
    number of questions directly assigned to a topic. If a topic is missing
    from the count mapping, its question count is treated as zero.

    The builder does not access the database. It only works with data that
    has already been loaded and returns ``TopicTreeData`` objects.

    Example:

        Root
        └── Gen-one-child
            └── Gen-two-child
                ├── Gen-three-child
                └── Gen-three-child
    """

    def build(
        self,
        topics: list[Topic],
        question_counts: dict[UUID, int],
    ) -> list[TopicTreeData]:
        """Return complete topic trees rooted at topics without a parent."""
        children_by_parent: dict[UUID | None, list[Topic]] = {}

        for topic in topics:
            children_by_parent.setdefault(topic.parent_id, []).append(topic)

        roots = children_by_parent.get(None, [])

        return [
            self._build_node(
                root,
                children_by_parent,
                question_counts,
            )
            for root in roots
        ]

    def _build_node(
        self,
        topic: Topic,
        children_by_parent: dict[UUID | None, list[Topic]],
        question_counts: dict[UUID, int],
    ) -> TopicTreeData:
        """Recursively build a tree node and all of its descendants."""
        children = children_by_parent.get(topic.id, [])

        return TopicTreeData(
            id=topic.id,
            name=topic.name,
            slug=topic.slug,
            description=topic.description,
            question_count=question_counts.get(topic.id, 0),
            children=tuple(
                self._build_node(
                    child,
                    children_by_parent,
                    question_counts,
                )
                for child in children
            ),
        )
