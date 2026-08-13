from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.domain.platform_role_status import PlatformRoleStatus
from app.domain.platform_user_status import PlatformUserStatus
from app.repositories.platform_permission_repository import PlatformPermissionRepository
from app.repositories.platform_role_assignment_repository import PlatformRoleAssignmentRepository
from app.repositories.platform_role_permission_repository import PlatformRolePermissionRepository
from app.repositories.platform_role_repository import PlatformRoleRepository
from app.repositories.platform_user_repository import PlatformUserRepository
from app.services.platform_runtime_authorization_result import (
    PlatformRuntimeAuthorizationDisposition,
    PlatformRuntimeAuthorizationResult,
)


class PlatformRuntimeAuthorizationService:
    """Fail-closed runtime permission evaluator for operating USOP itself."""

    def __init__(
        self,
        db: Session,
        *,
        platform_user_repository=None,
        platform_role_assignment_repository=None,
        platform_role_repository=None,
        platform_role_permission_repository=None,
        platform_permission_repository=None,
    ):
        self.db = db
        self.platform_user_repository = platform_user_repository or PlatformUserRepository(db)
        self.assignment_repository = platform_role_assignment_repository or PlatformRoleAssignmentRepository(db)
        self.role_repository = platform_role_repository or PlatformRoleRepository(db)
        self.mapping_repository = platform_role_permission_repository or PlatformRolePermissionRepository(db)
        self.permission_repository = platform_permission_repository or PlatformPermissionRepository(db)

    @staticmethod
    def _required(value: str, field_name: str) -> str:
        normalized = str(value or "").strip()
        if not normalized:
            raise ValueError(f"{field_name} is required.")
        return normalized

    @staticmethod
    def _as_utc(value: datetime) -> datetime:
        return value.replace(tzinfo=UTC) if value.tzinfo is None else value.astimezone(UTC)

    @classmethod
    def _assignment_is_effective(cls, assignment, now: datetime) -> bool:
        if not getattr(assignment, "is_active", True):
            return False
        assigned_at = getattr(assignment, "assigned_at", None)
        if assigned_at is None or cls._as_utc(assigned_at) > now:
            return False
        expires_at = getattr(assignment, "expires_at", None)
        if expires_at is not None and cls._as_utc(expires_at) <= now:
            return False
        return True

    def _deny(self, organization_id, platform_user_id, permission_key, reason, evidence=()):
        return PlatformRuntimeAuthorizationResult(
            disposition=PlatformRuntimeAuthorizationDisposition.DENY,
            organization_id=organization_id,
            platform_user_id=platform_user_id,
            permission_key=permission_key,
            reason=reason,
            evidence=evidence,
        )

    def evaluate(
        self,
        *,
        organization_id: str,
        platform_user_id: str,
        permission_key: str,
        now: datetime | None = None,
    ) -> PlatformRuntimeAuthorizationResult:
        organization_id = self._required(organization_id, "organization_id")
        platform_user_id = self._required(platform_user_id, "platform_user_id")
        permission_key = self._required(permission_key, "permission_key")
        effective_now = self._as_utc(now or datetime.now(UTC))

        user = self.platform_user_repository.get_by_id(platform_user_id)
        if user is None or user.organization_id != organization_id:
            return self._deny(organization_id, platform_user_id, permission_key, "PlatformUserNotFoundInOrganization")
        if not getattr(user, "is_active", True):
            return self._deny(organization_id, platform_user_id, permission_key, "PlatformUserInactive")
        if user.status != PlatformUserStatus.ACTIVE.value:
            return self._deny(
                organization_id, platform_user_id, permission_key,
                "PlatformUserNotActive", (f"user_status={user.status}",)
            )

        permission = self.permission_repository.get_by_key(permission_key)
        if permission is None:
            return self._deny(organization_id, platform_user_id, permission_key, "PermissionNotDefined")
        if not getattr(permission, "is_active", True):
            return self._deny(organization_id, platform_user_id, permission_key, "PermissionInactive")

        assignments = self.assignment_repository.list_for_user(
            organization_id=organization_id,
            platform_user_id=platform_user_id,
        )

        for assignment in assignments:
            if not self._assignment_is_effective(assignment, effective_now):
                continue

            role = self.role_repository.get_by_id(assignment.platform_role_id)
            if role is None or role.organization_id != organization_id:
                continue
            if not getattr(role, "is_active", True):
                continue
            if role.status != PlatformRoleStatus.ACTIVE.value:
                continue

            mappings = self.mapping_repository.list_for_role(
                organization_id=organization_id,
                platform_role_id=role.id,
            )
            for mapping in mappings:
                if not getattr(mapping, "is_active", True):
                    continue
                if mapping.platform_permission_id != permission.id:
                    continue

                return PlatformRuntimeAuthorizationResult(
                    disposition=PlatformRuntimeAuthorizationDisposition.ALLOW,
                    organization_id=organization_id,
                    platform_user_id=platform_user_id,
                    permission_key=permission_key,
                    reason="PermissionGrantedByActiveRole",
                    platform_role_id=role.id,
                    platform_role_key=role.role_key,
                    platform_permission_id=permission.id,
                    platform_role_assignment_id=assignment.id,
                    evidence=(
                        f"organization_id={organization_id}",
                        f"platform_user_id={platform_user_id}",
                        f"platform_role_id={role.id}",
                        f"permission_key={permission.permission_key}",
                        f"assignment_id={assignment.id}",
                    ),
                )

        return self._deny(
            organization_id,
            platform_user_id,
            permission_key,
            "NoEffectiveRoleGrantsPermission",
        )

    def has_permission(self, **kwargs) -> bool:
        return self.evaluate(**kwargs).allowed
