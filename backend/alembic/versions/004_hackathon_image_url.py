"""add hackathon image_url

Revision ID: 004_hackathon_image_url
Revises: 003_user_is_admin
Create Date: 16 Nov 2026
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "004_hackathon_image_url"
down_revision: Union[str, Sequence[str], None] = "004_add_vector_hnsw_indexes"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "hackathons",
        sa.Column("image_url", sa.String(1000), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("hackathons", "image_url")
