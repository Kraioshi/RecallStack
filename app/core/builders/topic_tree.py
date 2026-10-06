from uuid import UUID

from app.core.dto.topic import TopicQuestionCountData, TopicTreeData
from app.core.enums.question import QuestionDifficulty
from app.core.types.question import TopicDifficultyCounts
from app.core.types.topic import TopicsById, TopicsByParent
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
        """
        Build one topic node and recursively build its children.

        This is the normal DOWNWARD recursion:

        topic
        ├── child
        │   └── grandchild
        └── child
        """
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

    def build_context_tree(
        self,
        topics: list[Topic],
        selected_topic_id: UUID,
        question_counts: TopicDifficultyCounts,
    ) -> TopicTreeData:
        """
        Build a context tree around one selected topic.

        The tree contains:

            1. The path from the root down to the selected topic.
            2. The complete subtree below the selected topic.
            3. No unrelated sibling branches above the selected topic.

        Example source tree:

            Absolute Root
            ├── Gen-One-Child-1
            ├── Gen-One-Child-2
            │   ├── Gen-Two-Child-1
            │   └── TARGET                  <- Hello, we are here
            │       ├── Gen-Three-Child-1
            │       └── Gen-Three-Child-2
            └── Gen-One-Child-3

        Result:

            Absolute Root
            └── Gen-One-Child-2
                └── TARGET
                    ├── Gen-Three-Child-1
                    └── Gen-Three-Child-2

        Siblings ABOVE the selected topic disappear
        Children BELOW the selected topic stay.
        """
        # We need to navigate this in two directions:
        #
        # 1. topics_by_id:
        #     child -> parent traversal
        #
        # 2. children_by_parent:
        #     parent -> children traversal
        #
        # Context-tree logic needs both because we go UP first,
        # then DOWN. Trees apparently weren't confusing enough already.
        topics_by_id, children_by_parent = self._build_topic_lookups(topics)

        selected_topic = topics_by_id[selected_topic_id]

        # Build the parent chain in ROOT -> SELECTED order:
        #
        #     Absolute Root -> Gen-One-Child-2 -> TARGET
        root_to_selected_path = self._build_root_to_selected_path(
            selected_topic,
            topics_by_id,
        )
        # Starting from the SELECTED topic, build its COMPLETE subtree normally.
        #     TARGET
        #     ├── Gen-Three-Child-1
        #     └── Gen-Three-Child-2
        #
        # Unlike the parents, all children are included.
        context_tree = self._build_node(
            selected_topic,
            children_by_parent,
            question_counts,
        )

        # TARGET is already sitting at the top of `context_tree`.
        #
        #     [Absolute Root, Gen-One-Child-2, TARGET]
        # BECOMES
        #     [Absolute Root, Gen-One-Child-2]
        #
        # Then we wrap the subtree from the inside out:
        #
        #     TARGET subtree
        #         ↓
        #     Gen-One-Child-2
        #     └── TARGET subtree
        #         ↓
        #     Absolute Root
        #     └── Gen-One-Child-2
        #         └── TARGET subtree
        final_tree = self._wrap_with_parents(
            context_tree,
            root_to_selected_path[:-1],
            question_counts,
        )

        # I am a smooth brain, so for debug purposes:
        # self._print_tree(final_tree)
        return final_tree

    @staticmethod
    def _build_question_count_data(
        topic_id: UUID,
        question_counts: TopicDifficultyCounts,
    ) -> TopicQuestionCountData:
        """
        Convert raw difficulty counts into the DTO used by tree nodes.

        Missing difficulty == zero questions, not an existential crisis.
        """
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

    @staticmethod
    def _build_topic_lookups(
        topics: list[Topic],
    ) -> tuple[TopicsById, TopicsByParent]:
        """
        Build two lookup tables so we to move around the hierarchy cheaply.

        `topics_by_id`:

            topic_id -> Topic

        Used when walking UP:
        child.parent_id -> parent topic

        `children_by_parent`:

            parent_id -> [children]

        Used when walking DOWN:
        parent -> all direct children
        """
        topics_by_id: dict[UUID, Topic] = {}
        children_by_parent: TopicsByParent = {}

        for topic in topics:
            topics_by_id[topic.id] = topic
            children_by_parent.setdefault(topic.parent_id, []).append(topic)

        return topics_by_id, children_by_parent

    @staticmethod
    def _build_root_to_selected_path(
        selected_topic: Topic,
        topics_by_id: TopicsById,
    ) -> list[Topic]:
        """
        Return the path from the root topic down to the selected topic.

        Starting at TARGET:

            TARGET
               ↑
            Gen-One-Child-2
               ↑
            Absolute Root

        Which initially gives:

            [TARGET, Gen-One-Child-2, Absolute Root]

        That's backwards for what we need, so we reverse it:

            [Absolute Root, Gen-One-Child-2, TARGET]

        The selected topic itself is intentionally included.
        """
        path: list[Topic] = [selected_topic]

        current = selected_topic
        parent_id = current.parent_id

        # Walking until no parent.
        while parent_id is not None:
            current = topics_by_id[parent_id]
            path.append(current)

            parent_id = current.parent_id

        # reverse for future consumers
        path.reverse()

        return path

    def _wrap_with_parents(
        self,
        context_tree: TopicTreeData,
        parents: list[Topic],
        question_counts: TopicDifficultyCounts,
    ) -> TopicTreeData:
        """
        Wrap an already-built selected-topic subtree with its parents.

        At this point we might have:

            TARGET
            ├── Child-1
            └── Child-2

        and:

            parents = [Absolute Root, Gen-One-Child-2]

        Wrap from the INSIDE OUT, so the list is processed backwards:

            Gen-One-Child-2
            └── TARGET
                ├── Child-1
                └── Child-2

        then:

            Absolute Root
            └── Gen-One-Child-2
                └── TARGET
                    ├── Child-1
                    └── Child-2

        Each parent receives exactly ONE child on this path.
        Prevents unrelated sibling branches from getting back into the result.
        """
        for parent in reversed(parents):
            context_tree = TopicTreeData(
                id=parent.id,
                name=parent.name,
                slug=parent.slug,
                description=parent.description,
                question_counts=self._build_question_count_data(
                    parent.id,
                    question_counts,
                ),
                children=(context_tree,),
            )

        return context_tree

    @staticmethod
    def _print_tree(
        node: TopicTreeData,
        prefix: str = "",
        is_last: bool = True,
    ) -> None:
        """
        Debug printer for visual check of the tree shape.
        No business logic, just shows I can ctrl+c -> ctrl+v cool symbols.
        """
        connector = "└── " if is_last else "├── "

        print(f"{prefix}{connector}{node.name}")

        child_prefix = prefix + ("    " if is_last else "│   ")

        for index, child in enumerate(node.children):
            TopicTreeBuilder._print_tree(
                child,
                prefix=child_prefix,
                is_last=index == len(node.children) - 1,
            )
