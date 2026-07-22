"""create decision knowledge table

Revision ID: 089da77a257d
Revises: 7080e602d9a0
Create Date: 2026-07-22
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "089da77a257d"
down_revision: str | None = "7080e602d9a0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "decision_knowledge",
        sa.Column(
            "decision_record_id",
            sa.String(length=36),
            nullable=False,
        ),
        sa.Column(
            "knowledge_asset_id",
            sa.String(length=36),
            nullable=False,
        ),
        sa.Column(
            "relationship_type",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "source_system",
            sa.String(length=100),
            nullable=True,
        ),
        sa.Column(
            "source_identifier",
            sa.String(length=255),
            nullable=True,
        ),
        sa.Column(
            "confidence_score",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "id",
            sa.String(length=36),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "created_by",
            sa.String(length=255),
            nullable=True,
        ),
        sa.Column(
            "updated_by",
            sa.String(length=255),
            nullable=True,
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["decision_record_id"],
            ["decision_records.id"],
        ),
        sa.ForeignKeyConstraint(
            ["knowledge_asset_id"],
            ["knowledge_assets.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "decision_record_id",
            "knowledge_asset_id",
            "relationship_type",
            name=(
                "uq_decision_knowledge_"
                "decision_asset_relationship"
            ),
        ),
    )

    op.create_index(
        op.f(
            "ix_decision_knowledge_decision_record_id"
        ),
        "decision_knowledge",
        ["decision_record_id"],
        unique=False,
    )

    op.create_index(
        op.f(
            "ix_decision_knowledge_knowledge_asset_id"
        ),
        "decision_knowledge",
        ["knowledge_asset_id"],
        unique=False,
    )

    op.create_index(
        op.f(
            "ix_decision_knowledge_relationship_type"
        ),
        "decision_knowledge",
        ["relationship_type"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f(
            "ix_decision_knowledge_relationship_type"
        ),
        table_name="decision_knowledge",
    )

    op.drop_index(
        op.f(
            "ix_decision_knowledge_knowledge_asset_id"
        ),
        table_name="decision_knowledge",
    )

    op.drop_index(
        op.f(
            "ix_decision_knowledge_decision_record_id"
        ),
        table_name="decision_knowledge",
    )

    op.drop_table("decision_knowledge")