"""email unique

Revision ID: 1a144aaceb5b
Revises: e4cae4c80d1c
Create Date: 2025-06-13 09:54:52.044783

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "1a144aaceb5b"
down_revision: Union[str, None] = "e4cae4c80d1c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint(None, "users", ["email"])


def downgrade() -> None:
    op.drop_constraint(None, "users", type_="unique")
