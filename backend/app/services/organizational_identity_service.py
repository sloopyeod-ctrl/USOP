from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.organizational_identity import OrganizationalIdentity
from app.repositories.identity_repository import IdentityRepository
from app.repositories.organization_repository import OrganizationRepository
from app.repositories.organizational_identity_repository import (
    OrganizationalIdentityRepository,
)
from app.schemas.organizational_identity import (
    OrganizationalIdentityCreate,
)


class OrganizationalIdentityError(Exception):
    """Base service error for OrganizationalIdentity operations."""


class OrganizationalIdentityOrganizationNotFoundError(
    OrganizationalIdentityError
):
    """Raised when the requested Organization does not exist."""


class OrganizationalIdentityIdentityNotFoundError(
    OrganizationalIdentityError
):
    """Raised when the requested canonical Identity does not exist."""


class OrganizationalIdentityConflictError(
    OrganizationalIdentityError
):
    """Raised when the Identity is already placed in the Organization."""


class OrganizationalIdentityService:
    """
    Organization-safe orchestration for canonical identity placement.
    """

    def __init__(
        self,
        db: Session,
        *,
        repository: OrganizationalIdentityRepository | None = None,
        organization_repository: OrganizationRepository | None = None,
        identity_repository: IdentityRepository | None = None,
    ):
        self.db = db
        self.repository = (
            repository
            or OrganizationalIdentityRepository(db)
        )
        self.organization_repository = (
            organization_repository
            or OrganizationRepository(db)
        )
        self.identity_repository = (
            identity_repository
            or IdentityRepository(db)
        )

    def create(
        self,
        *,
        organization_id: str,
        data: OrganizationalIdentityCreate,
        actor: str | None = None,
    ) -> OrganizationalIdentity:
        organization = (
            self.organization_repository.get_by_id(
                organization_id
            )
        )

        if organization is None:
            raise (
                OrganizationalIdentityOrganizationNotFoundError(
                    "The OrganizationalIdentity references "
                    "an unknown Organization."
                )
            )

        identity = self.identity_repository.get_by_id(
            data.identity_id
        )

        if identity is None:
            raise OrganizationalIdentityIdentityNotFoundError(
                "The OrganizationalIdentity references "
                "an unknown canonical Identity."
            )

        existing = self.repository.get_for_identity(
            organization_id=organization.id,
            identity_id=identity.id,
        )

        if existing is not None:
            raise OrganizationalIdentityConflictError(
                "This canonical Identity is already placed "
                "in the requested Organization."
            )

        organizational_identity = OrganizationalIdentity(
            organization_id=organization.id,
            identity_id=identity.id,
            display_name=(
                data.display_name
                or identity.display_name
            ),
            status=data.status,
            created_by=actor,
            updated_by=actor,
        )

        try:
            organizational_identity = (
                self.repository.create(
                    organizational_identity
                )
            )

            self.db.commit()
            self.db.refresh(
                organizational_identity
            )

            return organizational_identity

        except IntegrityError as error:
            self.db.rollback()

            raise OrganizationalIdentityConflictError(
                "This canonical Identity is already placed "
                "in the requested Organization."
            ) from error

        except Exception:
            self.db.rollback()
            raise

    def list_for_organization(
        self,
        organization_id: str,
    ) -> list[OrganizationalIdentity]:
        organization = (
            self.organization_repository.get_by_id(
                organization_id
            )
        )

        if organization is None:
            raise (
                OrganizationalIdentityOrganizationNotFoundError(
                    "The OrganizationalIdentity query references "
                    "an unknown Organization."
                )
            )

        return self.repository.list_for_organization(
            organization.id
        )

    def get_by_id(
        self,
        *,
        organization_id: str,
        organizational_identity_id: str,
    ) -> OrganizationalIdentity | None:
        organization = (
            self.organization_repository.get_by_id(
                organization_id
            )
        )

        if organization is None:
            raise (
                OrganizationalIdentityOrganizationNotFoundError(
                    "The OrganizationalIdentity query references "
                    "an unknown Organization."
                )
            )

        return (
            self.repository.get_by_id_for_organization(
                organization_id=organization.id,
                organizational_identity_id=(
                    organizational_identity_id
                ),
            )
        )
