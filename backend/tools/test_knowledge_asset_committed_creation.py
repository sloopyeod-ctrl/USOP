import sys
import uuid
from pathlib import Path
from unittest.mock import patch

from dotenv import load_dotenv


BACKEND_ROOT = Path(__file__).resolve().parents[1]

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

load_dotenv(
    dotenv_path=BACKEND_ROOT / ".env",
    override=False,
)


from app.database.session import SessionLocal
from app.domain import (
    KnowledgeAssetStatus,
    KnowledgeCategory,
)
from app.models.audit_event import AuditEvent
from app.models.knowledge_asset import KnowledgeAsset
from app.models.organization import Organization
from app.services.knowledge_asset_service import (
    KnowledgeAssetService,
)


ACTOR = "USOP Knowledge Asset Committed Creation Regression"


def knowledge_asset_audits(db, entity_id: str) -> list[AuditEvent]:
    """
    Return all immutable audit events for one KnowledgeAsset.

    AuditEvent does not duplicate Organization ownership as a column.
    Organization context remains inside metadata_json while entity_id
    provides the canonical audit-to-asset relationship.
    """

    return (
        db.query(AuditEvent)
        .filter(
            AuditEvent.entity_type == "KnowledgeAsset",
            AuditEvent.entity_id == entity_id,
        )
        .order_by(
            AuditEvent.created_at.asc(),
            AuditEvent.id.asc(),
        )
        .all()
    )


def audit_exists_for_title(
    db,
    *,
    title: str,
) -> bool:
    """
    Determine whether any KnowledgeAsset audit references a title.

    Metadata inspection is intentionally performed in Python rather than
    through database-specific JSON query syntax so the regression remains
    portable across supported SQLAlchemy database engines.
    """

    events = (
        db.query(AuditEvent)
        .filter(
            AuditEvent.entity_type == "KnowledgeAsset",
        )
        .all()
    )

    return any(
        isinstance(event.metadata_json, dict)
        and event.metadata_json.get("title") == title
        for event in events
    )


def main() -> int:
    print(
        "USOP Knowledge Asset Committed Creation Regression"
    )
    print(
        "--------------------------------------------------"
    )

    db = SessionLocal()
    service = KnowledgeAssetService(db)

    suffix = uuid.uuid4().hex

    organization_id: str | None = None
    committed_asset_id: str | None = None
    pending_asset_id: str | None = None

    committed_title = (
        f"Privileged Access Review Standard {suffix}"
    )
    pending_title = (
        f"Pending Transaction Standard {suffix}"
    )
    failed_title = (
        f"Failed Creation Standard {suffix}"
    )

    errors: list[str] = []

    try:
        organization = Organization(
            name=(
                "Knowledge Asset Committed Creation "
                f"{suffix}"
            ),
            slug=(
                "knowledge-asset-committed-creation-"
                f"{suffix}"
            ),
            status="Active",
            organization_type="Customer",
            time_zone="UTC",
            created_by=ACTOR,
            updated_by=ACTOR,
        )

        db.add(organization)
        db.commit()
        db.refresh(organization)

        organization_id = organization.id

        # -------------------------------------------------------------
        # Committed creation
        # -------------------------------------------------------------

        with patch.object(
            db,
            "commit",
            wraps=db.commit,
        ) as commit_mock:
            committed_asset = service.create(
                organization_id=organization_id,
                title=f"  {committed_title}  ",
                summary=(
                    "  Defines the approved review process.  "
                ),
                guidance=(
                    "  Review privileged assignments before "
                    "approval and document the decision.  "
                ),
                category=KnowledgeCategory.AUTHORIZATION,
                status=KnowledgeAssetStatus.DRAFT,
                source_system="  Entra ID  ",
                source_identifier="  PAM-001  ",
                confidence_score=95,
                actor=ACTOR,
            )

        committed_asset_id = committed_asset.id
        committed_creation_commits_once = (
            commit_mock.call_count == 1
        )

        with SessionLocal() as verification_db:
            persisted_asset = (
                verification_db.query(KnowledgeAsset)
                .filter(
                    KnowledgeAsset.id == committed_asset_id,
                    KnowledgeAsset.organization_id
                    == organization_id,
                )
                .one_or_none()
            )

            committed_audits = knowledge_asset_audits(
                verification_db,
                committed_asset_id,
            )

            committed_asset_persisted = (
                persisted_asset is not None
            )

            committed_fields_normalized = (
                persisted_asset is not None
                and persisted_asset.title == committed_title
                and persisted_asset.summary
                == "Defines the approved review process."
                and persisted_asset.guidance
                == (
                    "Review privileged assignments before "
                    "approval and document the decision."
                )
                and persisted_asset.source_system == "Entra ID"
                and persisted_asset.source_identifier == "PAM-001"
            )

            exactly_one_committed_audit = (
                len(committed_audits) == 1
            )

            committed_audit_correct = (
                exactly_one_committed_audit
                and committed_audits[0].event_type
                == "KnowledgeAssetCreated"
                and committed_audits[0].entity_type
                == "KnowledgeAsset"
                and committed_audits[0].entity_id
                == committed_asset_id
                and committed_audits[0].actor == ACTOR
                and isinstance(
                    committed_audits[0].metadata_json,
                    dict,
                )
                and committed_audits[0].metadata_json.get(
                    "organization_id"
                )
                == organization_id
                and committed_audits[0].metadata_json.get(
                    "title"
                )
                == committed_title
                and committed_audits[0].metadata_json.get(
                    "transaction_mode"
                )
                == "CallerOwned"
            )

        # -------------------------------------------------------------
        # Caller-owned pending creation
        # -------------------------------------------------------------

        with patch.object(
            db,
            "commit",
            wraps=db.commit,
        ) as pending_commit_mock:
            pending_asset = service.create_pending(
                organization_id=organization_id,
                title=pending_title,
                guidance=(
                    "This KnowledgeAsset must remain inside "
                    "the caller-owned transaction."
                ),
                category=(
                    KnowledgeCategory.OPERATIONAL_PROCEDURE
                ),
                actor=ACTOR,
            )

            pending_asset_id = pending_asset.id

            pending_visible_before_rollback = (
                db.query(KnowledgeAsset)
                .filter(
                    KnowledgeAsset.id == pending_asset_id,
                )
                .one_or_none()
                is not None
            )

            pending_audit_visible_before_rollback = (
                len(
                    knowledge_asset_audits(
                        db,
                        pending_asset_id,
                    )
                )
                == 1
            )

            pending_creation_committed = (
                pending_commit_mock.call_count > 0
            )

            db.rollback()

        with SessionLocal() as verification_db:
            pending_asset_persisted = (
                verification_db.query(KnowledgeAsset)
                .filter(
                    KnowledgeAsset.id == pending_asset_id,
                )
                .one_or_none()
                is not None
            )

            pending_audit_persisted = (
                len(
                    knowledge_asset_audits(
                        verification_db,
                        pending_asset_id,
                    )
                )
                > 0
            )

        # -------------------------------------------------------------
        # Failed committed creation
        # -------------------------------------------------------------

        rollback_called_once = False
        expected_commit_failure_propagated = False

        with patch.object(
            db,
            "commit",
            side_effect=RuntimeError(
                "Simulated KnowledgeAsset commit failure."
            ),
        ), patch.object(
            db,
            "rollback",
            wraps=db.rollback,
        ) as rollback_mock:
            try:
                service.create(
                    organization_id=organization_id,
                    title=failed_title,
                    guidance=(
                        "This KnowledgeAsset and its audit event "
                        "must not survive a failed commit."
                    ),
                    category=KnowledgeCategory.INFRASTRUCTURE,
                    actor=ACTOR,
                )
            except RuntimeError as error:
                expected_commit_failure_propagated = (
                    str(error)
                    == "Simulated KnowledgeAsset commit failure."
                )

                rollback_called_once = (
                    rollback_mock.call_count == 1
                )

        with SessionLocal() as verification_db:
            failed_asset_persisted = (
                verification_db.query(KnowledgeAsset)
                .filter(
                    KnowledgeAsset.organization_id
                    == organization_id,
                    KnowledgeAsset.title == failed_title,
                )
                .one_or_none()
                is not None
            )

            failed_audit_persisted = (
                audit_exists_for_title(
                    verification_db,
                    title=failed_title,
                )
            )

        validations = {
            "Committed creation called commit once": (
                committed_creation_commits_once
            ),
            "Committed KnowledgeAsset persisted": (
                committed_asset_persisted
            ),
            "Committed fields normalized": (
                committed_fields_normalized
            ),
            "Exactly one committed audit persisted": (
                exactly_one_committed_audit
            ),
            "Committed audit contract correct": (
                committed_audit_correct
            ),
            "create_pending() committed transaction": (
                pending_creation_committed
            ),
            "Pending asset visible before rollback": (
                pending_visible_before_rollback
            ),
            "Pending audit visible before rollback": (
                pending_audit_visible_before_rollback
            ),
            "Pending asset persisted after rollback": (
                pending_asset_persisted
            ),
            "Pending audit persisted after rollback": (
                pending_audit_persisted
            ),
            "Commit failure propagated": (
                expected_commit_failure_propagated
            ),
            "Failed commit triggered one rollback": (
                rollback_called_once
            ),
            "Failed asset persisted": (
                failed_asset_persisted
            ),
            "Failed audit persisted": (
                failed_audit_persisted
            ),
        }

        for label, result in validations.items():
            print(f"{label}: {result}")

        if not committed_creation_commits_once:
            errors.append(
                "create() did not commit exactly once."
            )

        if not committed_asset_persisted:
            errors.append(
                "create() did not persist the KnowledgeAsset."
            )

        if not committed_fields_normalized:
            errors.append(
                "create() did not preserve normalized domain fields."
            )

        if not exactly_one_committed_audit:
            errors.append(
                "create() did not persist exactly one audit event."
            )

        if not committed_audit_correct:
            errors.append(
                "The committed audit contract was incorrect."
            )

        if pending_creation_committed:
            errors.append(
                "create_pending() committed the caller transaction."
            )

        if not pending_visible_before_rollback:
            errors.append(
                "The pending KnowledgeAsset was not staged."
            )

        if not pending_audit_visible_before_rollback:
            errors.append(
                "The pending audit event was not staged."
            )

        if pending_asset_persisted:
            errors.append(
                "The pending KnowledgeAsset survived rollback."
            )

        if pending_audit_persisted:
            errors.append(
                "The pending audit event survived rollback."
            )

        if not expected_commit_failure_propagated:
            errors.append(
                "The simulated commit failure was not propagated."
            )

        if not rollback_called_once:
            errors.append(
                "A failed create() did not call rollback exactly once."
            )

        if failed_asset_persisted:
            errors.append(
                "The failed KnowledgeAsset was persisted."
            )

        if failed_audit_persisted:
            errors.append(
                "The failed KnowledgeAsset audit was persisted."
            )

        print()

        if errors:
            print("Validation: FAILED")

            for error in errors:
                print(f"- {error}")

            return 1

        print("Validation: PASSED")
        print(
            "KnowledgeAssetService.create() owns committed "
            "transaction completion, persists the KnowledgeAsset "
            "and immutable audit event atomically, rolls both back "
            "when commit fails, and preserves create_pending() for "
            "larger caller-owned workflows."
        )

        return 0

    finally:
        try:
            db.rollback()

            if organization_id is not None:
                remaining_asset_ids = [
                    asset_id
                    for (asset_id,) in (
                        db.query(KnowledgeAsset.id)
                        .filter(
                            KnowledgeAsset.organization_id
                            == organization_id,
                        )
                        .all()
                    )
                ]

                if remaining_asset_ids:
                    (
                        db.query(AuditEvent)
                        .filter(
                            AuditEvent.entity_type
                            == "KnowledgeAsset",
                            AuditEvent.entity_id.in_(
                                remaining_asset_ids
                            ),
                        )
                        .delete(
                            synchronize_session=False
                        )
                    )

                    (
                        db.query(KnowledgeAsset)
                        .filter(
                            KnowledgeAsset.id.in_(
                                remaining_asset_ids
                            )
                        )
                        .delete(
                            synchronize_session=False
                        )
                    )

                (
                    db.query(Organization)
                    .filter(
                        Organization.id == organization_id,
                    )
                    .delete(
                        synchronize_session=False
                    )
                )

            db.commit()

        except Exception as cleanup_error:
            db.rollback()
            print(
                "Cleanup warning: "
                f"{cleanup_error}"
            )

        finally:
            db.close()


if __name__ == "__main__":
    raise SystemExit(main())
