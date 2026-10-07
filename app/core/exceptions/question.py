from uuid import UUID


class QuestionNotFoundError(Exception):
    """Raised when an application operation requires a question that does not exist."""

    def __init__(self, question_id: UUID) -> None:
        self.question_id = question_id
        super().__init__(f"Question '{question_id}' was not found.")


class RandomQuestionNotFoundError(Exception):
    """Raised when no question matches the random selection criteria."""
