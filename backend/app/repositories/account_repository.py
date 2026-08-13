from sqlalchemy.orm import Session

from app.models.account import Account
from app.models.organizational_identity import OrganizationalIdentity
from app.repositories.base_repository import BaseRepository
from app.schemas.account import AccountCreate


class AccountRepository(BaseRepository[Account, AccountCreate]):
    def __init__(self, db: Session):
        super().__init__(db, Account)

    def list_by_source_for_organization(
        self,
        *,
        organization_id: str,
        source_system: str,
        source_identifier: str,
    ) -> list[Account]:
        """
        Return active Accounts matching durable provider evidence inside one
        active Organization.
        """

        organization_id = str(organization_id or "").strip()
        source_system = str(source_system or "").strip()
        source_identifier = str(source_identifier or "").strip()

        if not organization_id or not source_system or not source_identifier:
            return []

        return (
            self.db.query(Account)
            .join(
                OrganizationalIdentity,
                Account.organizational_identity_id
                == OrganizationalIdentity.id,
            )
            .filter(
                OrganizationalIdentity.organization_id
                == organization_id,
                OrganizationalIdentity.is_active.is_(True),
                Account.is_active.is_(True),
                Account.source_system == source_system,
                Account.source_identifier == source_identifier,
            )
            .order_by(
                Account.created_at.asc(),
                Account.id.asc(),
            )
            .all()
        )
