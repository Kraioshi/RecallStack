from typing import Annotated

from fastapi import Depends

from app.database.session import async_session_maker
from app.infrastructure.unit_of_work.sqlalchemy import SQLAlchemyUnitOfWork
from app.services.question import QuestionService
from app.services.topic import TopicService


def get_topic_service() -> TopicService:
    """
    Build the TopicService used by the API layer.

    Composition point where abstract app dependencies
    are connected to their real infrastructure implementations.

    TopicService only knows about the UnitOfWork protocol.
    It should not know that PostgreSQL or SQLAlchemy exist.
    Here at the API boundary SQLAlchemyUnitOfWork is used as the concrete implementation
    and is given the application's session factory.

    The session itself is not created here.
    SQLAlchemyUnitOfWork owns that lifecycle and creates a fresh
    AsyncSession when the service enters:

        async with self._uow:

    This keeps session and transaction management outside both the endpoint
    and the service layer.
    """
    uow = SQLAlchemyUnitOfWork(async_session_maker)

    return TopicService(uow)


type TopicServiceDep = Annotated[
    TopicService,
    Depends(get_topic_service),
]


def get_question_service() -> QuestionService:
    """Build the QuestionService used by the API layer."""

    uow = SQLAlchemyUnitOfWork(async_session_maker)

    return QuestionService(uow)


type QuestionServiceDep = Annotated[
    QuestionService,
    Depends(get_question_service),
]
