"""Generalize membership relationships

Revision ID: 8f4c2a91d7b3
Revises: de646e9a52eb
Create Date: 2026-07-10

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "8f4c2a91d7b3"
down_revision: Union[str, Sequence[str], None] = "de646e9a52eb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Replace the account-specific membership reference with a canonical
    polymorphic subject reference.

    Existing account memberships are preserved as:

    subject_type = Account
    subject_id = existing account_id
    """

    op.add_column(
        "memberships",
        sa.Column(
            "subject_type",
            sa.String(length=100),
            nullable=True,
        ),
    )

    op.add_column(
        "memberships",
        sa.Column(
            "subject_id",
            sa.String(length=36),
            nullable=True,
        ),
    )

    op.execute(
        """
        UPDATE memberships
        SET
            subject_type = 'Account',
            subject_id = account_id
        """
    )

    connection = op.get_bind()

    incomplete_rows = connection.execute(
        sa.text(
            """
            SELECT COUNT(*)
            FROM memberships
            WHERE subject_type IS NULL
               OR subject_id IS NULL
            """
        )
    ).scalar_one()

    if incomplete_rows:
        raise RuntimeError(
            "Membership migration could not populate every canonical "
            "subject reference."
        )

    op.alter_column(
        "memberships",
        "subject_type",
        existing_type=sa.String(length=100),
        nullable=False,
    )

    op.alter_column(
        "memberships",
        "subject_id",
        existing_type=sa.String(length=36),
        nullable=False,
    )

    op.create_index(
        op.f("ix_memberships_subject_type"),
        "memberships",
        ["subject_type"],
        unique=False,
    )

    op.create_index(
        op.f("ix_memberships_subject_id"),
        "memberships",
        ["subject_id"],
        unique=False,
    )

    op.drop_constraint(
        "memberships_account_id_fkey",
        "memberships",
        type_="foreignkey",
    )

    op.drop_index(
        op.f("ix_memberships_account_id"),
        table_name="memberships",
    )

    op.drop_column(
        "memberships",
        "account_id",
    )


def downgrade() -> None:
    """
    Restore the original account-specific membership structure.

    Downgrade is intentionally blocked when non-account memberships exist
    because those relationships cannot be represented by account_id without
    losing data.
    """

    connection = op.get_bind()

    non_account_rows = connection.execute(
        sa.text(
            """
            SELECT COUNT(*)
            FROM memberships
            WHERE subject_type <> 'Account'
            """
        )
    ).scalar_one()

    if non_account_rows:
        raise RuntimeError(
            "Cannot downgrade generalized memberships while non-account "
            "principal memberships exist."
        )

    op.add_column(
        "memberships",
        sa.Column(
            "account_id",
            sa.String(length=36),
            nullable=True,
        ),
    )

    op.execute(
        """
        UPDATE memberships
        SET account_id = subject_id
        WHERE subject_type = 'Account'
        """
    )

    incomplete_rows = connection.execute(
        sa.text(
            """
            SELECT COUNT(*)
            FROM memberships
            WHERE account_id IS NULL
            """
        )
    ).scalar_one()

    if incomplete_rows:
        raise RuntimeError(
            "Membership downgrade could not restore every account reference."
        )

    op.alter_column(
        "memberships",
        "account_id",
        existing_type=sa.String(length=36),
        nullable=False,
    )

    op.create_foreign_key(
        "memberships_account_id_fkey",
        "memberships",
        "accounts",
        ["account_id"],
        ["id"],
    )

    op.create_index(
        op.f("ix_memberships_account_id"),
        "memberships",
        ["account_id"],
        unique=False,
    )

    op.drop_index(
        op.f("ix_memberships_subject_id"),
        table_name="memberships",
    )

    op.drop_index(
        op.f("ix_memberships_subject_type"),
        table_name="memberships",
    )

    op.drop_column(
        "memberships",
        "subject_id",
    )

    op.drop_column(
        "memberships",
        "subject_type",
    )