from collections import Counter

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.organizational_identity import OrganizationalIdentity
from app.repositories.identity_repository import IdentityRepository
from app.repositories.organization_repository import OrganizationRepository
from app.repositories.organizational_identity_repository import (
    OrganizationalIdentityRepository,
)
from app.schemas.organizational_identity_placement import (
    OrganizationalIdentityPlacementReport,
    OrganizationalIdentityPlacementRequest,
    OrganizationalIdentityPlacementResultItem,
    PlacementDisposition,
)


class OrganizationalIdentityPlacementError(Exception):
    """Base error for explicit Organizational Identity placement."""


class OrganizationalIdentityPlacementOrganizationNotFoundError(
    OrganizationalIdentityPlacementError
):
    """Raised when the placement Organization does not exist."""


class OrganizationalIdentityPlacementValidationError(
    OrganizationalIdentityPlacementError
):
    """Raised when apply is requested for an unsafe batch."""


class OrganizationalIdentityPlacementEngine:
    """
    Trusted organization boundary for explicit canonical Identity placement.

    preview() validates and reports without writing.
    apply() validates the entire batch and commits atomically.
    """

    def __init__(
        self,
        db: Session,
        *,
        organizational_identity_repository: (
            OrganizationalIdentityRepository | None
        ) = None,
        organization_repository: OrganizationRepository | None = None,
        identity_repository: IdentityRepository | None = None,
    ):
        self.db = db
        self.organizational_identity_repository = (
            organizational_identity_repository
            or OrganizationalIdentityRepository(db)
        )
        self.organization_repository = (
            organization_repository
            or OrganizationRepository(db)
        )
        self.identity_repository = (
            identity_repository
            or IdentityRepository(db)
        )

    def preview(
        self,
        *,
        organization_id: str,
        request: OrganizationalIdentityPlacementRequest,
    ) -> OrganizationalIdentityPlacementReport:
        organization = self._require_organization(organization_id)

        return self._build_report(
            organization_id=organization.id,
            request=request,
            dry_run=True,
        )

    def apply(
        self,
        *,
        organization_id: str,
        request: OrganizationalIdentityPlacementRequest,
        actor: str,
    ) -> OrganizationalIdentityPlacementReport:
        normalized_actor = actor.strip()

        if not normalized_actor:
            raise OrganizationalIdentityPlacementValidationError(
                "Placement apply requires an explicit actor."
            )

        organization = self._require_organization(organization_id)

        preview = self._build_report(
            organization_id=organization.id,
            request=request,
            dry_run=True,
        )

        if not preview.can_apply:
            raise OrganizationalIdentityPlacementValidationError(
                "Placement batch contains invalid entries. "
                "Review the dry-run report before applying."
            )

        created_by_identity_id: dict[str, OrganizationalIdentity] = {}

        try:
            for item, result in zip(
                request.placements,
                preview.results,
                strict=True,
            ):
                if (
                    result.disposition
                    == PlacementDisposition.ALREADY_PLACED
                ):
                    continue

                identity = self.identity_repository.get_by_id(
                    item.identity_id
                )

                created = self.organizational_identity_repository.create(
                    OrganizationalIdentity(
                        organization_id=organization.id,
                        identity_id=identity.id,
                        display_name=(
                            item.display_name
                            or identity.display_name
                        ),
                        status=item.status,
                        created_by=normalized_actor,
                        updated_by=normalized_actor,
                    )
                )

                created_by_identity_id[item.identity_id] = created

            self.db.commit()

            for created in created_by_identity_id.values():
                self.db.refresh(created)

        except IntegrityError as error:
            self.db.rollback()
            raise OrganizationalIdentityPlacementValidationError(
                "Placement could not be committed because the "
                "organization boundary changed during apply."
            ) from error

        except Exception:
            self.db.rollback()
            raise

        results = []

        for preview_result in preview.results:
            created = created_by_identity_id.get(
                preview_result.identity_id
            )

            if created is None:
                results.append(preview_result)
                continue

            results.append(
                OrganizationalIdentityPlacementResultItem(
                    identity_id=created.identity_id,
                    organizational_identity_id=created.id,
                    display_name=created.display_name,
                    disposition=PlacementDisposition.CREATED,
                    message=(
                        "Organizational Identity created "
                        "for the requested Organization."
                    ),
                )
            )

        return self._summarize(
            organization_id=organization.id,
            dry_run=False,
            results=results,
        )

    def _require_organization(self, organization_id: str):
        organization = self.organization_repository.get_by_id(
            organization_id
        )

        if organization is None:
            raise OrganizationalIdentityPlacementOrganizationNotFoundError(
                "Placement references an unknown Organization."
            )

        return organization

    def _build_report(
        self,
        *,
        organization_id: str,
        request: OrganizationalIdentityPlacementRequest,
        dry_run: bool,
    ) -> OrganizationalIdentityPlacementReport:
        identity_counts = Counter(
            item.identity_id
            for item in request.placements
        )

        results = []

        for item in request.placements:
            if identity_counts[item.identity_id] > 1:
                results.append(
                    OrganizationalIdentityPlacementResultItem(
                        identity_id=item.identity_id,
                        display_name=item.display_name,
                        disposition=PlacementDisposition.INVALID,
                        message=(
                            "Canonical Identity appears more than "
                            "once in the placement request."
                        ),
                    )
                )
                continue

            identity = self.identity_repository.get_by_id(
                item.identity_id
            )

            if identity is None:
                results.append(
                    OrganizationalIdentityPlacementResultItem(
                        identity_id=item.identity_id,
                        display_name=item.display_name,
                        disposition=PlacementDisposition.INVALID,
                        message="Canonical Identity does not exist.",
                    )
                )
                continue

            existing = (
                self.organizational_identity_repository
                .get_for_identity(
                    organization_id=organization_id,
                    identity_id=identity.id,
                )
            )

            if existing is not None:
                results.append(
                    OrganizationalIdentityPlacementResultItem(
                        identity_id=identity.id,
                        organizational_identity_id=existing.id,
                        display_name=existing.display_name,
                        disposition=(
                            PlacementDisposition.ALREADY_PLACED
                        ),
                        message=(
                            "Canonical Identity is already placed "
                            "in the requested Organization."
                        ),
                    )
                )
                continue

            results.append(
                OrganizationalIdentityPlacementResultItem(
                    identity_id=identity.id,
                    display_name=(
                        item.display_name
                        or identity.display_name
                    ),
                    disposition=PlacementDisposition.READY,
                    message=(
                        "Placement is valid and ready to apply."
                    ),
                )
            )

        return self._summarize(
            organization_id=organization_id,
            dry_run=dry_run,
            results=results,
        )

    @staticmethod
    def _summarize(
        *,
        organization_id: str,
        dry_run: bool,
        results: list[
            OrganizationalIdentityPlacementResultItem
        ],
    ) -> OrganizationalIdentityPlacementReport:
        ready_count = sum(
            result.disposition == PlacementDisposition.READY
            for result in results
        )
        already_placed_count = sum(
            result.disposition
            == PlacementDisposition.ALREADY_PLACED
            for result in results
        )
        invalid_count = sum(
            result.disposition == PlacementDisposition.INVALID
            for result in results
        )
        created_count = sum(
            result.disposition == PlacementDisposition.CREATED
            for result in results
        )

        return OrganizationalIdentityPlacementReport(
            organization_id=organization_id,
            dry_run=dry_run,
            requested_count=len(results),
            ready_count=ready_count,
            already_placed_count=already_placed_count,
            invalid_count=invalid_count,
            created_count=created_count,
            can_apply=invalid_count == 0,
            results=results,
        )
