"""create authorization events

Revision ID: 2f8a6d4c91e7
Revises: 8c4e2f7a91bd
Create Date: 2026-08-03

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "2f8a6d4c91e7"
down_revision: Union[str, Sequence[str], None] = "8c4e2f7a91bd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "authorization_events",
        sa.Column("organization_id", sa.String(length=36), nullable=False),
        sa.Column("organizational_identity_id", sa.String(length=36), nullable=True),
        sa.Column("identity_id", sa.String(length=36), nullable=True),
        sa.Column("account_id", sa.String(length=36), nullable=True),
        sa.Column("role_assignment_id", sa.String(length=36), nullable=True),
        sa.Column("subject_type", sa.String(length=100), nullable=False),
        sa.Column("subject_id", sa.String(length=255), nullable=False),
        sa.Column("event_type", sa.String(length=100), nullable=False),
        sa.Column("assignment_type", sa.String(length=100), nullable=True),
        sa.Column("previous_status", sa.String(length=100), nullable=True),
        sa.Column("current_status", sa.String(length=100), nullable=True),
        sa.Column("directory_scope", sa.String(length=1024), nullable=True),
        sa.Column("application_scope", sa.String(length=1024), nullable=True),
        sa.Column("effective_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("effective_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("detected_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("risk_level", sa.String(length=100), nullable=False),
        sa.Column("is_material", sa.Boolean(), nullable=False),
        sa.Column("previous_state_json", sa.JSON(), nullable=True),
        sa.Column("current_state_json", sa.JSON(), nullable=True),
        sa.Column("evidence_json", sa.JSON(), nullable=True),
        sa.Column("source_system", sa.String(length=100), nullable=True),
        sa.Column("source_identifier", sa.String(length=255), nullable=True),
        sa.Column("confidence_score", sa.Integer(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_by", sa.String(length=255), nullable=True),
        sa.Column("updated_by", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"]),
        sa.ForeignKeyConstraint(["identity_id"], ["identities.id"]),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(
            ["organizational_identity_id"],
            ["organizational_identities.id"],
        ),
        sa.ForeignKeyConstraint(
            ["role_assignment_id"],
            ["role_assignments.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    for column_name in (
        "organization_id",
        "organizational_identity_id",
        "identity_id",
        "account_id",
        "role_assignment_id",
        "subject_type",
        "subject_id",
        "event_type",
        "assignment_type",
        "directory_scope",
        "application_scope",
        "effective_start",
        "effective_end",
        "detected_at",
        "risk_level",
        "is_material",
    ):
        op.create_index(
            f"ix_authorization_events_{column_name}",
            "authorization_events",
            [column_name],
            unique=False,
        )


def downgrade() -> None:
    for column_name in reversed(
        (
            "organization_id",
            "organizational_identity_id",
            "identity_id",
            "account_id",
            "role_assignment_id",
            "subject_type",
            "subject_id",
            "event_type",
            "assignment_type",
            "directory_scope",
            "application_scope",
            "effective_start",
            "effective_end",
            "detected_at",
            "risk_level",
            "is_material",
        )
    ):
        op.drop_index(
            f"ix_authorization_events_{column_name}",
            table_name="authorization_events",
        )

    op.drop_table("authorization_events")
