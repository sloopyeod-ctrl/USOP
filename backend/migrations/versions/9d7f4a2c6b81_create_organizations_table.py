"""create organizations table

Revision ID: 9d7f4a2c6b81
Revises: 7470c9694a00
Create Date: 2026-07-14

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "9d7f4a2c6b81"
down_revision: Union[str, Sequence[str], None] = "7470c9694a00"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the canonical USOP organizations table."""

    op.create_table(
        "organizations",
        sa.Column(
            "name",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "slug",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "organization_type",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "primary_domain",
            sa.String(length=255),
            nullable=True,
        ),
        sa.Column(
            "time_zone",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "description",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "external_reference",
            sa.String(length=255),
            nullable=True,
        ),
        sa.Column(
            "deployment_identifier",
            sa.String(length=255),
            nullable=True,
        ),
        sa.Column(
            "settings_json",
            sa.JSON(),
            nullable=True,
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
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_organizations_name"),
        "organizations",
        ["name"],
        unique=False,
    )

    op.create_index(
        op.f("ix_organizations_slug"),
        "organizations",
        ["slug"],
        unique=True,
    )

    op.create_index(
        op.f("ix_organizations_status"),
        "organizations",
        ["status"],
        unique=False,
    )

    op.create_index(
        op.f("ix_organizations_organization_type"),
        "organizations",
        ["organization_type"],
        unique=False,
    )

    op.create_index(
        op.f("ix_organizations_primary_domain"),
        "organizations",
        ["primary_domain"],
        unique=False,
    )

    op.create_index(
        op.f("ix_organizations_external_reference"),
        "organizations",
        ["external_reference"],
        unique=False,
    )

    op.create_index(
        op.f("ix_organizations_deployment_identifier"),
        "organizations",
        ["deployment_identifier"],
        unique=True,
    )


def downgrade() -> None:
    """Remove the canonical USOP organizations table."""

    op.drop_index(
        op.f("ix_organizations_deployment_identifier"),
        table_name="organizations",
    )

    op.drop_index(
        op.f("ix_organizations_external_reference"),
        table_name="organizations",
    )

    op.drop_index(
        op.f("ix_organizations_primary_domain"),
        table_name="organizations",
    )

    op.drop_index(
        op.f("ix_organizations_organization_type"),
        table_name="organizations",
    )

    op.drop_index(
        op.f("ix_organizations_status"),
        table_name="organizations",
    )

    op.drop_index(
        op.f("ix_organizations_slug"),
        table_name="organizations",
    )

    op.drop_index(
        op.f("ix_organizations_name"),
        table_name="organizations",
    )

    op.drop_table("organizations")
