from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.domain.license_status import LicenseStatus
from app.models.license import License
from app.repositories.license_repository import (
    LicenseRepository,
)
from app.repositories.organization_repository import (
    OrganizationRepository,
)
from app.schemas.license import (
    LicenseInstallDisposition,
    LicenseInstallRequest,
    LicenseInstallResult,
)
from app.services.audit_service import AuditService


SYSTEM_LICENSE_INSTALLER = "USOP System Bootstrap"


class LicenseInstallationError(ValueError):
    """Base exception for structural License installation failures."""


class LicenseOrganizationNotFoundError(
    LicenseInstallationError
):
    """Raised when the License references an unknown Organization."""


class LicenseOrganizationConflictError(
    LicenseInstallationError
):
    """Raised when a License identifier is bound to another Organization."""


class LicenseDeploymentBindingError(
    LicenseInstallationError
):
    """Raised when License and Organization deployment bindings conflict."""


class LicenseService:
    """
    Backend authority for immutable License installation.

    This service performs structural installation only. It does not verify
    signatures or derive effective Subscription State.
    """

    def __init__(self, db: Session):
        self.db = db
        self.repository = LicenseRepository(db)
        self.organization_repository = OrganizationRepository(
            db
        )
        self.audit_service = AuditService(db)

    def install(
        self,
        data: LicenseInstallRequest,
        actor: str = SYSTEM_LICENSE_INSTALLER,
    ) -> LicenseInstallResult:
        organization = (
            self.organization_repository.get_by_id(
                data.organization_id
            )
        )

        if organization is None:
            raise LicenseOrganizationNotFoundError(
                "The License references an unknown Organization."
            )

        existing = self.repository.get_by_identifier(
            data.license_identifier
        )

        if existing is not None:
            if existing.organization_id != organization.id:
                raise LicenseOrganizationConflictError(
                    "This License identifier is already bound "
                    "to another Organization."
                )

            return LicenseInstallResult(
                license_id=existing.id,
                license_identifier=(
                    existing.license_identifier
                ),
                organization_id=existing.organization_id,
                disposition=(
                    LicenseInstallDisposition
                    .ALREADY_INSTALLED
                ),
                superseded_license_id=(
                    existing.supersedes_license_id
                ),
                audit_event_id=None,
            )

        if (
            data.deployment_identifier
            and organization.deployment_identifier
            and data.deployment_identifier
            != organization.deployment_identifier
        ):
            raise LicenseDeploymentBindingError(
                "The License deployment binding does not match "
                "the Organization deployment identifier."
            )

        previous_license = (
            self.repository
            .get_latest_issued_for_organization(
                organization.id
            )
        )

        previous_license_id = (
            previous_license.id
            if previous_license is not None
            else None
        )

        try:
            if previous_license is not None:
                previous_license.status = (
                    LicenseStatus.SUPERSEDED.value
                )
                previous_license.updated_by = actor
                self.db.flush()

            license_record = License(
                organization_id=organization.id,
                license_identifier=(
                    data.license_identifier
                ),
                status=LicenseStatus.ISSUED.value,
                commercial_edition=(
                    data.commercial_edition.value
                ),
                commercial_purpose=(
                    data.commercial_purpose.value
                ),
                license_format_version=(
                    data.license_format_version
                ),
                issued_at=data.issued_at,
                effective_at=data.effective_at,
                expires_at=data.expires_at,
                deployment_identifier=(
                    data.deployment_identifier
                ),
                seat_limit=data.seat_limit,
                commercial_modules_json=(
                    data.commercial_modules
                ),
                feature_entitlements_json=(
                    data.feature_entitlements
                ),
                canonical_payload_json=(
                    data.canonical_payload
                ),
                canonical_payload_hash=(
                    data.canonical_payload_hash.lower()
                ),
                signature=data.signature,
                signing_key_identifier=(
                    data.signing_key_identifier
                ),
                supersedes_license_id=(
                    previous_license_id
                ),
                created_by=actor,
                updated_by=actor,
            )

            license_record = self.repository.create(
                license_record
            )

            audit_event = (
                self.audit_service.record_pending(
                    event_type="LicenseInstalled",
                    entity_type="License",
                    entity_id=license_record.id,
                    actor=actor,
                    message=(
                        f"License "
                        f"'{license_record.license_identifier}' "
                        "was installed."
                    ),
                    metadata={
                        "organization_id": (
                            organization.id
                        ),
                        "license_identifier": (
                            license_record
                            .license_identifier
                        ),
                        "commercial_edition": (
                            license_record
                            .commercial_edition
                        ),
                        "commercial_purpose": (
                            license_record
                            .commercial_purpose
                        ),
                        "superseded_license_id": (
                            previous_license_id
                        ),
                        "deployment_bound": bool(
                            license_record
                            .deployment_identifier
                        ),
                        "cryptographic_validation": (
                            "NotYetPerformed"
                        ),
                        "actor_trust": (
                            "ServerAssignedSystemActor"
                        ),
                    },
                )
            )

            self.db.commit()
            self.db.refresh(license_record)
            self.db.refresh(audit_event)

            return LicenseInstallResult(
                license_id=license_record.id,
                license_identifier=(
                    license_record.license_identifier
                ),
                organization_id=(
                    license_record.organization_id
                ),
                disposition=(
                    LicenseInstallDisposition.INSTALLED
                ),
                superseded_license_id=(
                    previous_license_id
                ),
                audit_event_id=audit_event.id,
            )

        except IntegrityError as error:
            self.db.rollback()

            existing = (
                self.repository.get_by_identifier(
                    data.license_identifier
                )
            )

            if (
                existing is not None
                and existing.organization_id
                == organization.id
            ):
                return LicenseInstallResult(
                    license_id=existing.id,
                    license_identifier=(
                        existing.license_identifier
                    ),
                    organization_id=(
                        existing.organization_id
                    ),
                    disposition=(
                        LicenseInstallDisposition
                        .ALREADY_INSTALLED
                    ),
                    superseded_license_id=(
                        existing.supersedes_license_id
                    ),
                    audit_event_id=None,
                )

            raise LicenseInstallationError(
                "License installation violated a persistence constraint."
            ) from error

        except Exception:
            self.db.rollback()
            raise
