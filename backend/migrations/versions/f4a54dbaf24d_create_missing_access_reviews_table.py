"""Create access reviews table v3.

Revision ID: f4a54dbaf24d
Revises: 0e30cb831334
Create Date: 2026-07-05 10:50:20.218386

Historical compatibility revision.

The preceding revision, 0e30cb831334, already creates the access_reviews
table with the schema this revision originally attempted to create again.
This revision is intentionally retained in the Alembic chain so databases
that have recorded this revision remain compatible, but it performs no
schema operation.
"""

from typing import Sequence, Union

revision: str = "f4a54dbaf24d"
down_revision: Union[str, Sequence[str], None] = "0e30cb831334"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Preserve historical revision identity without duplicating schema."""
    pass


def downgrade() -> None:
    """No schema change was introduced by this compatibility revision."""
    pass
