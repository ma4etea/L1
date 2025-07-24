"""empty message

Revision ID: 015093090574
Revises: d3da133ce132
Create Date: 2025-07-15 19:55:04.765023

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "015093090574"
down_revision: Union[str, None] = "d3da133ce132"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
            WITH duplicates AS (
                SELECT id, title as old_title,
                       ROW_NUMBER() OVER (PARTITION BY title ORDER BY id) AS rn
                FROM hotels
            )
            UPDATE hotels
            SET title = d.old_title || ' #' || d.id
            FROM duplicates d
            WHERE hotels.id = d.id
              AND d.rn > 1
        """
    )
    op.create_unique_constraint("uq_hotels_title", "hotels", ["title"])


def downgrade() -> None:
    op.drop_constraint("uq_hotels_title", "hotels", type_="unique")
