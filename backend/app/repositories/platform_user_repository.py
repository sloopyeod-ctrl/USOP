from sqlalchemy.orm import Session

from app.models.platform_user import PlatformUser


class PlatformUserRepository:
    """
    Persistence boundary for USOP PlatformUser records.

    This repository stores and retrieves Platform Users but performs no
    authentication, authorization, commercial Seat evaluation, bootstrap
    policy enforcement, or transaction management.

    The calling service owns commit and rollback.
    """

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        platform_user: PlatformUser,
    ) -> PlatformUser:
        """
        Add a PlatformUser to the caller-owned transaction.
        """

        self.db.add(platform_user)
        self.db.flush()
        self.db.refresh(platform_user)

        return platform_user

    def get_by_id(
        self,
        platform_user_id: str,
    ) -> PlatformUser | None:
        return (
            self.db.query(PlatformUser)
            .filter(
                PlatformUser.id == platform_user_id,
            )
            .one_or_none()
        )

    def get_by_external_identity(
        self,
        *,
        organization_id: str,
        identity_provider: str,
        external_tenant_id: str,
        external_subject_id: str,
    ) -> PlatformUser | None:
        """
        Resolve one PlatformUser using the complete Organization-scoped
        external identity binding.
        """

        return (
            self.db.query(PlatformUser)
            .filter(
                PlatformUser.organization_id
                == organization_id,
                PlatformUser.identity_provider
                == identity_provider,
                PlatformUser.external_tenant_id
                == external_tenant_id,
                PlatformUser.external_subject_id
                == external_subject_id,
            )
            .one_or_none()
        )

    def get_by_external_identity_for_update(
        self,
        *,
        organization_id: str,
        identity_provider: str,
        external_tenant_id: str,
        external_subject_id: str,
    ) -> PlatformUser | None:
        """
        Lock and resolve one PlatformUser by its complete external identity.

        The repository owns persistence mechanics only. Authentication,
        invitation acceptance policy, issuer validation, auditing, and
        transaction ownership remain service-layer responsibilities.
        """

        return (
            self.db.query(PlatformUser)
            .filter(
                PlatformUser.organization_id
                == organization_id,
                PlatformUser.identity_provider
                == identity_provider,
                PlatformUser.external_tenant_id
                == external_tenant_id,
                PlatformUser.external_subject_id
                == external_subject_id,
            )
            .with_for_update()
            .one_or_none()
        )

    def record_first_authentication(
        self,
        *,
        platform_user: PlatformUser,
        activated_at,
        updated_by: str,
    ) -> PlatformUser:
        """
        Persist caller-authorized first-authentication lifecycle facts.

        Policy and trust validation must already have occurred in the
        calling service. This method does not authenticate, authorize,
        audit, commit, or roll back.
        """

        platform_user.status = "Active"
        platform_user.activated_at = activated_at
        platform_user.last_authenticated_at = activated_at
        platform_user.updated_by = updated_by

        self.db.flush()
        self.db.refresh(platform_user)

        return platform_user

    def list_for_organization(
        self,
        organization_id: str,
    ) -> list[PlatformUser]:
        return (
            self.db.query(PlatformUser)
            .filter(
                PlatformUser.organization_id
                == organization_id,
            )
            .order_by(
                PlatformUser.created_at.asc(),
                PlatformUser.id.asc(),
            )
            .all()
        )

    def list_for_organizational_identity(
        self,
        *,
        organization_id: str,
        organizational_identity_id: str,
    ) -> list[PlatformUser]:
        """
        Return Platform Users explicitly bound to one OrganizationalIdentity.

        Organization scope is mandatory so this relationship can never be
        queried as a tenant-neutral collection.
        """

        return (
            self.db.query(PlatformUser)
            .filter(
                PlatformUser.organization_id
                == organization_id,
                PlatformUser.organizational_identity_id
                == organizational_identity_id,
            )
            .order_by(
                PlatformUser.created_at.asc(),
                PlatformUser.id.asc(),
            )
            .all()
        )

    def set_organizational_identity_binding(
        self,
        *,
        platform_user: PlatformUser,
        organizational_identity_id: str | None,
    ) -> PlatformUser:
        """
        Persist the caller-authorized identity binding without committing.

        Binding policy and tenant validation belong to the service layer.
        """

        platform_user.organizational_identity_id = (
            organizational_identity_id
        )

        self.db.flush()
        self.db.refresh(platform_user)

        return platform_user

    def set_lifecycle_status(
        self,
        *,
        platform_user: PlatformUser,
        status: str,
        updated_by: str,
    ) -> PlatformUser:
        """
        Persist a caller-authorized PlatformUser access lifecycle change.

        Lifecycle policy, transition validation, tenant validation, trusted
        actor attribution, auditing, and transaction ownership belong to the
        service layer. This operation intentionally does not modify is_active.
        """

        platform_user.status = status
        platform_user.updated_by = updated_by

        self.db.flush()
        self.db.refresh(platform_user)

        return platform_user

    def count_for_organization(
        self,
        organization_id: str,
    ) -> int:
        return (
            self.db.query(PlatformUser)
            .filter(
                PlatformUser.organization_id
                == organization_id,
            )
            .count()
        )

    def bootstrap_exists(
        self,
        organization_id: str,
    ) -> bool:
        """
        Return whether any PlatformUser already exists for the Organization.

        This expresses bootstrap eligibility intent but does not itself enforce
        bootstrap policy or grant authorization.
        """

        return (
            self.count_for_organization(
                organization_id
            )
            > 0
        )
