from sqlalchemy.orm import Session

from app.models.knowledge_asset import KnowledgeAsset
from app.repositories.knowledge_asset_repository import (
    KnowledgeAssetRepository,
)
from app.repositories.organization_repository import (
    OrganizationRepository,
)


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
    Raised when a requested KnowledgeAsset version conflicts with
    existing Organizational Memory.
    """


class KnowledgeAssetService:
    """
    Backend authority for Organization-scoped Organizational Memory.

    This initial service foundation exposes read-only operations. It validates
    the Organization boundary before querying KnowledgeAssets and does not
    create records, allocate versions, write audit events, authorize callers,
    or manage database transactions during reads.
    """

    def __init__(self, db: Session):
        self.db = db
        self.organization_repository = OrganizationRepository(db)
        self.repository = KnowledgeAssetRepository(db)

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

    def list_for_organization(
        self,
        organization_id: str,
    ) -> list[KnowledgeAsset]:
        """
        Return all KnowledgeAssets belonging to one known Organization.

        This read operation does not allocate versions, interpret lifecycle
        status, authorize the caller, write audit events, or manage a
        transaction.
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
