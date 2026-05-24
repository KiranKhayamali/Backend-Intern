"""add author_name to the posts table

Revision ID: dbf3ba063f3f
Revises: 20260413_01
Create Date: 2026-04-13 10:05:52.888919

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dbf3ba063f3f'
down_revision: Union[str, Sequence[str], None] = '20260413_01'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'posts' AND column_name = 'author_name'
            ) THEN
                ALTER TABLE posts ADD COLUMN author_name VARCHAR(20);
            END IF;
        END
        $$;
        """
    )

    op.execute(
        """
        UPDATE posts p
        SET author_name = u.username
        FROM users u
        WHERE p.author_id = u.id
          AND p.author_name IS NULL;
        """
    )

    op.execute("UPDATE posts SET author_name = 'unknown' WHERE author_name IS NULL;")
    op.execute("ALTER TABLE posts ALTER COLUMN author_name SET NOT NULL;")


def downgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'posts' AND column_name = 'author_name'
            ) THEN
                ALTER TABLE posts DROP COLUMN author_name;
            END IF;
        END
        $$;
        """
    )
