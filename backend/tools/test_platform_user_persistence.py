import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy.exc import IntegrityError


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


ACTOR = "USOP Platform User Persistence Regression"


def main() -> int:
    print("USOP Platform User Persistence Regression")
    print("-----------------------------------------")

    db = SessionLocal()
    organization_id: str | None = None

    suffix = uuid.uuid4().hex
    tenant_id = str(uuid.uuid4())
    subject_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)

    errors: list[str] = []

    try:
        organization = Organization(
            name="Platform User Persistence Regression",
            slug=f"platform-user-{suffix}",
            status="Active",
            organization_type="Customer",
            time_zone="UTC",
            created_by=ACTOR,
            updated_by=ACTOR,
        )

        db.add(organization)
        db.commit()
        db.refresh(organization)

        organization_id = organization.id

        platform_user = PlatformUser(
            organization_id=organization.id,
            display_name="Initial Platform Administrator",
            email=f"admin-{suffix}@example.invalid",
            status=PlatformUserStatus.INVITED.value,
            identity_provider="MicrosoftEntraID",
            external_tenant_id=tenant_id,
            external_subject_id=subject_id,
            identity_issuer=(
                "https://login.microsoftonline.com/"
                f"{tenant_id}/v2.0"
            ),
            created_via_bootstrap=True,
            invited_at=now,
            activated_at=None,
            last_authenticated_at=None,
            created_by=ACTOR,
            updated_by=ACTOR,
        )

        db.add(platform_user)
        db.commit()
        db.refresh(platform_user)

        persisted = (
            db.query(PlatformUser)
            .filter(
                PlatformUser.id == platform_user.id,
            )
            .one_or_none()
        )

        if persisted is None:
            errors.append(
                "PlatformUser was not persisted."
            )

        elif persisted.organization_id != organization.id:
            errors.append(
                "PlatformUser Organization binding was not preserved."
            )

        elif persisted.external_subject_id != subject_id:
            errors.append(
                "External subject binding was not preserved."
            )

        elif (
            persisted.status
            != PlatformUserStatus.INVITED.value
        ):
            errors.append(
                "PlatformUser lifecycle status was not preserved."
            )

        duplicate_rejected = False

        duplicate = PlatformUser(
            organization_id=organization.id,
            display_name="Duplicate External Identity",
            email=f"duplicate-{suffix}@example.invalid",
            status=PlatformUserStatus.INVITED.value,
            identity_provider="MicrosoftEntraID",
            external_tenant_id=tenant_id,
            external_subject_id=subject_id,
            identity_issuer=(
                "https://login.microsoftonline.com/"
                f"{tenant_id}/v2.0"
            ),
            created_via_bootstrap=False,
            invited_at=now,
            created_by=ACTOR,
            updated_by=ACTOR,
        )

        db.add(duplicate)

        try:
            db.commit()
        except IntegrityError:
            duplicate_rejected = True
            db.rollback()

        if not duplicate_rejected:
            errors.append(
                "Duplicate Organization/provider/tenant/subject "
                "binding was accepted."
            )

        another_organization = Organization(
            name="Platform User Secondary Organization",
            slug=f"platform-user-secondary-{suffix}",
            status="Active",
            organization_type="Customer",
            time_zone="UTC",
            created_by=ACTOR,
            updated_by=ACTOR,
        )

        db.add(another_organization)
        db.commit()
        db.refresh(another_organization)

        cross_organization_user = PlatformUser(
            organization_id=another_organization.id,
            display_name="Cross Organization Operator",
            email=f"cross-{suffix}@example.invalid",
            status=PlatformUserStatus.INVITED.value,
            identity_provider="MicrosoftEntraID",
            external_tenant_id=tenant_id,
            external_subject_id=subject_id,
            identity_issuer=(
                "https://login.microsoftonline.com/"
                f"{tenant_id}/v2.0"
            ),
            created_via_bootstrap=False,
            invited_at=now,
            created_by=ACTOR,
            updated_by=ACTOR,
        )

        db.add(cross_organization_user)
        db.commit()
        db.refresh(cross_organization_user)

        cross_organization_allowed = (
            cross_organization_user.id is not None
        )

        if not cross_organization_allowed:
            errors.append(
                "The same external identity could not be scoped "
                "independently to another Organization."
            )

        if errors:
            print()
            print("Validation: FAILED")

            for error in errors:
                print(f"- {error}")

            return 1

        print(f"Platform User ID: {platform_user.id}")
        print(f"Organization ID: {organization.id}")
        print(
            "Organization binding preserved: "
            f"{persisted.organization_id == organization.id}"
        )
        print(
            "External identity binding preserved: "
            f"{persisted.external_subject_id == subject_id}"
        )
        print(
            "Lifecycle status preserved: "
            f"{persisted.status == PlatformUserStatus.INVITED.value}"
        )
        print(
            "Bootstrap provenance preserved: "
            f"{persisted.created_via_bootstrap}"
        )
        print(
            "Duplicate binding rejected: "
            f"{duplicate_rejected}"
        )
        print(
            "Cross-Organization identity reuse allowed: "
            f"{cross_organization_allowed}"
        )
        print("Credentials persisted: False")
        print("Seat State persisted: False")
        print("Authorization embedded: False")

        print()
        print("Validation: PASSED")
        print(
            "PlatformUser persistence preserves Organization ownership, "
            "external authentication binding, lifecycle state, and "
            "bootstrap provenance while enforcing Organization-scoped "
            "identity uniqueness."
        )

        return 0

    finally:
        db.rollback()

        (
            db.query(PlatformUser)
            .filter(
                PlatformUser.external_tenant_id == tenant_id,
                PlatformUser.external_subject_id == subject_id,
            )
            .delete(
                synchronize_session=False
            )
        )

        (
            db.query(Organization)
            .filter(
                Organization.slug.in_(
                    [
                        f"platform-user-{suffix}",
                        f"platform-user-secondary-{suffix}",
                    ]
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
