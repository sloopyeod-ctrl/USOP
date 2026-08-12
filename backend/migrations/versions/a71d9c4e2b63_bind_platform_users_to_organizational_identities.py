"""bind platform users to organizational identities

Revision ID: a71d9c4e2b63
Revises: 6b3f9a2d1c74
Create Date: 2026-08-12
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a71d9c4e2b63"
down_revision: Union[str, Sequence[str], None] = "6b3f9a2d1c74"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "platform_users",
        sa.Column(
            "organizational_identity_id",
            sa.String(length=36),
            nullable=True,
        ),
    )
    op.create_index(
        "ix_platform_users_organizational_identity_id",
        "platform_users",
        ["organizational_identity_id"],
        unique=False,
    )
    op.create_foreign_key(
        "fk_platform_users_organizational_identity_id",
        "platform_users",
        "organizational_identities",
        ["organizational_identity_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_platform_users_organizational_identity_id",
        "platform_users",
        type_="foreignkey",
    )
    op.drop_index(
        "ix_platform_users_organizational_identity_id",
        table_name="platform_users",
    )
    op.drop_column(
        "platform_users",
        "organizational_identity_id",
    )
