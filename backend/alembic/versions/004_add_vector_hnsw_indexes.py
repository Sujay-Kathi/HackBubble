"""add HNSW vector similarity indexes for matching engine

Revision ID: 004_add_vector_hnsw_indexes
Revises: 003_user_is_admin
Create Date: 16 Nov 2026

Why this migration exists
--------------------------
The matching engine runs ORDER-BY-distance queries using the pgvector <=>
(cosine distance) operator on three vector columns:

  candidate_embeddings.vector         -- candidate skill + project vectors
  team_intelligence.problem_embedding -- team problem-statement vector
  team_roles.role_embedding           -- role-requirement vector

Without an index PostgreSQL performs a sequential scan of every row on each
matching request.  HNSW (Hierarchical Navigable Small World) provides
approximate nearest-neighbour search in O(log n) time with high recall.

Index parameters chosen
-----------------------
  m              = 16   -- neighbours per node; standard default; good recall/speed
  ef_construction = 64  -- build-time beam width; doubles the default (40) for
                            better graph quality at modest extra build cost
  operator class  = vector_cosine_ops
                        -- matches the <=> operator used in queries;
                           must equal the query operator or the index is ignored

Downgrade
---------
Drops all three HNSW indexes.  The tables and data are untouched.
"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "004_add_vector_hnsw_indexes"
down_revision: Union[str, Sequence[str], None] = "003_user_is_admin"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── candidate_embeddings.vector ──────────────────────────────────────
    # Queried by the matching engine: find candidates closest to a team's
    # problem embedding via cosine distance.
    op.execute(
        """
        CREATE INDEX ix_cand_embed_vector_hnsw
            ON candidate_embeddings
            USING hnsw (vector vector_cosine_ops)
            WITH (m = 16, ef_construction = 64);
        """
    )

    # ── team_intelligence.problem_embedding ──────────────────────────────
    # Queried when scoring a candidate against team problem context.
    op.execute(
        """
        CREATE INDEX ix_team_intel_problem_embed_hnsw
            ON team_intelligence USING hnsw (problem_embedding vector_cosine_ops)
            WITH (m = 16, ef_construction = 64);
        """
    )

    # ── team_roles.role_embedding ─────────────────────────────────────────
    # Queried when ranking teams whose open roles best match a candidate.
    op.execute(
        """
        CREATE INDEX ix_team_roles_role_embed_hnsw
            ON team_roles USING hnsw (role_embedding vector_cosine_ops)
            WITH (m = 16, ef_construction = 64);
        """
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_team_roles_role_embed_hnsw;")
    op.execute("DROP INDEX IF EXISTS ix_team_intel_problem_embed_hnsw;")
    op.execute("DROP INDEX IF EXISTS ix_cand_embed_vector_hnsw;")
