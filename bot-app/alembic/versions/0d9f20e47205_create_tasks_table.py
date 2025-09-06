"""Create tasks table

Revision ID: 0d9f20e47205
Revises: a021453792ec
Create Date: 2025-03-17 16:43:01.511871

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0d9f20e47205"
down_revision: Union[str, None] = "a021453792ec"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "tasks",
        sa.Column("text_task", sa.String(length=255), nullable=False),
        sa.Column("is_done", sa.Boolean(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        create_if_not_exists=True,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("tasks")
