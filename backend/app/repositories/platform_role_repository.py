from sqlalchemy.orm import Session

from app.models.platform_role import PlatformRole


class PlatformRoleRepository:
    """
    Persistence boundary for Organization-scoped PlatformRole records.

    This repository performs no authorization, tenant-consistency validation,
    default-role seeding, auditing, or transaction management. The calling
    service owns all security decisions, commit, and rollback.
    """

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        platform_role: PlatformRole,
    ) -> PlatformRole:
        self.db.add(platform_role)
        self.db.flush()
        self.db.refresh(platform_role)

        return platform_role

    def get_by_id(
        self,
        platform_role_id: str,
    ) -> PlatformRole | None:
        return (
            self.db.query(PlatformRole)
            .filter(
                PlatformRole.id == platform_role_id,
            )
            .one_or_none()
        )

    def get_by_key(
        self,
        *,
        organization_id: str,
        role_key: str,
    ) -> PlatformRole | None:
        return (
            self.db.query(PlatformRole)
            .filter(
                PlatformRole.organization_id
                == organization_id,
                PlatformRole.role_key == role_key,
            )
            .one_or_none()
        )

    def list_for_organization(
        self,
        organization_id: str,
    ) -> list[PlatformRole]:
        return (
            self.db.query(PlatformRole)
            .filter(
                PlatformRole.organization_id
                == organization_id,
            )
            .order_by(
                PlatformRole.created_at.asc(),
                PlatformRole.id.asc(),
            )
            .all()
        )

    def count_for_organization(
        self,
        organization_id: str,
    ) -> int:
        return (
            self.db.query(PlatformRole)
            .filter(
                PlatformRole.organization_id
                == organization_id,
            )
            .count()
        )
