"""Add new field to users table

Revision ID: d7c687429f2d
Revises: bec76780fc8b
Create Date: 2025-04-03 20:31:40.809079

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d7c687429f2d"
down_revision: Union[str, None] = "bec76780fc8b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "users", sa.Column("first_name", sa.String(length=50), nullable=True)
    )
    op.add_column(
        "users", sa.Column("last_name", sa.String(length=50), nullable=True)
    )
    op.add_column(
        "users", sa.Column("username", sa.String(length=50), nullable=True)
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("users", "username")
    op.drop_column("users", "last_name")
    op.drop_column("users", "first_name")
