import sys
import uuid
from pathlib import Path

from dotenv import load_dotenv


BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

load_dotenv(
    dotenv_path=BACKEND_ROOT / ".env",
    override=False,
)

from app.database.session import SessionLocal
from app.models.audit_event import AuditEvent
from app.models.organization import Organization
from app.schemas.organization import OrganizationCreate
from app.services.organization_service import (
    OrganizationConflictError,
    OrganizationService,
    SYSTEM_BOOTSTRAP_ACTOR,
)


def main() -> int:
    print("USOP Organization Service Regression")
    print("------------------------------------")

    db = SessionLocal()
    organization_id: str | None = None

    unique_suffix = uuid.uuid4().hex
    slug = f"service-regression-{unique_suffix}"
    deployment_identifier = (
        f"service-deployment-{unique_suffix}"
    )

    errors: list[str] = []

    try:
        service = OrganizationService(db)

        create_request = OrganizationCreate(
            name="  Organization Service Regression  ",
            slug=slug.upper(),
            primary_domain="EXAMPLE.INVALID",
            time_zone="America/New_York",
            description=(
                "Temporary Organization service record."
            ),
            external_reference=(
                f"external-{unique_suffix}"
            ),
            deployment_identifier=(
                deployment_identifier
            ),
            settings_json={
                "contains_secret": False,
                "subscription_embedded": False,
                "governance_embedded": False,
            },
        )

        organization = service.create(
            create_request
        )

        organization_id = organization.id

        if (
            organization.name
            != "Organization Service Regression"
        ):
            errors.append(
                "Organization name normalization failed."
            )

        if organization.slug != slug:
            errors.append(
                "Organization slug normalization failed."
            )

        if (
            organization.primary_domain
            != "example.invalid"
        ):
            errors.append(
                "Primary domain normalization failed."
            )

        if (
            organization.created_by
            != SYSTEM_BOOTSTRAP_ACTOR
        ):
            errors.append(
                "Server-controlled creation attribution "
                "was not persisted."
            )

        if (
            organization.updated_by
            != SYSTEM_BOOTSTRAP_ACTOR
        ):
            errors.append(
                "Server-controlled update attribution "
                "was not persisted."
            )

        by_id = service.get_by_id(
            organization.id
        )

        if by_id is None:
            errors.append(
                "Organization could not be retrieved by ID."
            )

        by_slug = service.get_by_slug(
            slug.upper()
        )

        if by_slug is None:
            errors.append(
                "Organization could not be retrieved by slug."
            )

        listed_ids = {
            item.id
            for item in service.list_all()
        }

        if organization.id not in listed_ids:
            errors.append(
                "Organization was not returned by list_all."
            )

        audit_event = (
            db.query(AuditEvent)
            .filter(
                AuditEvent.event_type
                == "OrganizationCreated",
                AuditEvent.entity_type
                == "Organization",
                AuditEvent.entity_id
                == organization.id,
            )
            .one_or_none()
        )

        if audit_event is None:
            errors.append(
                "Organization creation audit event "
                "was not persisted."
            )
        else:
            if (
                audit_event.actor
                != SYSTEM_BOOTSTRAP_ACTOR
            ):
                errors.append(
                    "Audit actor was not assigned by "
                    "the backend."
                )

            metadata = (
                audit_event.metadata_json or {}
            )

            if (
                metadata.get("actor_trust")
                != "ServerAssignedSystemActor"
            ):
                errors.append(
                    "Audit actor trust classification "
                    "was not persisted."
                )

            if metadata.get("contains_secret"):
                errors.append(
                    "Audit metadata unexpectedly "
                    "contained secret material."
                )

        duplicate_rejected = False

        try:
            service.create(
                OrganizationCreate(
                    name="Duplicate Organization",
                    slug=slug,
                    time_zone="UTC",
                )
            )
        except OrganizationConflictError:
            duplicate_rejected = True

        if not duplicate_rejected:
            errors.append(
                "Duplicate Organization slug was accepted."
            )

        if errors:
            print()
            print("Validation: FAILED")

            for error in errors:
                print(f"- {error}")

            return 1

        print(f"Organization ID: {organization.id}")
        print(f"Name: {organization.name}")
        print(f"Slug: {organization.slug}")
        print(
            "Actor: "
            f"{organization.created_by}"
        )
        print(
            "Audit event created: "
            f"{audit_event is not None}"
        )
        print(
            "Duplicate rejected: "
            f"{duplicate_rejected}"
        )

        print()
        print("Validation: PASSED")
        print(
            "Organization schema validation, "
            "persistence, service behavior, "
            "server-controlled attribution, audit "
            "integration, retrieval, and uniqueness "
            "enforcement are operating correctly."
        )

        return 0

    finally:
        if organization_id:
            (
                db.query(AuditEvent)
                .filter(
                    AuditEvent.entity_type
                    == "Organization",
                    AuditEvent.entity_id
                    == organization_id,
                )
                .delete(
                    synchronize_session=False
                )
            )

            (
                db.query(Organization)
                .filter(
                    Organization.id
                    == organization_id,
                )
                .delete(
                    synchronize_session=False
                )
            )

            db.commit()

        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
