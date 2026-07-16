from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.organization import Organization
from app.repositories.organization_repository import (
    OrganizationRepository,
)
from app.schemas.organization import OrganizationCreate
from app.services.audit_service import AuditService


SYSTEM_BOOTSTRAP_ACTOR = "USOP System Bootstrap"


class OrganizationConflictError(ValueError):
    """
    Raised when Organization uniqueness would be violated.
    """


class OrganizationService:
    """
    Backend authority for canonical Organization operations.

    Until authenticated Platform Users are introduced, Organization creation
    is attributed to the server-controlled bootstrap actor. The API never
    accepts actor attribution from the browser.
    """

    def __init__(self, db: Session):
        self.db = db
        self.repository = OrganizationRepository(db)
        self.audit_service = AuditService(db)

    def create(
        self,
        data: OrganizationCreate,
        actor: str = SYSTEM_BOOTSTRAP_ACTOR,
    ) -> Organization:
        existing_slug = self.repository.get_by_slug(
            data.slug
        )

        if existing_slug is not None:
            raise OrganizationConflictError(
                "An Organization with this slug already exists."
            )

        if data.deployment_identifier:
            existing_deployment = (
                self.repository
                .get_by_deployment_identifier(
                    data.deployment_identifier
                )
            )

            if existing_deployment is not None:
                raise OrganizationConflictError(
                    "This deployment identifier is already "
                    "assigned to another Organization."
                )

        organization = Organization(
            name=data.name,
            slug=data.slug,
            status=data.status.value,
            organization_type=(
                data.organization_type.value
            ),
            primary_domain=data.primary_domain,
            time_zone=data.time_zone,
            description=data.description,
            external_reference=data.external_reference,
            deployment_identifier=(
                data.deployment_identifier
            ),
            settings_json=data.settings_json,
            created_by=actor,
            updated_by=actor,
        )

        try:
            organization = self.repository.create(
                organization
            )
        except IntegrityError as error:
            self.db.rollback()

            raise OrganizationConflictError(
                "Organization uniqueness validation failed."
            ) from error

        self.audit_service.record(
            event_type="OrganizationCreated",
            entity_type="Organization",
            entity_id=organization.id,
            actor=actor,
            message=(
                f"Organization '{organization.name}' "
                "was created."
            ),
            metadata={
                "organization_slug": organization.slug,
                "organization_type": (
                    organization.organization_type
                ),
                "status": organization.status,
                "primary_domain": (
                    organization.primary_domain
                ),
                "deployment_bound": bool(
                    organization.deployment_identifier
                ),
                "actor_trust": "ServerAssignedSystemActor",
            },
        )

        return organization

    def list_all(self) -> list[Organization]:
        return self.repository.list_all()

    def get_by_id(
        self,
        organization_id: str,
    ) -> Organization | None:
        return self.repository.get_by_id(
            organization_id
        )

    def get_by_slug(
        self,
        slug: str,
    ) -> Organization | None:
        return self.repository.get_by_slug(
            slug.strip().lower()
        )
