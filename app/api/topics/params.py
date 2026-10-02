"""
Reusable HTTP parameter definitions for the Topics API.

Centralizes FastAPI specific path and query parameter metadata.

Keeping it separate avoids repeating validation and OpenAPI documentation in routers
while keeping HTTP concerns inside the API layer.
"""

from typing import Annotated
from uuid import UUID

from fastapi import Path

type TopicIdPath = Annotated[
    UUID,
    Path(
        description="Unique identifier of the topic.",
    ),
]
