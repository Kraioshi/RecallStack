from uuid import UUID

from app.core.dto.topic import TopicQuestionCountData, TopicTreeData
from app.core.enums.question import QuestionDifficulty
from app.core.types.question import TopicDifficultyCounts
from app.core.types.topic import TopicsByParent
from app.models.topic import Topic


class TopicTreeBuilder:
    """
    Build a hierarchical topic tree from a flat list of topics.

    Topics are grouped by `parent_id`.
    Root topics are the ones with  `parent_id=None`.
    From there, child topics are added recursively.

    Question counts are passed in separately.
    Counts are grouped by topic and difficulty.
    Missing topics or difficulties are treated as zero.

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
        question_counts: TopicDifficultyCounts,
    ) -> list[TopicTreeData]:
        """Build complete trees starting from all root topics."""
        children_by_parent: TopicsByParent = {}

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
        children_by_parent: TopicsByParent,
        question_counts: TopicDifficultyCounts,
    ) -> TopicTreeData:
        """Build one topic node and recursively build its children."""
        children = children_by_parent.get(topic.id, [])

        return TopicTreeData(
            id=topic.id,
            name=topic.name,
            slug=topic.slug,
            description=topic.description,
            question_counts=self._build_question_count_data(
                topic.id,
                question_counts,
            ),
            children=tuple(
                self._build_node(
                    child,
                    children_by_parent,
                    question_counts,
                )
                for child in children
            ),
        )

    @staticmethod
    def _build_question_count_data(
        topic_id: UUID,
        question_counts: TopicDifficultyCounts,
    ) -> TopicQuestionCountData:
        """Build question count data for a single topic."""
        topic_counts = question_counts.get(topic_id, {})

        easy = topic_counts.get(QuestionDifficulty.EASY, 0)
        medium = topic_counts.get(QuestionDifficulty.MEDIUM, 0)
        hard = topic_counts.get(QuestionDifficulty.HARD, 0)

        return TopicQuestionCountData(
            easy=easy,
            medium=medium,
            hard=hard,
            total=easy + medium + hard,
        )
