from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.domain import (
    KnowledgeAssetStatus,
    KnowledgeCategory,
)
from app.models.knowledge_asset import KnowledgeAsset
from app.repositories.knowledge_asset_repository import (
    KnowledgeAssetRepository,
)
from app.repositories.organization_repository import (
    OrganizationRepository,
)
from app.services.audit_service import AuditService


class KnowledgeAssetServiceError(ValueError):
    """
    Base exception for KnowledgeAsset service failures.
    """


class KnowledgeAssetOrganizationNotFoundError(
    KnowledgeAssetServiceError
):
    """
    Raised when an operation references an unknown Organization.
    """


class KnowledgeAssetValidationError(
    KnowledgeAssetServiceError
):
    """
    Raised when KnowledgeAsset input violates a domain rule.
    """


class KnowledgeAssetDuplicateVersionError(
    KnowledgeAssetServiceError
):
    """
    Raised when a KnowledgeAsset version conflicts with existing
    Organizational Memory.
    """


class KnowledgeAssetService:
    """
    Backend authority for Organization-scoped Organizational Memory.

    Read operations validate the Organization boundary before retrieval.

    create_pending() validates and stages one KnowledgeAsset inside the
    caller-owned transaction. It does not commit, roll back, write audit
    events, authorize a caller, or manage relationships.
    """

    def __init__(self, db: Session):
        self.db = db
        self.organization_repository = OrganizationRepository(db)
        self.repository = KnowledgeAssetRepository(db)
        self.audit_service = AuditService(db)

    def _require_organization(
        self,
        organization_id: str,
    ):
        """
        Return one known Organization or raise the canonical service error.
        """

        organization = (
            self.organization_repository.get_by_id(
                organization_id
            )
        )

        if organization is None:
            raise KnowledgeAssetOrganizationNotFoundError(
                "The KnowledgeAsset operation references "
                "an unknown Organization."
            )

        return organization

    @staticmethod
    def _normalize_required_text(
        *,
        field_name: str,
        value: str,
    ) -> str:
        if not isinstance(value, str):
            raise KnowledgeAssetValidationError(
                f"{field_name} must be a string."
            )

        normalized = value.strip()

        if not normalized:
            raise KnowledgeAssetValidationError(
                f"{field_name} cannot be blank."
            )

        return normalized

    @staticmethod
    def _normalize_optional_text(
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        if not isinstance(value, str):
            raise KnowledgeAssetValidationError(
                "Optional KnowledgeAsset text must be a string."
            )

        normalized = value.strip()

        return normalized or None

    @staticmethod
    def _normalize_category(
        category: KnowledgeCategory | str,
    ) -> str:
        if isinstance(category, KnowledgeCategory):
            return category.value

        if not isinstance(category, str):
            raise KnowledgeAssetValidationError(
                "KnowledgeAsset category is invalid."
            )

        normalized = category.strip()

        try:
            return KnowledgeCategory(normalized).value
        except ValueError as error:
            raise KnowledgeAssetValidationError(
                f"Unknown KnowledgeAsset category: {normalized}"
            ) from error

    @staticmethod
    def _normalize_status(
        status: KnowledgeAssetStatus | str,
    ) -> str:
        if isinstance(status, KnowledgeAssetStatus):
            return status.value

        if not isinstance(status, str):
            raise KnowledgeAssetValidationError(
                "KnowledgeAsset status is invalid."
            )

        normalized = status.strip()

        try:
            return KnowledgeAssetStatus(normalized).value
        except ValueError as error:
            raise KnowledgeAssetValidationError(
                f"Unknown KnowledgeAsset status: {normalized}"
            ) from error

    def create_pending(
        self,
        *,
        organization_id: str,
        title: str,
        guidance: str,
        category: KnowledgeCategory | str,
        status: KnowledgeAssetStatus | str = (
            KnowledgeAssetStatus.DRAFT
        ),
        summary: str | None = None,
        source_system: str | None = None,
        source_identifier: str | None = None,
        confidence_score: int = 100,
        actor: str | None = None,
    ) -> KnowledgeAsset:
        """
        Validate and stage one versioned KnowledgeAsset.

        Version allocation is deterministic within the requested
        Organization and exact normalized title:

        - no previous asset -> version 1;
        - previous asset exists -> latest version + 1.

        The caller owns commit, rollback, audit creation, and any larger
        atomic workflow.
        """

        organization = self._require_organization(
            organization_id
        )

        normalized_title = self._normalize_required_text(
            field_name="KnowledgeAsset title",
            value=title,
        )

        normalized_guidance = self._normalize_required_text(
            field_name="KnowledgeAsset guidance",
            value=guidance,
        )

        normalized_summary = self._normalize_optional_text(
            summary
        )

        normalized_source_system = (
            self._normalize_optional_text(
                source_system
            )
        )

        normalized_source_identifier = (
            self._normalize_optional_text(
                source_identifier
            )
        )

        normalized_category = self._normalize_category(
            category
        )

        normalized_status = self._normalize_status(
            status
        )

        if (
            not isinstance(confidence_score, int)
            or isinstance(confidence_score, bool)
            or confidence_score < 0
            or confidence_score > 100
        ):
            raise KnowledgeAssetValidationError(
                "KnowledgeAsset confidence score must be "
                "an integer from 0 through 100."
            )

        latest_version = self.repository.get_latest_version(
            organization_id=organization.id,
            title=normalized_title,
        )

        next_version = (
            1
            if latest_version is None
            else latest_version.version + 1
        )

        knowledge_asset = KnowledgeAsset(
            organization_id=organization.id,
            title=normalized_title,
            summary=normalized_summary,
            guidance=normalized_guidance,
            category=normalized_category,
            status=normalized_status,
            version=next_version,
            source_system=normalized_source_system,
            source_identifier=normalized_source_identifier,
            confidence_score=confidence_score,
            created_by=actor,
            updated_by=actor,
        )

        try:
            knowledge_asset = self.repository.create(
                knowledge_asset
            )

            self.audit_service.record_pending(
                event_type="KnowledgeAssetCreated",
                entity_type="KnowledgeAsset",
                entity_id=knowledge_asset.id,
                actor=actor,
                message=(
                    f"Knowledge Asset '{knowledge_asset.title}' "
                    f"version {knowledge_asset.version} was created."
                ),
                metadata={
                    "organization_id": organization.id,
                    "knowledge_asset_id": knowledge_asset.id,
                    "title": knowledge_asset.title,
                    "version": knowledge_asset.version,
                    "category": knowledge_asset.category,
                    "status": knowledge_asset.status,
                    "source_system": (
                        knowledge_asset.source_system
                    ),
                    "source_identifier": (
                        knowledge_asset.source_identifier
                    ),
                    "confidence_score": (
                        knowledge_asset.confidence_score
                    ),
                    "transaction_mode": "CallerOwned",
                    "actor_trust": (
                        "CallerSupplied"
                        if actor
                        else "Unattributed"
                    ),
                },
            )

            return knowledge_asset

        except IntegrityError as error:
            raise KnowledgeAssetDuplicateVersionError(
                "The KnowledgeAsset version could not be created "
                "because the Organization, title, and version "
                "combination already exists."
            ) from error

    def list_for_organization(
        self,
        organization_id: str,
    ) -> list[KnowledgeAsset]:
        """
        Return all KnowledgeAssets belonging to one known Organization.
        """

        organization = self._require_organization(
            organization_id
        )

        return self.repository.list_for_organization(
            organization.id
        )

    def get_by_id(
        self,
        *,
        organization_id: str,
        knowledge_asset_id: str,
    ) -> KnowledgeAsset | None:
        """
        Return one KnowledgeAsset only within the requested Organization.

        A KnowledgeAsset belonging to another Organization is treated as not
        found so the service does not disclose cross-Organization existence.
        """

        organization = self._require_organization(
            organization_id
        )

        return self.repository.get_by_id(
            organization_id=organization.id,
            knowledge_asset_id=knowledge_asset_id,
        )
