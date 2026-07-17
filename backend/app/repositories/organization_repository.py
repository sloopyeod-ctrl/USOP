from sqlalchemy.orm import Session

from app.models.organization import Organization


class OrganizationRepository:
    """
    Persistence boundary for canonical USOP Organizations.
    """

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        organization: Organization,
    ) -> Organization:
        self.db.add(organization)
        self.db.commit()
        self.db.refresh(organization)

        return organization

    def list_all(self) -> list[Organization]:
        return (
            self.db.query(Organization)
            .order_by(
                Organization.name.asc(),
                Organization.id.asc(),
            )
            .all()
        )

    def get_by_id(
        self,
        organization_id: str,
    ) -> Organization | None:
        return (
            self.db.query(Organization)
            .filter(
                Organization.id == organization_id,
            )
            .one_or_none()
        )

    def get_by_slug(
        self,
        slug: str,
    ) -> Organization | None:
        return (
            self.db.query(Organization)
            .filter(
                Organization.slug == slug,
            )
            .one_or_none()
        )

    def get_by_deployment_identifier(
        self,
        deployment_identifier: str,
    ) -> Organization | None:
        return (
            self.db.query(Organization)
            .filter(
                Organization.deployment_identifier
                == deployment_identifier,
            )
            .one_or_none()
        )

    def get_by_id_for_update(
        self,
        organization_id: str,
    ) -> Organization | None:
        """
        Retrieve and lock one Organization for a caller-owned transaction.

        Bootstrap uses this row lock to serialize concurrent first-user
        creation attempts for the same Organization.
        """

        return (
            self.db.query(Organization)
            .filter(
                Organization.id == organization_id,
            )
            .with_for_update()
            .one_or_none()
        )
