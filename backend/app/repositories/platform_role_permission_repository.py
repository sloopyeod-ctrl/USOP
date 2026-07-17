from sqlalchemy.orm import Session

from app.models.platform_role_permission import (
    PlatformRolePermission,
)


class PlatformRolePermissionRepository:
    """
    Persistence boundary for PlatformRolePermission mappings.

    The repository confirms only persisted values and query scope. It does not
    prove that the supplied Organization owns the referenced PlatformRole.
    Cross-record Organization consistency must be enforced by the Platform
    Authorization service before create() is called.
    """

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        mapping: PlatformRolePermission,
    ) -> PlatformRolePermission:
        self.db.add(mapping)
        self.db.flush()
        self.db.refresh(mapping)

        return mapping

    def get_by_id(
        self,
        mapping_id: str,
    ) -> PlatformRolePermission | None:
        return (
            self.db.query(PlatformRolePermission)
            .filter(
                PlatformRolePermission.id == mapping_id,
            )
            .one_or_none()
        )

    def get_mapping(
        self,
        *,
        organization_id: str,
        platform_role_id: str,
        platform_permission_id: str,
    ) -> PlatformRolePermission | None:
        return (
            self.db.query(PlatformRolePermission)
            .filter(
                PlatformRolePermission.organization_id
                == organization_id,
                PlatformRolePermission.platform_role_id
                == platform_role_id,
                PlatformRolePermission.platform_permission_id
                == platform_permission_id,
            )
            .one_or_none()
        )

    def list_for_role(
        self,
        *,
        organization_id: str,
        platform_role_id: str,
    ) -> list[PlatformRolePermission]:
        return (
            self.db.query(PlatformRolePermission)
            .filter(
                PlatformRolePermission.organization_id
                == organization_id,
                PlatformRolePermission.platform_role_id
                == platform_role_id,
            )
            .order_by(
                PlatformRolePermission.created_at.asc(),
                PlatformRolePermission.id.asc(),
            )
            .all()
        )

    def count_for_role(
        self,
        *,
        organization_id: str,
        platform_role_id: str,
    ) -> int:
        return (
            self.db.query(PlatformRolePermission)
            .filter(
                PlatformRolePermission.organization_id
                == organization_id,
                PlatformRolePermission.platform_role_id
                == platform_role_id,
            )
            .count()
        )
