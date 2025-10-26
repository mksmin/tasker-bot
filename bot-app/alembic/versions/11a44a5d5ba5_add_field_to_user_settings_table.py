"""add field to user settings table

Revision ID: 11a44a5d5ba5
Revises: d92737062729
Create Date: 2025-10-26 22:17:57.693244

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "11a44a5d5ba5"
down_revision: str | None = "d92737062729"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "user_settings",
        sa.Column(
            "send_enable",
            sa.Boolean(),
            server_default="true",
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("user_settings", "send_enable")
