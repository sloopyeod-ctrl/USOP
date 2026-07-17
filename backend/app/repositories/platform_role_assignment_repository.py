from sqlalchemy.orm import Session

from app.models.platform_role_assignment import (
    PlatformRoleAssignment,
)


class PlatformRoleAssignmentRepository:
    """
    Persistence boundary for PlatformRoleAssignment records.

    This repository does not determine whether the PlatformUser and
    PlatformRole belong to the supplied Organization. The Platform
    Authorization service must validate the complete tenant relationship
    before create() is called.
    """

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        assignment: PlatformRoleAssignment,
    ) -> PlatformRoleAssignment:
        self.db.add(assignment)
        self.db.flush()
        self.db.refresh(assignment)

        return assignment

    def get_by_id(
        self,
        assignment_id: str,
    ) -> PlatformRoleAssignment | None:
        return (
            self.db.query(PlatformRoleAssignment)
            .filter(
                PlatformRoleAssignment.id
                == assignment_id,
            )
            .one_or_none()
        )

    def get_assignment(
        self,
        *,
        organization_id: str,
        platform_user_id: str,
        platform_role_id: str,
    ) -> PlatformRoleAssignment | None:
        return (
            self.db.query(PlatformRoleAssignment)
            .filter(
                PlatformRoleAssignment.organization_id
                == organization_id,
                PlatformRoleAssignment.platform_user_id
                == platform_user_id,
                PlatformRoleAssignment.platform_role_id
                == platform_role_id,
            )
            .one_or_none()
        )

    def list_for_user(
        self,
        *,
        organization_id: str,
        platform_user_id: str,
    ) -> list[PlatformRoleAssignment]:
        return (
            self.db.query(PlatformRoleAssignment)
            .filter(
                PlatformRoleAssignment.organization_id
                == organization_id,
                PlatformRoleAssignment.platform_user_id
                == platform_user_id,
            )
            .order_by(
                PlatformRoleAssignment.assigned_at.asc(),
                PlatformRoleAssignment.id.asc(),
            )
            .all()
        )

    def list_for_role(
        self,
        *,
        organization_id: str,
        platform_role_id: str,
    ) -> list[PlatformRoleAssignment]:
        return (
            self.db.query(PlatformRoleAssignment)
            .filter(
                PlatformRoleAssignment.organization_id
                == organization_id,
                PlatformRoleAssignment.platform_role_id
                == platform_role_id,
            )
            .order_by(
                PlatformRoleAssignment.assigned_at.asc(),
                PlatformRoleAssignment.id.asc(),
            )
            .all()
        )

    def count_for_user(
        self,
        *,
        organization_id: str,
        platform_user_id: str,
    ) -> int:
        return (
            self.db.query(PlatformRoleAssignment)
            .filter(
                PlatformRoleAssignment.organization_id
                == organization_id,
                PlatformRoleAssignment.platform_user_id
                == platform_user_id,
            )
            .count()
        )
