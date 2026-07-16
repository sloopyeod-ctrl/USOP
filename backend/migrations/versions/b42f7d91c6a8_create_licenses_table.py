"""create licenses table

Revision ID: b42f7d91c6a8
Revises: 9d7f4a2c6b81
Create Date: 2026-07-15

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b42f7d91c6a8"
down_revision: Union[str, Sequence[str], None] = "9d7f4a2c6b81"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the immutable canonical USOP licenses table."""

    op.create_table(
        "licenses",
        sa.Column(
            "organization_id",
            sa.String(length=36),
            nullable=False,
        ),
        sa.Column(
            "license_identifier",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "commercial_edition",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "commercial_purpose",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "license_format_version",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "issued_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "effective_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "expires_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "deployment_identifier",
            sa.String(length=255),
            nullable=True,
        ),
        sa.Column(
            "seat_limit",
            sa.Integer(),
            nullable=True,
        ),
        sa.Column(
            "commercial_modules_json",
            sa.JSON(),
            nullable=True,
        ),
        sa.Column(
            "feature_entitlements_json",
            sa.JSON(),
            nullable=True,
        ),
        sa.Column(
            "canonical_payload_json",
            sa.JSON(),
            nullable=False,
        ),
        sa.Column(
            "canonical_payload_hash",
            sa.String(length=64),
            nullable=False,
        ),
        sa.Column(
            "signature",
            sa.Text(),
            nullable=False,
        ),
        sa.Column(
            "signing_key_identifier",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "supersedes_license_id",
            sa.String(length=36),
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
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
        ),
        sa.ForeignKeyConstraint(
            ["supersedes_license_id"],
            ["licenses.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_licenses_organization_id"),
        "licenses",
        ["organization_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_licenses_license_identifier"),
        "licenses",
        ["license_identifier"],
        unique=True,
    )

    op.create_index(
        op.f("ix_licenses_status"),
        "licenses",
        ["status"],
        unique=False,
    )

    op.create_index(
        op.f("ix_licenses_commercial_edition"),
        "licenses",
        ["commercial_edition"],
        unique=False,
    )

    op.create_index(
        op.f("ix_licenses_commercial_purpose"),
        "licenses",
        ["commercial_purpose"],
        unique=False,
    )

    op.create_index(
        op.f("ix_licenses_license_format_version"),
        "licenses",
        ["license_format_version"],
        unique=False,
    )

    op.create_index(
        op.f("ix_licenses_issued_at"),
        "licenses",
        ["issued_at"],
        unique=False,
    )

    op.create_index(
        op.f("ix_licenses_effective_at"),
        "licenses",
        ["effective_at"],
        unique=False,
    )

    op.create_index(
        op.f("ix_licenses_expires_at"),
        "licenses",
        ["expires_at"],
        unique=False,
    )

    op.create_index(
        op.f("ix_licenses_deployment_identifier"),
        "licenses",
        ["deployment_identifier"],
        unique=False,
    )

    op.create_index(
        op.f("ix_licenses_canonical_payload_hash"),
        "licenses",
        ["canonical_payload_hash"],
        unique=False,
    )

    op.create_index(
        op.f("ix_licenses_signing_key_identifier"),
        "licenses",
        ["signing_key_identifier"],
        unique=False,
    )

    op.create_index(
        op.f("ix_licenses_supersedes_license_id"),
        "licenses",
        ["supersedes_license_id"],
        unique=False,
    )


def downgrade() -> None:
    """Remove the canonical USOP licenses table."""

    op.drop_index(
        op.f("ix_licenses_supersedes_license_id"),
        table_name="licenses",
    )

    op.drop_index(
        op.f("ix_licenses_signing_key_identifier"),
        table_name="licenses",
    )

    op.drop_index(
        op.f("ix_licenses_canonical_payload_hash"),
        table_name="licenses",
    )

    op.drop_index(
        op.f("ix_licenses_deployment_identifier"),
        table_name="licenses",
    )

    op.drop_index(
        op.f("ix_licenses_expires_at"),
        table_name="licenses",
    )

    op.drop_index(
        op.f("ix_licenses_effective_at"),
        table_name="licenses",
    )

    op.drop_index(
        op.f("ix_licenses_issued_at"),
        table_name="licenses",
    )

    op.drop_index(
        op.f("ix_licenses_license_format_version"),
        table_name="licenses",
    )

    op.drop_index(
        op.f("ix_licenses_commercial_purpose"),
        table_name="licenses",
    )

    op.drop_index(
        op.f("ix_licenses_commercial_edition"),
        table_name="licenses",
    )

    op.drop_index(
        op.f("ix_licenses_status"),
        table_name="licenses",
    )

    op.drop_index(
        op.f("ix_licenses_license_identifier"),
        table_name="licenses",
    )

    op.drop_index(
        op.f("ix_licenses_organization_id"),
        table_name="licenses",
    )

    op.drop_table("licenses")
