"""add new field to usersettings

Revision ID: f3d1be46587b
Revises: 645e857f25c1
Create Date: 2025-04-25 18:40:36.826386

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f3d1be46587b"
down_revision: str | None = "645e857f25c1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("user_settings", sa.Column("send_time", sa.Time(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("user_settings", "send_time")
