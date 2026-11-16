"""add hackathon is_verified moderation flag

Revision ID: 002_hackathon_is_verified
Revises: 001_initial_schema
Create Date: 16 Nov 2026
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "002_hackathon_is_verified"
down_revision: Union[str, Sequence[str], None] = "001_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "hackathons",
        sa.Column(
            "is_verified",
            sa.Boolean(),
            server_default=sa.false(),
            nullable=False,
        ),
    )
    op.create_index("ix_hackathons_is_verified", "hackathons", ["is_verified"])


def downgrade() -> None:
    op.drop_index("ix_hackathons_is_verified", table_name="hackathons")
    op.drop_column("hackathons", "is_verified")
