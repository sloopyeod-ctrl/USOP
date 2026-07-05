"""Create access reviews table v2

Revision ID: c9a60d568249
Revises: 0e30cb831334
Create Date: 2026-07-04 19:38:31.536375
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c9a60d568249"
down_revision: Union[str, Sequence[str], None] = "0e30cb831334"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "access_reviews",
        sa.Column("identity_id", sa.String(length=36), nullable=False),
        sa.Column("review_type", sa.String(length=100), nullable=False),
        sa.Column("status", sa.String(length=100), nullable=False),
        sa.Column("risk_score", sa.Integer(), nullable=False),
        sa.Column("risk_level", sa.String(length=100), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(), nullable=True),
        sa.Column("reviewed_by", sa.String(length=255), nullable=True),
        sa.Column("review_due_at", sa.DateTime(), nullable=True),
        sa.Column("snapshot_hash", sa.String(length=64), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("source_system", sa.String(length=100), nullable=True),
        sa.Column("source_identifier", sa.String(length=255), nullable=True),
        sa.Column("confidence_score", sa.Integer(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("created_by", sa.String(length=255), nullable=True),
        sa.Column("updated_by", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["identity_id"], ["identities.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index("ix_access_reviews_identity_id", "access_reviews", ["identity_id"])
    op.create_index("ix_access_reviews_status", "access_reviews", ["status"])
    op.create_index("ix_access_reviews_review_due_at", "access_reviews", ["review_due_at"])
    op.create_index("ix_access_reviews_snapshot_hash", "access_reviews", ["snapshot_hash"])


def downgrade() -> None:
    op.drop_index("ix_access_reviews_snapshot_hash", table_name="access_reviews")
    op.drop_index("ix_access_reviews_review_due_at", table_name="access_reviews")
    op.drop_index("ix_access_reviews_status", table_name="access_reviews")
    op.drop_index("ix_access_reviews_identity_id", table_name="access_reviews")
    op.drop_table("access_reviews")