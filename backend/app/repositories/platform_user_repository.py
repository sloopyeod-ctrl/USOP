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
