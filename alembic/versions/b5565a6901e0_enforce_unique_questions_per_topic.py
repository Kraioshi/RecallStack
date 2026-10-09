"""enforce unique questions per topic

Revision ID: b5565a6901e0
Revises: 9ebbb47127f7
Create Date: 2026-10-09 22:27:39.971009

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b5565a6901e0"
down_revision: str | Sequence[str] | None = "9ebbb47127f7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Enforce normalized question uniqueness within each topic."""
    op.create_index(
        "uq_questions_topic_normalized_text",
        "questions",
        [
            "topic_id",
            sa.text("lower(btrim(question))"),
        ],
        unique=True,
    )


def downgrade() -> None:
    """Remove normalized question uniqueness enforcement."""
    op.drop_index(
        "uq_questions_topic_normalized_text",
        table_name="questions",
    )
