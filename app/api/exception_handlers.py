from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.core.exceptions.question import QuestionNotFoundError
from app.core.exceptions.topic import TopicHasChildrenError, TopicNotFoundError


async def handle_topic_not_found(
    _request: Request,
    exc: Exception,
) -> JSONResponse:
    """
    Translate TopicNotFoundError into an HTTP 404 response.

    Starlette types exception handlers against the generic Exception type.
    The concrete exception handled by this function is determined by the
    registration below, where TopicNotFoundError is mapped to this handler.
    """
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "detail": str(exc),
        },
    )


async def handle_topic_has_children(
    _request: Request,
    exc: Exception,
) -> JSONResponse:
    """Translate TopicHasChildrenError into an HTTP 409 response."""
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "detail": str(exc),
        },
    )


async def handle_question_not_found(
    _request: Request,
    exc: Exception,
) -> JSONResponse:
    """Translate QuestionNotFoundError into an HTTP 404 response."""

    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "detail": str(exc),
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(TopicNotFoundError, handle_topic_not_found)
    app.add_exception_handler(TopicHasChildrenError, handle_topic_has_children)
    app.add_exception_handler(QuestionNotFoundError, handle_question_not_found)
