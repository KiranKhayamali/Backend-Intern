"""Added ready and cancelled options in OrderStatusEnum

Revision ID: 40542bae7ca8
Revises: 4e532c586976
Create Date: 2026-05-14 10:04:00.649217

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '40542bae7ca8'
down_revision: Union[str, Sequence[str], None] = '4e532c586976'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Alter the order_status_enum to include all values
    op.execute("ALTER TYPE order_status_enum ADD VALUE 'ready'")
    op.execute("ALTER TYPE order_status_enum ADD VALUE 'cancelled'")
    op.execute("ALTER TYPE order_status_enum ADD VALUE 'idle'")


def downgrade() -> None:
    """Downgrade schema."""
    # Note: PostgreSQL does not allow removing enum values, so we cannot truly revert this migration.
    # If needed, the enum would need to be recreated.
    pass
