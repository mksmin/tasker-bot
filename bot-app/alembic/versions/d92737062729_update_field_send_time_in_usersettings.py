"""update field send_time in usersettings

Revision ID: d92737062729
Revises: f3d1be46587b
Create Date: 2025-04-25 18:46:02.603395

"""

from typing import Sequence, Union

from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d92737062729"
down_revision: Union[str, None] = "f3d1be46587b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        "user_settings",
        "send_time",
        existing_type=postgresql.TIME(),
        nullable=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "user_settings",
        "send_time",
        existing_type=postgresql.TIME(),
        nullable=True,
    )
