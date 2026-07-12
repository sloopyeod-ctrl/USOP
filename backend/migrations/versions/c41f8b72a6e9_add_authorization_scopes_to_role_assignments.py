"""add authorization scopes to role assignments

Revision ID: c41f8b72a6e9
Revises: 8f4c2a91d7b3
Create Date: 2026-07-12

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c41f8b72a6e9"
down_revision: Union[str, Sequence[str], None] = "8f4c2a91d7b3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Preserve directory and application scope on canonical role assignments.
    """

    op.add_column(
        "role_assignments",
        sa.Column(
            "directory_scope",
            sa.String(length=1024),
            nullable=True,
        ),
    )

    op.add_column(
        "role_assignments",
        sa.Column(
            "application_scope",
            sa.String(length=1024),
            nullable=True,
        ),
    )

    op.create_index(
        op.f("ix_role_assignments_directory_scope"),
        "role_assignments",
        ["directory_scope"],
        unique=False,
    )

    op.create_index(
        op.f("ix_role_assignments_application_scope"),
        "role_assignments",
        ["application_scope"],
        unique=False,
    )


def downgrade() -> None:
    """
    Remove persisted authorization scope metadata.
    """

    op.drop_index(
        op.f("ix_role_assignments_application_scope"),
        table_name="role_assignments",
    )

    op.drop_index(
        op.f("ix_role_assignments_directory_scope"),
        table_name="role_assignments",
    )

    op.drop_column(
        "role_assignments",
        "application_scope",
    )

    op.drop_column(
        "role_assignments",
        "directory_scope",
    )