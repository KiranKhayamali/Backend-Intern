"""add is_admin to users

Revision ID: 6d2c1a4b9f10
Revises: 001a5341fb78
Create Date: 2026-04-07 12:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "6d2c1a4b9f10"
down_revision: Union[str, Sequence[str], None] = "001a5341fb78"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if "users" in inspector.get_table_names():
        existing_columns = {col["name"] for col in inspector.get_columns("users")}
        if "is_admin" not in existing_columns:
            op.add_column(
                "users",
                sa.Column(
                    "is_admin",
                    sa.Boolean(),
                    nullable=False,
                    server_default=sa.text("false"),
                ),
            )
            op.alter_column("users", "is_admin", server_default=None)


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if "users" in inspector.get_table_names():
        existing_columns = {col["name"] for col in inspector.get_columns("users")}
        if "is_admin" in existing_columns:
            op.drop_column("users", "is_admin")
