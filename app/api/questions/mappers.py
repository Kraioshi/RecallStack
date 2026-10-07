"""
Mapping helpers for Questions API layer.

Functions translate between HTTP-facing Pydantic schemas and application DTOs.
"""

from app.api.questions.schemas.request import (
    CreateQuestionRequest,
    RandomQuestionQuery,
    UpdateQuestionRequest,
)
from app.api.questions.schemas.response import QuestionResponse
from app.core.dto.question import (
    CreateQuestionData,
    QuestionData,
    RandomQuestionCriteria,
    UpdateQuestionData,
)
from app.core.types.common import UNSET


def to_create_question_data(
    request: CreateQuestionRequest,
) -> CreateQuestionData:
    """Map an HTTP create-question request to the service input DTO."""

    return CreateQuestionData(
        topic_id=request.topic_id,
        question=request.question,
        answer=request.answer,
        difficulty=request.difficulty,
    )


def to_question_response(
    data: QuestionData,
) -> QuestionResponse:
    """Map application question data to the public API response schema."""

    return QuestionResponse.model_validate(data)


def to_question_responses(
    data: list[QuestionData],
) -> list[QuestionResponse]:
    """Map application question data to public API response schemas."""

    return [to_question_response(question) for question in data]


def to_update_question_data(
    request: UpdateQuestionRequest,
) -> UpdateQuestionData:
    """Map an HTTP partial-update request to the service input DTO."""

    return UpdateQuestionData(
        topic_id=request.topic_id if request.topic_id is not None else UNSET,
        question=request.question if request.question is not None else UNSET,
        answer=request.answer if request.answer is not None else UNSET,
        difficulty=request.difficulty if request.difficulty is not None else UNSET,
    )


def to_random_question_criteria(
    query: RandomQuestionQuery,
) -> RandomQuestionCriteria:
    return RandomQuestionCriteria(
        exclude_id=query.exclude_id,
        difficulty=query.difficulty,
        topic_id=query.topic_id,
        include_descendants=query.include_descendants,
    )
