"""add user is_admin flag

Revision ID: 003_user_is_admin
Revises: 002_hackathon_is_verified
Create Date: 16 Nov 2026
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "003_user_is_admin"
down_revision: Union[str, Sequence[str], None] = "002_hackathon_is_verified"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "is_admin",
            sa.Boolean(),
            server_default=sa.false(),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("users", "is_admin")
