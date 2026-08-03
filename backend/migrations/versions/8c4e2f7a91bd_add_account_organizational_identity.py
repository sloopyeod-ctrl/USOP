"""add account organizational identity ownership

Revision ID: 8c4e2f7a91bd
Revises: 730ae1d62204
Create Date: 2026-08-02
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "8c4e2f7a91bd"
down_revision: Union[str, Sequence[str], None] = "730ae1d62204"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "accounts",
        sa.Column(
            "organizational_identity_id",
            sa.String(length=36),
            nullable=True,
        ),
    )
    op.create_foreign_key(
        "fk_accounts_organizational_identity_id",
        "accounts",
        "organizational_identities",
        ["organizational_identity_id"],
        ["id"],
    )
    op.create_index(
        "ix_accounts_organizational_identity_id",
        "accounts",
        ["organizational_identity_id"],
        unique=False,
    )
    op.execute(
        """
        UPDATE accounts AS account
        SET organizational_identity_id = resolved.organizational_identity_id
        FROM (
            SELECT
                account_candidate.id AS account_id,
                MIN(organizational_identity.id)
                    AS organizational_identity_id
            FROM accounts AS account_candidate
            JOIN organizational_identities AS organizational_identity
                ON organizational_identity.identity_id
                    = account_candidate.identity_id
            WHERE account_candidate.identity_id IS NOT NULL
              AND organizational_identity.is_active IS TRUE
            GROUP BY account_candidate.id
            HAVING COUNT(organizational_identity.id) = 1
        ) AS resolved
        WHERE account.id = resolved.account_id
        """
    )


def downgrade() -> None:
    op.drop_index(
        "ix_accounts_organizational_identity_id",
        table_name="accounts",
    )
    op.drop_constraint(
        "fk_accounts_organizational_identity_id",
        "accounts",
        type_="foreignkey",
    )
    op.drop_column("accounts", "organizational_identity_id")
