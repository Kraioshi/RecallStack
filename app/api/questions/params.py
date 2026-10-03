"""Reusable HTTP parameter definitions for the Questions API."""

from typing import Annotated
from uuid import UUID

from fastapi import Path, Query

type QuestionIdPath = Annotated[
    UUID,
    Path(
        description="Unique identifier of the question.",
    ),
]


type TopicIdQuery = Annotated[
    UUID,
    Query(
        description="Return questions belonging to this topic.",
    ),
]
