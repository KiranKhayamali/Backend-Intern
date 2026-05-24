"""add cascade delete to posts author_id

Revision ID: 5d353d0f0aa0
Revises: dbf3ba063f3f
Create Date: 2026-04-16 13:45:39.642495

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5d353d0f0aa0'
down_revision: Union[str, Sequence[str], None] = 'dbf3ba063f3f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Drop existing foreign key constraint
    op.execute("""
        ALTER TABLE posts
        DROP CONSTRAINT posts_author_id_fkey;
    """)

    # 2. Recreate with ON DELETE CASCADE
    op.execute("""
        ALTER TABLE posts
        ADD CONSTRAINT posts_author_id_fkey
        FOREIGN KEY (author_id)
        REFERENCES users(id)
        ON DELETE CASCADE;
    """)


def downgrade() -> None:
    # 1. Drop cascade constraint
    op.execute("""
        ALTER TABLE posts
        DROP CONSTRAINT posts_author_id_fkey;
    """)

    # 2. Recreate original FK (without cascade)
    op.execute("""
        ALTER TABLE posts
        ADD CONSTRAINT posts_author_id_fkey
        FOREIGN KEY (author_id)
        REFERENCES users(id);
    """)