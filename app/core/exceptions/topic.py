from uuid import UUID


class TopicNotFoundError(Exception):
    """Raised when an application operation requires a topic that does not exist."""

    def __init__(self, topic_id: UUID) -> None:
        self.topic_id = topic_id
        super().__init__(f"Topic '{topic_id}' was not found.")


class TopicSlugAlreadyExistsError(Exception):
    """Raised when a sibling topic already uses the requested slug."""

    def __init__(
        self,
        slug: str,
        parent_id: UUID | None,
    ) -> None:
        self.slug = slug
        self.parent_id = parent_id

        scope = (
            f"under parent '{parent_id}'" if parent_id is not None else "at root level"
        )

        super().__init__(f"Topic with slug '{slug}' already exists {scope}.")


class TopicHasChildrenError(Exception):
    """Raised when attempting to delete a topic that still has children."""

    def __init__(self, topic_id: UUID) -> None:
        self.topic_id = topic_id

        super().__init__(
            f"Topic '{topic_id}' cannot be deleted while it has child topics."
        )
