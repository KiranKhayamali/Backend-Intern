"""add author_name to posts

Revision ID: 20260413_01
Revises:
Create Date: 2026-04-13 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260413_01"
down_revision: Union[str, Sequence[str], None] = None
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
