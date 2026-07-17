from sqlalchemy.orm import Session

from app.models.platform_permission import PlatformPermission


class PlatformPermissionRepository:
    """
    Persistence boundary for the global PlatformPermission vocabulary.

    Permissions are global definitions of platform actions. This repository
    does not determine whether a user, role, or Organization is authorized to
    exercise a permission. The calling service owns security policy and the
    transaction.
    """

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        platform_permission: PlatformPermission,
    ) -> PlatformPermission:
        self.db.add(platform_permission)
        self.db.flush()
        self.db.refresh(platform_permission)

        return platform_permission

    def get_by_id(
        self,
        platform_permission_id: str,
    ) -> PlatformPermission | None:
        return (
            self.db.query(PlatformPermission)
            .filter(
                PlatformPermission.id
                == platform_permission_id,
            )
            .one_or_none()
        )

    def get_by_key(
        self,
        permission_key: str,
    ) -> PlatformPermission | None:
        return (
            self.db.query(PlatformPermission)
            .filter(
                PlatformPermission.permission_key
                == permission_key,
            )
            .one_or_none()
        )

    def get_by_resource_action(
        self,
        *,
        resource: str,
        action: str,
    ) -> PlatformPermission | None:
        return (
            self.db.query(PlatformPermission)
            .filter(
                PlatformPermission.resource == resource,
                PlatformPermission.action == action,
            )
            .one_or_none()
        )

    def list_all(
        self,
    ) -> list[PlatformPermission]:
        return (
            self.db.query(PlatformPermission)
            .order_by(
                PlatformPermission.permission_key.asc(),
                PlatformPermission.id.asc(),
            )
            .all()
        )
