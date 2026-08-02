from sqlalchemy.orm import Session

from app.models.organizational_identity import OrganizationalIdentity


class OrganizationalIdentityRepository:
    """
    Persistence boundary for Organization-owned identity placement.

    Every read method requires Organization context so callers cannot
    accidentally query OrganizationalIdentity as a global collection.
    """

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        organizational_identity: OrganizationalIdentity,
    ) -> OrganizationalIdentity:
        self.db.add(organizational_identity)
        self.db.flush()

        return organizational_identity

    def list_for_organization(
        self,
        organization_id: str,
    ) -> list[OrganizationalIdentity]:
        return (
            self.db.query(OrganizationalIdentity)
            .filter(
                OrganizationalIdentity.organization_id
                == organization_id,
                OrganizationalIdentity.is_active.is_(True),
            )
            .order_by(
                OrganizationalIdentity.display_name.asc(),
                OrganizationalIdentity.id.asc(),
            )
            .all()
        )

    def get_by_id_for_organization(
        self,
        *,
        organization_id: str,
        organizational_identity_id: str,
    ) -> OrganizationalIdentity | None:
        return (
            self.db.query(OrganizationalIdentity)
            .filter(
                OrganizationalIdentity.organization_id
                == organization_id,
                OrganizationalIdentity.id
                == organizational_identity_id,
                OrganizationalIdentity.is_active.is_(True),
            )
            .one_or_none()
        )

    def get_for_identity(
        self,
        *,
        organization_id: str,
        identity_id: str,
    ) -> OrganizationalIdentity | None:
        return (
            self.db.query(OrganizationalIdentity)
            .filter(
                OrganizationalIdentity.organization_id
                == organization_id,
                OrganizationalIdentity.identity_id
                == identity_id,
            )
            .one_or_none()
        )
