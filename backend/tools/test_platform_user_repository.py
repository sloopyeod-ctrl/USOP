import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

from dotenv import load_dotenv


BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

load_dotenv(
    dotenv_path=BACKEND_ROOT / ".env",
    override=False,
)

from app.database.session import SessionLocal
from app.domain.platform_user_status import PlatformUserStatus
from app.models.organization import Organization
from app.models.platform_user import PlatformUser
from app.repositories.platform_user_repository import (
    PlatformUserRepository,
)


ACTOR = "USOP Platform User Repository Regression"


def build_platform_user(
    *,
    organization_id: str,
    display_name: str,
    email: str,
    tenant_id: str,
    subject_id: str,
    invited_at: datetime,
    created_via_bootstrap: bool,
) -> PlatformUser:
    return PlatformUser(
        organization_id=organization_id,
        display_name=display_name,
        email=email,
        status=PlatformUserStatus.INVITED.value,
        identity_provider="MicrosoftEntraID",
        external_tenant_id=tenant_id,
        external_subject_id=subject_id,
        identity_issuer=(
            "https://login.microsoftonline.com/"
            f"{tenant_id}/v2.0"
        ),
        created_via_bootstrap=created_via_bootstrap,
        invited_at=invited_at,
        activated_at=None,
        last_authenticated_at=None,
        created_by=ACTOR,
        updated_by=ACTOR,
    )


def main() -> int:
    print("USOP Platform User Repository Regression")
    print("----------------------------------------")

    db = SessionLocal()
    repository = PlatformUserRepository(db)

    suffix = uuid.uuid4().hex
    now = datetime.now(timezone.utc)

    organization_id: str | None = None
    secondary_organization_id: str | None = None

    errors: list[str] = []

    try:
        organization = Organization(
            name="Platform User Repository Regression",
            slug=f"platform-user-repository-{suffix}",
            status="Active",
            organization_type="Customer",
            time_zone="UTC",
            created_by=ACTOR,
            updated_by=ACTOR,
        )

        secondary_organization = Organization(
            name="Platform User Repository Secondary",
            slug=f"platform-user-repository-secondary-{suffix}",
            status="Active",
            organization_type="Customer",
            time_zone="UTC",
            created_by=ACTOR,
            updated_by=ACTOR,
        )

        db.add(organization)
        db.add(secondary_organization)
        db.flush()
        db.refresh(organization)
        db.refresh(secondary_organization)

        organization_id = organization.id
        secondary_organization_id = secondary_organization.id

        tenant_id = str(uuid.uuid4())

        first_user = repository.create(
            build_platform_user(
                organization_id=organization.id,
                display_name="Initial Platform Administrator",
                email=f"initial-{suffix}@example.invalid",
                tenant_id=tenant_id,
                subject_id=str(uuid.uuid4()),
                invited_at=now,
                created_via_bootstrap=True,
            )
        )

        second_user = repository.create(
            build_platform_user(
                organization_id=organization.id,
                display_name="Second Platform Operator",
                email=f"second-{suffix}@example.invalid",
                tenant_id=tenant_id,
                subject_id=str(uuid.uuid4()),
                invited_at=now + timedelta(seconds=1),
                created_via_bootstrap=False,
            )
        )

        secondary_user = repository.create(
            build_platform_user(
                organization_id=secondary_organization.id,
                display_name="Secondary Organization Operator",
                email=f"secondary-{suffix}@example.invalid",
                tenant_id=tenant_id,
                subject_id=str(uuid.uuid4()),
                invited_at=now + timedelta(seconds=2),
                created_via_bootstrap=False,
            )
        )

        by_id = repository.get_by_id(
            first_user.id
        )

        if by_id is None:
            errors.append(
                "PlatformUser lookup by ID returned no record."
            )
        elif by_id.id != first_user.id:
            errors.append(
                "PlatformUser lookup by ID returned the wrong record."
            )

        by_external_identity = (
            repository.get_by_external_identity(
                organization_id=organization.id,
                identity_provider=(
                    first_user.identity_provider
                ),
                external_tenant_id=(
                    first_user.external_tenant_id
                ),
                external_subject_id=(
                    first_user.external_subject_id
                ),
            )
        )

        if by_external_identity is None:
            errors.append(
                "External identity lookup returned no PlatformUser."
            )
        elif by_external_identity.id != first_user.id:
            errors.append(
                "External identity lookup returned the wrong PlatformUser."
            )

        wrong_organization_lookup = (
            repository.get_by_external_identity(
                organization_id=secondary_organization.id,
                identity_provider=(
                    first_user.identity_provider
                ),
                external_tenant_id=(
                    first_user.external_tenant_id
                ),
                external_subject_id=(
                    first_user.external_subject_id
                ),
            )
        )

        if wrong_organization_lookup is not None:
            errors.append(
                "External identity lookup crossed the Organization boundary."
            )

        organization_users = (
            repository.list_for_organization(
                organization.id
            )
        )

        organization_user_ids = [
            item.id
            for item in organization_users
        ]

        expected_organization_user_ids = [
            first_user.id,
            second_user.id,
        ]

        if (
            organization_user_ids
            != expected_organization_user_ids
        ):
            errors.append(
                "Platform Users were not listed in deterministic "
                "creation order."
            )

        organization_count = (
            repository.count_for_organization(
                organization.id
            )
        )

        secondary_count = (
            repository.count_for_organization(
                secondary_organization.id
            )
        )

        if organization_count != 2:
            errors.append(
                "Primary Organization PlatformUser count was incorrect."
            )

        if secondary_count != 1:
            errors.append(
                "Secondary Organization PlatformUser count was incorrect."
            )

        bootstrap_exists = (
            repository.bootstrap_exists(
                organization.id
            )
        )

        if not bootstrap_exists:
            errors.append(
                "bootstrap_exists() returned False for an Organization "
                "with Platform Users."
            )

        empty_organization = Organization(
            name="Platform User Repository Empty",
            slug=f"platform-user-repository-empty-{suffix}",
            status="Active",
            organization_type="Customer",
            time_zone="UTC",
            created_by=ACTOR,
            updated_by=ACTOR,
        )

        db.add(empty_organization)
        db.flush()
        db.refresh(empty_organization)

        empty_bootstrap_exists = (
            repository.bootstrap_exists(
                empty_organization.id
            )
        )

        if empty_bootstrap_exists:
            errors.append(
                "bootstrap_exists() returned True for an empty Organization."
            )

        prohibited_methods = {
            "delete",
            "authenticate",
            "assign_role",
            "assign_seat",
            "commit",
            "rollback",
        }

        exposed_prohibited_methods = sorted(
            method_name
            for method_name in prohibited_methods
            if hasattr(
                repository,
                method_name,
            )
        )

        if exposed_prohibited_methods:
            errors.append(
                "PlatformUserRepository exposes prohibited methods: "
                + ", ".join(exposed_prohibited_methods)
            )

        # Repository methods must not commit. Rolling back the caller-owned
        # transaction must remove every temporary Organization and PlatformUser.
        db.rollback()

        persisted_primary_organization = (
            db.query(Organization)
            .filter(
                Organization.id == organization.id,
            )
            .one_or_none()
        )

        persisted_secondary_organization = (
            db.query(Organization)
            .filter(
                Organization.id
                == secondary_organization.id,
            )
            .one_or_none()
        )

        persisted_platform_user_count = (
            db.query(PlatformUser)
            .filter(
                PlatformUser.id.in_(
                    [
                        first_user.id,
                        second_user.id,
                        secondary_user.id,
                    ]
                )
            )
            .count()
        )

        if persisted_primary_organization is not None:
            errors.append(
                "Repository unexpectedly committed the primary Organization."
            )

        if persisted_secondary_organization is not None:
            errors.append(
                "Repository unexpectedly committed the secondary Organization."
            )

        if persisted_platform_user_count != 0:
            errors.append(
                "Repository unexpectedly committed PlatformUser records."
            )

        if errors:
            print()
            print("Validation: FAILED")

            for error in errors:
                print(f"- {error}")

            return 1

        print(f"Primary Organization ID: {organization.id}")
        print(
            "Platform Users created: "
            f"{len(organization_users) + secondary_count}"
        )
        print(
            "Lookup by ID: "
            f"{by_id is not None}"
        )
        print(
            "Lookup by external identity: "
            f"{by_external_identity is not None}"
        )
        print(
            "Organization boundary preserved: "
            f"{wrong_organization_lookup is None}"
        )
        print(
            "Organization listing deterministic: "
            f"{organization_user_ids == expected_organization_user_ids}"
        )
        print(
            "Primary Organization count: "
            f"{organization_count}"
        )
        print(
            "Secondary Organization count: "
            f"{secondary_count}"
        )
        print(
            "Bootstrap exists for populated Organization: "
            f"{bootstrap_exists}"
        )
        print(
            "Bootstrap exists for empty Organization: "
            f"{empty_bootstrap_exists}"
        )
        print(
            "Prohibited repository methods exposed: "
            f"{bool(exposed_prohibited_methods)}"
        )
        print(
            "Repository committed transaction: "
            f"{persisted_platform_user_count != 0}"
        )

        print()
        print("Validation: PASSED")
        print(
            "PlatformUserRepository provides deterministic, "
            "Organization-scoped persistence and retrieval while preserving "
            "service-layer transaction ownership and separation from "
            "authentication, authorization, and commercial Seat logic."
        )

        return 0

    finally:
        db.rollback()

        if organization_id or secondary_organization_id:
            organization_ids = [
                item
                for item in (
                    organization_id,
                    secondary_organization_id,
                )
                if item is not None
            ]

            if organization_ids:
                (
                    db.query(PlatformUser)
                    .filter(
                        PlatformUser.organization_id.in_(
                            organization_ids
                        )
                    )
                    .delete(
                        synchronize_session=False
                    )
                )

                (
                    db.query(Organization)
                    .filter(
                        Organization.id.in_(
                            organization_ids
                        )
                    )
                    .delete(
                        synchronize_session=False
                    )
                )

                db.commit()

        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
