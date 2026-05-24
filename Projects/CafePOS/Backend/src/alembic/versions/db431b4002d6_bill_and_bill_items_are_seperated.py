"""Bill and Bill items are seperated

Revision ID: db431b4002d6
Revises:
Create Date: 2026-05-05 11:58:04.147034

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from Projects.CafePOS.Backend.src.app import models  # noqa: F401
from Projects.CafePOS.Backend.src.app.models.base import Base

# revision identifiers, used by Alembic.
revision: str = 'db431b4002d6'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    Base.metadata.create_all(bind)


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()
    Base.metadata.drop_all(bind)
