from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Topic(Base):
    __tablename__ = "topics"

    id: Mapped[UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid4,
    )

    # self-referencing FK to build any-depth tree
    # Root topics have parent_id=None
    # Child topics reference another topic
    parent_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("topics.id"),
    )

    name: Mapped[str] = mapped_column(
        String(100),
    )

    slug: Mapped[str] = mapped_column(
        String(100),
    )

    description: Mapped[str | None] = mapped_column(
        Text,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Topic can point to another topic as its parent
    #
    # Both sides of this relationship use the same table, that's why
    # Alchemy can't automatically tell which topic is the parent and which is the child.
    # remote_side=[id] tells alchemy the id on the other Topic is the parent side in
    # parent_id -> id relationship
    #
    # Ex:
    # Parent (id=1)
    # └── Child (parent_id=1)
    parent: Mapped["Topic | None"] = relationship(
        back_populates="children",
        remote_side=[id],
    )

    # Opposite orm side of that relationship.
    # Alchemy uses parent id to find all Topics that point to this Topic
    #
    # Ex:
    # Parent (id=1)
    #   ├── Child1 (parent_id=1)
    #   └── Child2     (parent_id=1)
    #
    # For parent:
    #     parent.children -> [child1, child2]
    children: Mapped[list["Topic"]] = relationship(
        back_populates="parent",
    )
