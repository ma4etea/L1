"""empty message

Revision ID: 2a72a77b4382
Revises: 015093090574
Create Date: 2025-07-17 10:35:30.522653

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "2a72a77b4382"
down_revision: Union[str, None] = "015093090574"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade() -> None:
    op.execute(
        """
            WITH duplicates AS (
                SELECT id, title as old_title,
                       ROW_NUMBER() OVER (PARTITION BY title ORDER BY id) AS rn
                FROM facilities
            )
            UPDATE facilities
            SET title = d.old_title || ' #' || d.id
            FROM duplicates d
            WHERE facilities.id = d.id
              AND d.rn > 1
        """
    )
    op.create_unique_constraint("uq_facilities_title", "facilities", ["title"])


def downgrade() -> None:
    op.drop_constraint("uq_facilities_title", "facilities", type_="unique")