"""create pending decision work items

Revision ID: 6b3f9a2d1c74
Revises: 2f8a6d4c91e7
Create Date: 2026-08-03

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "6b3f9a2d1c74"
down_revision: Union[str, Sequence[str], None] = (
    "2f8a6d4c91e7"
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "pending_decision_work_items",
        sa.Column(
            "organization_id",
            sa.String(length=36),
            nullable=False,
        ),
        sa.Column(
            "identity_id",
            sa.String(length=36),
            nullable=True,
        ),
        sa.Column(
            "source_type",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "source_id",
            sa.String(length=36),
            nullable=False,
        ),
        sa.Column(
            "decision_category",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "title",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column(
            "priority",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "risk_level",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "materiality_reason",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "evidence_snapshot_json",
            sa.JSON(),
            nullable=False,
        ),
        sa.Column(
            "assigned_to",
            sa.String(length=255),
            nullable=True,
        ),
        sa.Column(
            "due_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "claimed_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "resolved_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "resolved_by",
            sa.String(length=255),
            nullable=True,
        ),
        sa.Column(
            "decision_record_id",
            sa.String(length=36),
            nullable=True,
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
            ["identity_id"],
            ["identities.id"],
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "organization_id",
            "source_type",
            "source_id",
            name=(
                "uq_pending_decision_work_items_"
                "organization_source"
            ),
        ),
    )

    for column_name in (
        "organization_id",
        "identity_id",
        "source_type",
        "source_id",
        "decision_category",
        "priority",
        "status",
        "risk_level",
        "assigned_to",
        "due_at",
        "resolved_at",
        "decision_record_id",
    ):
        op.create_index(
            (
                "ix_pending_decision_work_items_"
                f"{column_name}"
            ),
            "pending_decision_work_items",
            [column_name],
            unique=False,
        )


def downgrade() -> None:
    for column_name in reversed(
        (
            "organization_id",
            "identity_id",
            "source_type",
            "source_id",
            "decision_category",
            "priority",
            "status",
            "risk_level",
            "assigned_to",
            "due_at",
            "resolved_at",
            "decision_record_id",
        )
    ):
        op.drop_index(
            (
                "ix_pending_decision_work_items_"
                f"{column_name}"
            ),
            table_name="pending_decision_work_items",
        )

    op.drop_table("pending_decision_work_items")
