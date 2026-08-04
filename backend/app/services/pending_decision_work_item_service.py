from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.pending_decision_work_item import (
    PendingDecisionWorkItem,
)
from app.repositories.organization_repository import (
    OrganizationRepository,
)
from app.repositories.pending_decision_work_item_repository import (
    PendingDecisionWorkItemRepository,
)
from app.services.audit_service import AuditService


class PendingDecisionWorkItemError(Exception):
    """Base error for PendingDecisionWorkItem operations."""


class PendingDecisionWorkItemValidationError(
    PendingDecisionWorkItemError
):
    pass


class PendingDecisionWorkItemOrganizationNotFoundError(
    PendingDecisionWorkItemError
):
    pass


class PendingDecisionWorkItemDuplicateError(
    PendingDecisionWorkItemError
):
    pass


class PendingDecisionWorkItemService:
    """
    Backend authority for Organization-scoped human decision work.

    create_pending() validates, deduplicates, stages persistence, and stages
    audit evidence in the caller-owned transaction.
    """

    ALLOWED_STATUSES = {
        "Pending",
        "Assigned",
        "In Review",
        "Resolved",
        "Dismissed",
    }

    def __init__(
        self,
        db: Session,
        *,
        repository: (
            PendingDecisionWorkItemRepository | None
        ) = None,
        organization_repository: (
            OrganizationRepository | None
        ) = None,
        audit_service: AuditService | None = None,
    ):
        self.db = db
        self.repository = (
            repository
            or PendingDecisionWorkItemRepository(db)
        )
        self.organization_repository = (
            organization_repository
            or OrganizationRepository(db)
        )
        self.audit_service = (
            audit_service or AuditService(db)
        )

    def _require_organization(
        self,
        organization_id: str,
    ):
        organization = self.organization_repository.get_by_id(
            organization_id
        )

        if organization is None:
            raise (
                PendingDecisionWorkItemOrganizationNotFoundError(
                    "The PendingDecisionWorkItem operation "
                    "references an unknown Organization."
                )
            )

        return organization

    @staticmethod
    def _required_text(
        value: str,
        *,
        field_name: str,
    ) -> str:
        if not isinstance(value, str):
            raise PendingDecisionWorkItemValidationError(
                f"{field_name} must be a string."
            )

        normalized = value.strip()

        if not normalized:
            raise PendingDecisionWorkItemValidationError(
                f"{field_name} cannot be blank."
            )

        return normalized

    @staticmethod
    def _optional_text(
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        if not isinstance(value, str):
            raise PendingDecisionWorkItemValidationError(
                "Optional PendingDecisionWorkItem text "
                "must be a string."
            )

        return value.strip() or None

    def create_pending(
        self,
        *,
        organization_id: str,
        source_type: str,
        source_id: str,
        decision_category: str,
        title: str,
        priority: str,
        risk_level: str,
        evidence_snapshot_json: dict,
        identity_id: str | None = None,
        summary: str | None = None,
        materiality_reason: str | None = None,
        assigned_to: str | None = None,
        due_at=None,
        source_system: str | None = "USOP",
        source_identifier: str | None = None,
        confidence_score: int = 100,
        actor: str | None = None,
    ) -> PendingDecisionWorkItem:
        normalized_organization_id = self._required_text(
            organization_id,
            field_name="organization_id",
        )
        organization = self._require_organization(
            normalized_organization_id
        )

        normalized_source_type = self._required_text(
            source_type,
            field_name="source_type",
        )
        normalized_source_id = self._required_text(
            source_id,
            field_name="source_id",
        )
        normalized_category = self._required_text(
            decision_category,
            field_name="decision_category",
        )
        normalized_title = self._required_text(
            title,
            field_name="title",
        )
        normalized_priority = self._required_text(
            priority,
            field_name="priority",
        )
        normalized_risk = self._required_text(
            risk_level,
            field_name="risk_level",
        )

        if not isinstance(evidence_snapshot_json, dict):
            raise PendingDecisionWorkItemValidationError(
                "evidence_snapshot_json must be an object."
            )

        if (
            not isinstance(confidence_score, int)
            or isinstance(confidence_score, bool)
            or confidence_score < 0
            or confidence_score > 100
        ):
            raise PendingDecisionWorkItemValidationError(
                "confidence_score must be an integer "
                "from 0 through 100."
            )

        existing = (
            self.repository
            .get_by_source_for_organization(
                organization_id=organization.id,
                source_type=normalized_source_type,
                source_id=normalized_source_id,
            )
        )

        if existing is not None:
            return existing

        work_item = PendingDecisionWorkItem(
            organization_id=organization.id,
            identity_id=self._optional_text(identity_id),
            source_type=normalized_source_type,
            source_id=normalized_source_id,
            decision_category=normalized_category,
            title=normalized_title,
            summary=self._optional_text(summary),
            priority=normalized_priority,
            status="Pending",
            risk_level=normalized_risk,
            materiality_reason=self._optional_text(
                materiality_reason
            ),
            evidence_snapshot_json=dict(
                evidence_snapshot_json
            ),
            assigned_to=self._optional_text(assigned_to),
            due_at=due_at,
            source_system=self._optional_text(source_system),
            source_identifier=(
                self._optional_text(source_identifier)
                or normalized_source_id
            ),
            confidence_score=confidence_score,
            created_by=actor,
            updated_by=actor,
        )

        try:
            work_item = self.repository.create_pending(
                work_item
            )

            self.audit_service.record_pending(
                event_type="PendingDecisionWorkItemCreated",
                entity_type="PendingDecisionWorkItem",
                entity_id=work_item.id,
                actor=actor,
                message=(
                    f"Pending decision work item "
                    f"'{work_item.title}' was created."
                ),
                metadata={
                    "organization_id": organization.id,
                    "work_item_id": work_item.id,
                    "source_type": work_item.source_type,
                    "source_id": work_item.source_id,
                    "decision_category": (
                        work_item.decision_category
                    ),
                    "priority": work_item.priority,
                    "risk_level": work_item.risk_level,
                    "status": work_item.status,
                    "transaction_mode": "CallerOwned",
                    "actor_trust": (
                        "CallerSupplied"
                        if actor
                        else "Unattributed"
                    ),
                },
            )

            return work_item

        except IntegrityError as error:
            raise PendingDecisionWorkItemDuplicateError(
                "A PendingDecisionWorkItem already exists "
                "for this Organization and source."
            ) from error

    def create(self, **kwargs) -> PendingDecisionWorkItem:
        try:
            work_item = self.create_pending(**kwargs)
            self.db.commit()
            self.db.refresh(work_item)
            return work_item
        except Exception:
            self.db.rollback()
            raise

    def get_by_id(
        self,
        *,
        organization_id: str,
        work_item_id: str,
    ) -> PendingDecisionWorkItem | None:
        organization = self._require_organization(
            self._required_text(
                organization_id,
                field_name="organization_id",
            )
        )
        return self.repository.get_by_id_for_organization(
            organization_id=organization.id,
            work_item_id=work_item_id,
        )

    def list_for_organization(
        self,
        *,
        organization_id: str,
        status: str | None = None,
    ) -> list[PendingDecisionWorkItem]:
        organization = self._require_organization(
            self._required_text(
                organization_id,
                field_name="organization_id",
            )
        )

        normalized_status = self._optional_text(status)

        if (
            normalized_status is not None
            and normalized_status
            not in self.ALLOWED_STATUSES
        ):
            raise PendingDecisionWorkItemValidationError(
                f"Unknown work-item status: "
                f"{normalized_status}"
            )

        return self.repository.list_for_organization(
            organization_id=organization.id,
            status=normalized_status,
        )
