from fastapi import APIRouter, status

from app.api.dependencies.services import QuestionServiceDep
from app.api.questions import mappers as question_mapper
from app.api.questions.params import QuestionIdPath, TopicIdQuery
from app.api.questions.schemas.request import (
    CreateQuestionRequest,
    UpdateQuestionRequest,
)
from app.api.questions.schemas.response import QuestionResponse

router = APIRouter(
    prefix="/questions",
    tags=["questions"],
)


@router.get(
    "/{question_id}",
    response_model=QuestionResponse,
    summary="Get a question",
    response_description="The requested question.",
    responses={
        404: {
            "description": "Question not found.",
        },
    },
)
async def get_question(
    question_id: QuestionIdPath,
    service: QuestionServiceDep,
) -> QuestionResponse:
    """Retrieve a single question by its unique identifier."""

    question = await service.get_question(question_id)

    return question_mapper.to_question_response(question)


@router.get(
    "",
    response_model=list[QuestionResponse],
    summary="List questions by topic",
    response_description="Questions belonging to the requested topic.",
    responses={
        404: {
            "description": "Topic not found.",
        },
    },
)
async def list_questions_by_topic(
    topic_id: TopicIdQuery,
    service: QuestionServiceDep,
) -> list[QuestionResponse]:
    """Retrieve questions belonging to a topic."""

    questions = await service.list_questions_by_topic(topic_id)

    return question_mapper.to_question_responses(questions)


@router.post(
    "",
    response_model=QuestionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a question",
    response_description="The newly created question.",
    responses={
        404: {
            "description": "Topic not found.",
        },
    },
)
async def create_question(
    request: CreateQuestionRequest,
    service: QuestionServiceDep,
) -> QuestionResponse:
    data = question_mapper.to_create_question_data(request)

    question = await service.create_question(data)

    return question_mapper.to_question_response(question)


@router.patch(
    "/{question_id}",
    response_model=QuestionResponse,
    summary="Update a question",
    response_description="The updated question.",
    responses={
        404: {
            "description": "Question or destination topic not found.",
        },
    },
)
async def update_question(
    question_id: QuestionIdPath,
    request: UpdateQuestionRequest,
    service: QuestionServiceDep,
) -> QuestionResponse:
    """Partially update an existing question."""

    data = question_mapper.to_update_question_data(request)

    question = await service.update_question(
        question_id,
        data,
    )

    return question_mapper.to_question_response(question)


@router.delete(
    "/{question_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a question",
    responses={
        404: {
            "description": "Question not found.",
        },
    },
)
async def delete_question(
    question_id: QuestionIdPath,
    service: QuestionServiceDep,
) -> None:
    await service.delete_question(question_id)
