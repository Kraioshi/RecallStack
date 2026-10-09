from uuid import UUID


class QuestionNotFoundError(Exception):
    """Raised when an application operation requires a question that does not exist."""

    def __init__(self, question_id: UUID) -> None:
        self.question_id = question_id
        super().__init__(f"Question '{question_id}' was not found.")


class QuestionAlreadyExistsError(Exception):
    """Raised when a topic already contains this question text."""

    def __init__(self, topic_id: UUID, question: str) -> None:
        self.topic_id = topic_id
        self.question = question
        super().__init__(f"Question '{question}' already exists in topic '{topic_id}'.")


class RandomQuestionNotFoundError(Exception):
    """Raised when no question matches the random selection criteria."""

    def __init__(self) -> None:
        super().__init__("No question matches the requested criteria.")
