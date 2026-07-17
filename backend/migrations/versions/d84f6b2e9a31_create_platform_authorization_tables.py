"""create platform authorization tables

Revision ID: d84f6b2e9a31
Revises: c73e5a91d4f2
Create Date: 2026-07-16
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "d84f6b2e9a31"
down_revision: str | None = "c73e5a91d4f2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "platform_permissions",
        sa.Column(
            "permission_key",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "name",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "description",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "resource",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "action",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "is_system_permission",
            sa.Boolean(),
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
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "permission_key",
            name="uq_platform_permissions_permission_key",
        ),
        sa.UniqueConstraint(
            "resource",
            "action",
            name="uq_platform_permissions_resource_action",
        ),
    )

    op.create_index(
        op.f("ix_platform_permissions_permission_key"),
        "platform_permissions",
        ["permission_key"],
        unique=True,
    )

    op.create_index(
        op.f("ix_platform_permissions_name"),
        "platform_permissions",
        ["name"],
        unique=False,
    )

    op.create_index(
        op.f("ix_platform_permissions_resource"),
        "platform_permissions",
        ["resource"],
        unique=False,
    )

    op.create_index(
        op.f("ix_platform_permissions_action"),
        "platform_permissions",
        ["action"],
        unique=False,
    )

    op.create_table(
        "platform_roles",
        sa.Column(
            "organization_id",
            sa.String(length=36),
            nullable=False,
        ),
        sa.Column(
            "role_key",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "name",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "description",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "status",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "is_system_role",
            sa.Boolean(),
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
            "role_key",
            name="uq_platform_roles_organization_role_key",
        ),
    )

    op.create_index(
        op.f("ix_platform_roles_organization_id"),
        "platform_roles",
        ["organization_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_platform_roles_role_key"),
        "platform_roles",
        ["role_key"],
        unique=False,
    )

    op.create_index(
        op.f("ix_platform_roles_name"),
        "platform_roles",
        ["name"],
        unique=False,
    )

    op.create_index(
        op.f("ix_platform_roles_status"),
        "platform_roles",
        ["status"],
        unique=False,
    )

    op.create_table(
        "platform_role_permissions",
        sa.Column(
            "organization_id",
            sa.String(length=36),
            nullable=False,
        ),
        sa.Column(
            "platform_role_id",
            sa.String(length=36),
            nullable=False,
        ),
        sa.Column(
            "platform_permission_id",
            sa.String(length=36),
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
        sa.ForeignKeyConstraint(
            ["platform_role_id"],
            ["platform_roles.id"],
        ),
        sa.ForeignKeyConstraint(
            ["platform_permission_id"],
            ["platform_permissions.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "platform_role_id",
            "platform_permission_id",
            name=(
                "uq_platform_role_permissions_"
                "role_permission"
            ),
        ),
    )

    op.create_index(
        op.f(
            "ix_platform_role_permissions_"
            "organization_id"
        ),
        "platform_role_permissions",
        ["organization_id"],
        unique=False,
    )

    op.create_index(
        op.f(
            "ix_platform_role_permissions_"
            "platform_role_id"
        ),
        "platform_role_permissions",
        ["platform_role_id"],
        unique=False,
    )

    op.create_index(
        op.f(
            "ix_platform_role_permissions_"
            "platform_permission_id"
        ),
        "platform_role_permissions",
        ["platform_permission_id"],
        unique=False,
    )

    op.create_table(
        "platform_role_assignments",
        sa.Column(
            "organization_id",
            sa.String(length=36),
            nullable=False,
        ),
        sa.Column(
            "platform_user_id",
            sa.String(length=36),
            nullable=False,
        ),
        sa.Column(
            "platform_role_id",
            sa.String(length=36),
            nullable=False,
        ),
        sa.Column(
            "assigned_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "expires_at",
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
        sa.ForeignKeyConstraint(
            ["platform_user_id"],
            ["platform_users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["platform_role_id"],
            ["platform_roles.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "platform_user_id",
            "platform_role_id",
            name=(
                "uq_platform_role_assignments_"
                "user_role"
            ),
        ),
    )

    op.create_index(
        op.f(
            "ix_platform_role_assignments_"
            "organization_id"
        ),
        "platform_role_assignments",
        ["organization_id"],
        unique=False,
    )

    op.create_index(
        op.f(
            "ix_platform_role_assignments_"
            "platform_user_id"
        ),
        "platform_role_assignments",
        ["platform_user_id"],
        unique=False,
    )

    op.create_index(
        op.f(
            "ix_platform_role_assignments_"
            "platform_role_id"
        ),
        "platform_role_assignments",
        ["platform_role_id"],
        unique=False,
    )

    op.create_index(
        op.f(
            "ix_platform_role_assignments_"
            "assigned_at"
        ),
        "platform_role_assignments",
        ["assigned_at"],
        unique=False,
    )

    op.create_index(
        op.f(
            "ix_platform_role_assignments_"
            "expires_at"
        ),
        "platform_role_assignments",
        ["expires_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f(
            "ix_platform_role_assignments_"
            "expires_at"
        ),
        table_name="platform_role_assignments",
    )

    op.drop_index(
        op.f(
            "ix_platform_role_assignments_"
            "assigned_at"
        ),
        table_name="platform_role_assignments",
    )

    op.drop_index(
        op.f(
            "ix_platform_role_assignments_"
            "platform_role_id"
        ),
        table_name="platform_role_assignments",
    )

    op.drop_index(
        op.f(
            "ix_platform_role_assignments_"
            "platform_user_id"
        ),
        table_name="platform_role_assignments",
    )

    op.drop_index(
        op.f(
            "ix_platform_role_assignments_"
            "organization_id"
        ),
        table_name="platform_role_assignments",
    )

    op.drop_table("platform_role_assignments")

    op.drop_index(
        op.f(
            "ix_platform_role_permissions_"
            "platform_permission_id"
        ),
        table_name="platform_role_permissions",
    )

    op.drop_index(
        op.f(
            "ix_platform_role_permissions_"
            "platform_role_id"
        ),
        table_name="platform_role_permissions",
    )

    op.drop_index(
        op.f(
            "ix_platform_role_permissions_"
            "organization_id"
        ),
        table_name="platform_role_permissions",
    )

    op.drop_table("platform_role_permissions")

    op.drop_index(
        op.f("ix_platform_roles_status"),
        table_name="platform_roles",
    )

    op.drop_index(
        op.f("ix_platform_roles_name"),
        table_name="platform_roles",
    )

    op.drop_index(
        op.f("ix_platform_roles_role_key"),
        table_name="platform_roles",
    )

    op.drop_index(
        op.f("ix_platform_roles_organization_id"),
        table_name="platform_roles",
    )

    op.drop_table("platform_roles")

    op.drop_index(
        op.f("ix_platform_permissions_action"),
        table_name="platform_permissions",
    )

    op.drop_index(
        op.f("ix_platform_permissions_resource"),
        table_name="platform_permissions",
    )

    op.drop_index(
        op.f("ix_platform_permissions_name"),
        table_name="platform_permissions",
    )

    op.drop_index(
        op.f("ix_platform_permissions_permission_key"),
        table_name="platform_permissions",
    )

    op.drop_table("platform_permissions")
