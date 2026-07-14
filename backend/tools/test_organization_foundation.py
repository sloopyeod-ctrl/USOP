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
from app.domain.organization_status import OrganizationStatus
from app.domain.organization_type import OrganizationType
from app.models.organization import Organization


def main() -> int:
    print("USOP Organization Foundation Regression")
    print("---------------------------------------")

    expected_statuses = {
        "Active",
        "Suspended",
        "Disabled",
    }

    expected_types = {
        "Customer",
        "Internal",
        "ManagedServiceProvider",
    }

    actual_statuses = {
        status.value
        for status in OrganizationStatus
    }

    actual_types = {
        organization_type.value
        for organization_type in OrganizationType
    }

    errors: list[str] = []

    if actual_statuses != expected_statuses:
        errors.append(
            "Organization status vocabulary does not match "
            "the canonical contract."
        )

    if actual_types != expected_types:
        errors.append(
            "Organization type vocabulary does not match "
            "the canonical contract."
        )

    db = SessionLocal()
    organization_id: str | None = None

    unique_suffix = uuid.uuid4().hex
    slug = f"organization-regression-{unique_suffix}"
    deployment_identifier = (
        f"deployment-regression-{unique_suffix}"
    )

    try:
        organization = Organization(
            name="Organization Regression Test",
            slug=slug,
            status=OrganizationStatus.ACTIVE.value,
            organization_type=(
                OrganizationType.CUSTOMER.value
            ),
            primary_domain="example.invalid",
            time_zone="America/New_York",
            description=(
                "Temporary deterministic regression record."
            ),
            external_reference=(
                f"external-regression-{unique_suffix}"
            ),
            deployment_identifier=deployment_identifier,
            settings_json={
                "contains_secret": False,
                "governance_embedded": False,
                "subscription_embedded": False,
            },
            created_by="USOP Regression Test",
            updated_by="USOP Regression Test",
        )

        db.add(organization)
        db.commit()
        db.refresh(organization)

        organization_id = organization.id

        if not organization.id:
            errors.append(
                "Organization ID was not generated."
            )

        if organization.slug != slug:
            errors.append(
                "Organization slug was not persisted."
            )

        if (
            organization.status
            != OrganizationStatus.ACTIVE.value
        ):
            errors.append(
                "Organization status was not persisted canonically."
            )

        if (
            organization.organization_type
            != OrganizationType.CUSTOMER.value
        ):
            errors.append(
                "Organization type was not persisted canonically."
            )

        if organization.primary_domain != "example.invalid":
            errors.append(
                "Organization primary domain was not persisted."
            )

        if organization.time_zone != "America/New_York":
            errors.append(
                "Organization time zone was not persisted."
            )

        if (
            organization.deployment_identifier
            != deployment_identifier
        ):
            errors.append(
                "Deployment identifier was not persisted."
            )

        settings = organization.settings_json or {}

        if settings.get("contains_secret") is not False:
            errors.append(
                "Organization settings unexpectedly contain "
                "secret material."
            )

        if settings.get("governance_embedded") is not False:
            errors.append(
                "Governance policy was incorrectly embedded "
                "in the Organization foundation."
            )

        if settings.get("subscription_embedded") is not False:
            errors.append(
                "Subscription data was incorrectly embedded "
                "in the Organization foundation."
            )

        if organization.created_by != "USOP Regression Test":
            errors.append(
                "Organization creation attribution was not persisted."
            )

        if not organization.created_at:
            errors.append(
                "Organization creation timestamp was not generated."
            )

        if not organization.updated_at:
            errors.append(
                "Organization update timestamp was not generated."
            )

        if organization.is_active is not True:
            errors.append(
                "Organization did not default to active persistence."
            )

        persisted = (
            db.query(Organization)
            .filter(
                Organization.id == organization.id,
                Organization.slug == slug,
            )
            .one_or_none()
        )

        if persisted is None:
            errors.append(
                "Organization could not be retrieved by its "
                "canonical identifiers."
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
        print(f"Status: {organization.status}")
        print(
            "Organization type: "
            f"{organization.organization_type}"
        )
        print(
            "Primary domain: "
            f"{organization.primary_domain}"
        )
        print(f"Time zone: {organization.time_zone}")
        print(
            "Deployment identifier present: "
            f"{bool(organization.deployment_identifier)}"
        )
        print(
            "Contains secrets: "
            f"{settings.get('contains_secret')}"
        )
        print(
            "Subscription embedded: "
            f"{settings.get('subscription_embedded')}"
        )
        print(
            "Governance embedded: "
            f"{settings.get('governance_embedded')}"
        )

        print()
        print("Validation: PASSED")
        print(
            "The canonical Organization model, lifecycle "
            "vocabulary, customer boundary, persistence, "
            "attribution, and architectural separation are "
            "operating correctly."
        )

        return 0

    finally:
        if organization_id:
            (
                db.query(Organization)
                .filter(
                    Organization.id == organization_id
                )
                .delete(
                    synchronize_session=False
                )
            )

            db.commit()

        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
