"""create platform users table

Revision ID: c73e5a91d4f2
Revises: b42f7d91c6a8
Create Date: 2026-07-16
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "c73e5a91d4f2"
down_revision: str | None = "b42f7d91c6a8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "platform_users",
        sa.Column(
            "organization_id",
            sa.String(length=36),
            nullable=False,
        ),
        sa.Column(
            "display_name",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "email",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "identity_provider",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "external_tenant_id",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "external_subject_id",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "identity_issuer",
            sa.String(length=1024),
            nullable=True,
        ),
        sa.Column(
            "created_via_bootstrap",
            sa.Boolean(),
            nullable=False,
        ),
        sa.Column(
            "invited_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "activated_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "last_authenticated_at",
            sa.DateTime(timezone=True),
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
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "organization_id",
            "identity_provider",
            "external_tenant_id",
            "external_subject_id",
            name=(
                "uq_platform_users_organization_"
                "provider_tenant_subject"
            ),
        ),
    )

    op.create_index(
        op.f("ix_platform_users_organization_id"),
        "platform_users",
        ["organization_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_platform_users_display_name"),
        "platform_users",
        ["display_name"],
        unique=False,
    )

    op.create_index(
        op.f("ix_platform_users_email"),
        "platform_users",
        ["email"],
        unique=False,
    )

    op.create_index(
        op.f("ix_platform_users_status"),
        "platform_users",
        ["status"],
        unique=False,
    )

    op.create_index(
        op.f("ix_platform_users_identity_provider"),
        "platform_users",
        ["identity_provider"],
        unique=False,
    )

    op.create_index(
        op.f("ix_platform_users_external_tenant_id"),
        "platform_users",
        ["external_tenant_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_platform_users_external_subject_id"),
        "platform_users",
        ["external_subject_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_platform_users_external_subject_id"),
        table_name="platform_users",
    )

    op.drop_index(
        op.f("ix_platform_users_external_tenant_id"),
        table_name="platform_users",
    )

    op.drop_index(
        op.f("ix_platform_users_identity_provider"),
        table_name="platform_users",
    )

    op.drop_index(
        op.f("ix_platform_users_status"),
        table_name="platform_users",
    )

    op.drop_index(
        op.f("ix_platform_users_email"),
        table_name="platform_users",
    )

    op.drop_index(
        op.f("ix_platform_users_display_name"),
        table_name="platform_users",
    )

    op.drop_index(
        op.f("ix_platform_users_organization_id"),
        table_name="platform_users",
    )

    op.drop_table("platform_users")
