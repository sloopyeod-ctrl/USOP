from sqlalchemy.orm import Session

from app.models.knowledge_asset import KnowledgeAsset


class KnowledgeAssetRepository:
    """
    Persistence boundary for Organization-scoped KnowledgeAsset records.

    This repository stores and retrieves Organizational Memory assets but
    performs no lifecycle validation, version calculation, authorization,
    approval workflow, relationship management, or transaction management.

    The calling service owns commit and rollback.
    """

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        knowledge_asset: KnowledgeAsset,
    ) -> KnowledgeAsset:
        """
        Add a KnowledgeAsset to the caller-owned transaction.
        """

        self.db.add(knowledge_asset)
        self.db.flush()
        self.db.refresh(knowledge_asset)

        return knowledge_asset

    def get_by_id(
        self,
        *,
        organization_id: str,
        knowledge_asset_id: str,
    ) -> KnowledgeAsset | None:
        """
        Retrieve one KnowledgeAsset within its Organization boundary.
        """

        return (
            self.db.query(KnowledgeAsset)
            .filter(
                KnowledgeAsset.organization_id
                == organization_id,
                KnowledgeAsset.id
                == knowledge_asset_id,
            )
            .one_or_none()
        )

    def list_for_organization(
        self,
        organization_id: str,
    ) -> list[KnowledgeAsset]:
        """
        List all KnowledgeAssets for one Organization.

        Results are deterministic: title ascending, version descending,
        and ID ascending as the final stable tie-breaker.
        """

        return (
            self.db.query(KnowledgeAsset)
            .filter(
                KnowledgeAsset.organization_id
                == organization_id,
            )
            .order_by(
                KnowledgeAsset.title.asc(),
                KnowledgeAsset.version.desc(),
                KnowledgeAsset.id.asc(),
            )
            .all()
        )

    def list_active(
        self,
        organization_id: str,
    ) -> list[KnowledgeAsset]:
        """
        List active KnowledgeAssets for one Organization.

        Active here refers only to the shared record-level is_active flag.
        KnowledgeAsset lifecycle interpretation belongs to the service layer.
        """

        return (
            self.db.query(KnowledgeAsset)
            .filter(
                KnowledgeAsset.organization_id
                == organization_id,
                KnowledgeAsset.is_active.is_(True),
            )
            .order_by(
                KnowledgeAsset.title.asc(),
                KnowledgeAsset.version.desc(),
                KnowledgeAsset.id.asc(),
            )
            .all()
        )

    def list_by_category(
        self,
        *,
        organization_id: str,
        category: str,
    ) -> list[KnowledgeAsset]:
        """
        List KnowledgeAssets in one category within one Organization.
        """

        return (
            self.db.query(KnowledgeAsset)
            .filter(
                KnowledgeAsset.organization_id
                == organization_id,
                KnowledgeAsset.category
                == category,
            )
            .order_by(
                KnowledgeAsset.title.asc(),
                KnowledgeAsset.version.desc(),
                KnowledgeAsset.id.asc(),
            )
            .all()
        )
