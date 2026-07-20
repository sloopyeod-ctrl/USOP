"""create knowledge assets table

Revision ID: 7080e602d9a0
Revises: d84f6b2e9a31
Create Date: 2026-07-19
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "7080e602d9a0"
down_revision: str | None = "d84f6b2e9a31"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "knowledge_assets",
        sa.Column(
            "organization_id",
            sa.String(length=36),
            nullable=False,
        ),
        sa.Column(
            "title",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "summary",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "guidance",
            sa.Text(),
            nullable=False,
        ),
        sa.Column(
            "category",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "version",
            sa.Integer(),
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
            ["organization_id"],
            ["organizations.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "organization_id",
            "title",
            "version",
            name=(
                "uq_knowledge_assets_"
                "organization_title_version"
            ),
        ),
    )

    op.create_index(
        op.f("ix_knowledge_assets_category"),
        "knowledge_assets",
        ["category"],
        unique=False,
    )

    op.create_index(
        op.f("ix_knowledge_assets_organization_id"),
        "knowledge_assets",
        ["organization_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_knowledge_assets_status"),
        "knowledge_assets",
        ["status"],
        unique=False,
    )

    op.create_index(
        op.f("ix_knowledge_assets_title"),
        "knowledge_assets",
        ["title"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_knowledge_assets_title"),
        table_name="knowledge_assets",
    )

    op.drop_index(
        op.f("ix_knowledge_assets_status"),
        table_name="knowledge_assets",
    )

    op.drop_index(
        op.f("ix_knowledge_assets_organization_id"),
        table_name="knowledge_assets",
    )

    op.drop_index(
        op.f("ix_knowledge_assets_category"),
        table_name="knowledge_assets",
    )

    op.drop_table("knowledge_assets")
