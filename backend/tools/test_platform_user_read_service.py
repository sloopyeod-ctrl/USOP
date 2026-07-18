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
from app.services.platform_user_service import (
    PlatformUserOrganizationNotFoundError,
    PlatformUserService,
)


ACTOR = "USOP Platform User Read Service Regression"


def build_organization(
    *,
    suffix: str,
    label: str,
) -> Organization:
    return Organization(
        name=f"Platform User Read {label}",
        slug=f"platform-user-read-{label.lower()}-{suffix}",
        status="Active",
        organization_type="Customer",
        time_zone="UTC",
        created_by=ACTOR,
        updated_by=ACTOR,
    )


def build_platform_user(
    *,
    organization_id: str,
    display_name: str,
    email: str,
    invited_at: datetime,
) -> PlatformUser:
    tenant_id = str(uuid.uuid4())

    return PlatformUser(
        organization_id=organization_id,
        display_name=display_name,
        email=email,
        status=PlatformUserStatus.INVITED.value,
        identity_provider="MicrosoftEntraID",
        external_tenant_id=tenant_id,
        external_subject_id=str(uuid.uuid4()),
        identity_issuer=(
            "https://login.microsoftonline.com/"
            f"{tenant_id}/v2.0"
        ),
        created_via_bootstrap=False,
        invited_at=invited_at,
        activated_at=None,
        last_authenticated_at=None,
        created_by=ACTOR,
        updated_by=ACTOR,
    )


def main() -> int:
    print("USOP Platform User Read Service Regression")
    print("------------------------------------------")

    db = SessionLocal()
    service = PlatformUserService(db)

    suffix = uuid.uuid4().hex
    now = datetime.now(timezone.utc)
    errors: list[str] = []

    primary_organization_id: str | None = None
    secondary_organization_id: str | None = None
    platform_user_ids: list[str] = []

    try:
        primary_organization = build_organization(
            suffix=suffix,
            label="Primary",
        )

        secondary_organization = build_organization(
            suffix=suffix,
            label="Secondary",
        )

        db.add(primary_organization)
        db.add(secondary_organization)
        db.flush()
        db.refresh(primary_organization)
        db.refresh(secondary_organization)

        primary_organization_id = primary_organization.id
        secondary_organization_id = secondary_organization.id

        first_user = build_platform_user(
            organization_id=primary_organization.id,
            display_name="First Platform Operator",
            email=f"first-{suffix}@example.invalid",
            invited_at=now,
        )

        second_user = build_platform_user(
            organization_id=primary_organization.id,
            display_name="Second Platform Operator",
            email=f"second-{suffix}@example.invalid",
            invited_at=now + timedelta(seconds=1),
        )

        secondary_user = build_platform_user(
            organization_id=secondary_organization.id,
            display_name="Secondary Organization Operator",
            email=f"secondary-{suffix}@example.invalid",
            invited_at=now + timedelta(seconds=2),
        )

        db.add(first_user)
        db.add(second_user)
        db.add(secondary_user)
        db.flush()

        db.refresh(first_user)
        db.refresh(second_user)
        db.refresh(secondary_user)

        platform_user_ids.extend(
            [
                first_user.id,
                second_user.id,
                secondary_user.id,
            ]
        )

        primary_users = service.list_for_organization(
            primary_organization.id
        )

        primary_user_ids = [
            platform_user.id
            for platform_user in primary_users
        ]

        expected_primary_users = sorted(
            [
                first_user,
                second_user,
            ],
            key=lambda platform_user: (
                platform_user.created_at,
                platform_user.id,
            ),
        )

        expected_primary_user_ids = [
            platform_user.id
            for platform_user in expected_primary_users
        ]

        organization_boundary_preserved = (
            set(primary_user_ids)
            == {
                first_user.id,
                second_user.id,
            }
            and secondary_user.id
            not in primary_user_ids
        )

        deterministic_order_preserved = (
            primary_user_ids
            == expected_primary_user_ids
        )

        if not organization_boundary_preserved:
            errors.append(
                "Organization-scoped listing crossed the "
                "Organization boundary or omitted a Platform User."
            )

        if not deterministic_order_preserved:
            errors.append(
                "Platform Users were not returned in repository-defined "
                "created_at and ID order."
            )

        resolved_user = service.get_by_id(
            organization_id=primary_organization.id,
            platform_user_id=first_user.id,
        )

        if resolved_user is None:
            errors.append(
                "Known Platform User was not returned."
            )
        elif resolved_user.id != first_user.id:
            errors.append(
                "Platform User lookup returned the wrong record."
            )

        missing_user = service.get_by_id(
            organization_id=primary_organization.id,
            platform_user_id=str(uuid.uuid4()),
        )

        if missing_user is not None:
            errors.append(
                "Unknown Platform User did not return None."
            )

        cross_organization_user = service.get_by_id(
            organization_id=primary_organization.id,
            platform_user_id=secondary_user.id,
        )

        if cross_organization_user is not None:
            errors.append(
                "Platform User lookup disclosed a record from "
                "another Organization."
            )

        unknown_list_rejected = False

        try:
            service.list_for_organization(
                str(uuid.uuid4())
            )
        except PlatformUserOrganizationNotFoundError:
            unknown_list_rejected = True

        if not unknown_list_rejected:
            errors.append(
                "Unknown Organization listing was accepted."
            )

        unknown_lookup_rejected = False

        try:
            service.get_by_id(
                organization_id=str(uuid.uuid4()),
                platform_user_id=first_user.id,
            )
        except PlatformUserOrganizationNotFoundError:
            unknown_lookup_rejected = True

        if not unknown_lookup_rejected:
            errors.append(
                "Unknown Organization lookup was accepted."
            )

        if first_user.status != PlatformUserStatus.INVITED.value:
            errors.append(
                "Read operation changed Platform User lifecycle state."
            )

        if first_user.activated_at is not None:
            errors.append(
                "Read operation marked authentication as complete."
            )

        # Read methods must not commit. Rolling back the caller-owned
        # transaction must remove all temporary records.
        db.rollback()

        persisted_user_count = (
            db.query(PlatformUser)
            .filter(
                PlatformUser.id.in_(platform_user_ids)
            )
            .count()
        )

        persisted_organization_count = (
            db.query(Organization)
            .filter(
                Organization.id.in_(
                    [
                        primary_organization_id,
                        secondary_organization_id,
                    ]
                )
            )
            .count()
        )

        if persisted_user_count != 0:
            errors.append(
                "Platform User read service committed user records."
            )

        if persisted_organization_count != 0:
            errors.append(
                "Platform User read service committed Organization records."
            )

        if errors:
            print()
            print("Validation: FAILED")

            for error in errors:
                print(f"- {error}")

            return 1

        print(
            "Primary Organization users returned: "
            f"{len(primary_users)}"
        )
        print(
            "Deterministic Organization listing: "
            f"{deterministic_order_preserved}"
        )
        print(
            "Known Platform User resolved: "
            f"{resolved_user is not None}"
        )
        print(
            "Unknown Platform User hidden: "
            f"{missing_user is None}"
        )
        print(
            "Cross-Organization Platform User hidden: "
            f"{cross_organization_user is None}"
        )
        print(
            "Unknown Organization listing rejected: "
            f"{unknown_list_rejected}"
        )
        print(
            "Unknown Organization lookup rejected: "
            f"{unknown_lookup_rejected}"
        )
        print(
            "Lifecycle state unchanged: "
            f"{first_user.status == PlatformUserStatus.INVITED.value}"
        )
        print(
            "Authentication state unchanged: "
            f"{first_user.activated_at is None}"
        )
        print(
            "Read service committed transaction: "
            f"{persisted_user_count != 0}"
        )

        print()
        print("Validation: PASSED")
        print(
            "PlatformUserService provides deterministic, "
            "Organization-scoped reads without disclosing "
            "cross-Organization records or changing lifecycle, "
            "authentication, authorization, Seat, or transaction state."
        )

        return 0

    finally:
        db.rollback()
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
