"""add organization ownership to decision records

Revision ID: bb76da76389f
Revises: 089da77a257d
Create Date: 2026-07-22
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "bb76da76389f"
down_revision: str | None = "089da77a257d"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "decision_records",
        sa.Column(
            "organization_id",
            sa.String(length=36),
            nullable=False,
        ),
    )

    op.create_index(
        op.f("ix_decision_records_organization_id"),
        "decision_records",
        ["organization_id"],
        unique=False,
    )

    op.create_foreign_key(
        "fk_decision_records_organization_id_organizations",
        "decision_records",
        "organizations",
        ["organization_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_decision_records_organization_id_organizations",
        "decision_records",
        type_="foreignkey",
    )

    op.drop_index(
        op.f("ix_decision_records_organization_id"),
        table_name="decision_records",
    )

    op.drop_column(
        "decision_records",
        "organization_id",
    )
