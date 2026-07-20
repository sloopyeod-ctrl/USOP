import sys
import uuid
from pathlib import Path
from types import MethodType

from dotenv import load_dotenv


BACKEND_ROOT = Path(__file__).resolve().parents[1]
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


ACTOR = "USOP Knowledge Asset Audit Regression"


def main() -> int:
    print("USOP Knowledge Asset Pending Audit Regression")
    print("---------------------------------------------")

    db = SessionLocal()
    service = KnowledgeAssetService(db)

    suffix = uuid.uuid4().hex

    organization_id: str | None = None
    knowledge_asset_id: str | None = None

    errors: list[str] = []

    legacy_record_called = False

    def prohibit_legacy_record(
        _self,
        **_kwargs,
    ):
        nonlocal legacy_record_called
        legacy_record_called = True

        raise AssertionError(
            "KnowledgeAssetService used legacy AuditService.record()."
        )

    service.audit_service.record = MethodType(
        prohibit_legacy_record,
        service.audit_service,
    )

    try:
        organization = Organization(
            name="Knowledge Asset Audit Regression",
            slug=f"knowledge-asset-audit-{suffix}",
            status="Active",
            organization_type="Customer",
            time_zone="UTC",
            created_by=ACTOR,
            updated_by=ACTOR,
        )

        db.add(organization)
        db.flush()
        db.refresh(organization)

        organization_id = organization.id

        knowledge_asset = service.create_pending(
            organization_id=organization.id,
            title="Privileged Identity Management Policy",
            summary=(
                "Defines governance requirements for "
                "privileged role eligibility and activation."
            ),
            guidance=(
                "Require analyst review, approval, MFA, "
                "and time-bound activation."
            ),
            category=KnowledgeCategory.AUTHORIZATION,
            status=KnowledgeAssetStatus.DRAFT,
            source_system="USOP",
            source_identifier="pim-policy",
            confidence_score=100,
            actor=ACTOR,
        )

        knowledge_asset_id = knowledge_asset.id

        audit_events = (
            db.query(AuditEvent)
            .filter(
                AuditEvent.entity_type == "KnowledgeAsset",
                AuditEvent.entity_id == knowledge_asset.id,
            )
            .all()
        )

        audit_event = (
            audit_events[0]
            if len(audit_events) == 1
            else None
        )

        if len(audit_events) != 1:
            errors.append(
                "Pending KnowledgeAsset creation did not stage "
                "exactly one audit event."
            )

        expected_metadata = {
            "organization_id": organization.id,
            "knowledge_asset_id": knowledge_asset.id,
            "title": knowledge_asset.title,
            "version": knowledge_asset.version,
            "category": knowledge_asset.category,
            "status": knowledge_asset.status,
            "source_system": knowledge_asset.source_system,
            "source_identifier": (
                knowledge_asset.source_identifier
            ),
            "confidence_score": (
                knowledge_asset.confidence_score
            ),
            "transaction_mode": "CallerOwned",
            "actor_trust": "CallerSupplied",
        }

        if audit_event is not None:
            if audit_event.event_type != "KnowledgeAssetCreated":
                errors.append(
                    "KnowledgeAsset audit event type is incorrect."
                )

            if audit_event.entity_type != "KnowledgeAsset":
                errors.append(
                    "KnowledgeAsset audit entity type is incorrect."
                )

            if audit_event.entity_id != knowledge_asset.id:
                errors.append(
                    "KnowledgeAsset audit entity ID is incorrect."
                )

            if audit_event.actor != ACTOR:
                errors.append(
                    "KnowledgeAsset audit actor is incorrect."
                )

            actual_metadata = audit_event.metadata_json or {}

            for key, expected_value in expected_metadata.items():
                if actual_metadata.get(key) != expected_value:
                    errors.append(
                        "KnowledgeAsset audit metadata is incorrect "
                        f"for '{key}'."
                    )

        visible_asset_before_rollback = (
            db.query(KnowledgeAsset)
            .filter(
                KnowledgeAsset.id == knowledge_asset.id,
            )
            .one_or_none()
        )

        visible_audit_before_rollback = (
            db.query(AuditEvent)
            .filter(
                AuditEvent.entity_type == "KnowledgeAsset",
                AuditEvent.entity_id == knowledge_asset.id,
            )
            .one_or_none()
        )

        if visible_asset_before_rollback is None:
            errors.append(
                "Pending KnowledgeAsset was not visible "
                "inside the caller-owned transaction."
            )

        if visible_audit_before_rollback is None:
            errors.append(
                "Pending audit event was not visible "
                "inside the caller-owned transaction."
            )

        if legacy_record_called:
            errors.append(
                "KnowledgeAssetService used the legacy "
                "committed audit path."
            )

        # Cache all ORM-derived values before rollback. SQLAlchemy expires
        # pending objects when their transaction is rolled back.
        audit_event_type_correct = (
            audit_event is not None
            and audit_event.event_type
            == "KnowledgeAssetCreated"
        )

        audit_entity_binding_correct = (
            audit_event is not None
            and audit_event.entity_id
            == knowledge_asset.id
        )

        audit_actor_preserved = (
            audit_event is not None
            and audit_event.actor == ACTOR
        )

        audit_metadata_complete = (
            audit_event is not None
            and audit_event.metadata_json
            == expected_metadata
        )

        staged_asset_visible = (
            visible_asset_before_rollback is not None
        )

        staged_audit_visible = (
            visible_audit_before_rollback is not None
        )

        staged_audit_count = len(audit_events)

        db.rollback()

        persisted_asset = (
            db.query(KnowledgeAsset)
            .filter(
                KnowledgeAsset.id == knowledge_asset_id,
            )
            .one_or_none()
        )

        persisted_audit = (
            db.query(AuditEvent)
            .filter(
                AuditEvent.entity_type == "KnowledgeAsset",
                AuditEvent.entity_id == knowledge_asset_id,
            )
            .one_or_none()
        )

        persisted_organization = (
            db.query(Organization)
            .filter(
                Organization.id == organization_id,
            )
            .one_or_none()
        )

        if persisted_asset is not None:
            errors.append(
                "Pending KnowledgeAsset survived caller rollback."
            )

        if persisted_audit is not None:
            errors.append(
                "Pending KnowledgeAsset audit survived caller rollback."
            )

        if persisted_organization is not None:
            errors.append(
                "Pending audit creation committed the caller-owned "
                "Organization transaction."
            )

        if errors:
            print()
            print("Validation: FAILED")

            for error in errors:
                print(f"- {error}")

            return 1

        print(
            "KnowledgeAsset staged: "
            f"{staged_asset_visible}"
        )
        print(
            "Audit event staged: "
            f"{staged_audit_visible}"
        )
        print(
            "Audit event count: "
            f"{staged_audit_count}"
        )
        print(
            "Audit event type correct: "
            f"{audit_event_type_correct}"
        )
        print(
            "Audit entity binding correct: "
            f"{audit_entity_binding_correct}"
        )
        print(
            "Audit actor preserved: "
            f"{audit_actor_preserved}"
        )
        print(
            "Audit metadata complete: "
            f"{audit_metadata_complete}"
        )
        print(
            "Legacy committed audit used: "
            f"{legacy_record_called}"
        )
        print(
            "KnowledgeAsset persisted after rollback: "
            f"{persisted_asset is not None}"
        )
        print(
            "Audit persisted after rollback: "
            f"{persisted_audit is not None}"
        )

        print()
        print("Validation: PASSED")
        print(
            "KnowledgeAsset creation and its immutable audit event "
            "participate atomically in the caller-owned transaction "
            "without using the legacy committed audit path."
        )

        return 0

    finally:
        db.rollback()

        if knowledge_asset_id:
            (
                db.query(AuditEvent)
                .filter(
                    AuditEvent.entity_type == "KnowledgeAsset",
                    AuditEvent.entity_id == knowledge_asset_id,
                )
                .delete(
                    synchronize_session=False
                )
            )

            (
                db.query(KnowledgeAsset)
                .filter(
                    KnowledgeAsset.id == knowledge_asset_id,
                )
                .delete(
                    synchronize_session=False
                )
            )

        if organization_id:
            (
                db.query(KnowledgeAsset)
                .filter(
                    KnowledgeAsset.organization_id
                    == organization_id,
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
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
