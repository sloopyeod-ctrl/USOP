import sys
import uuid
from pathlib import Path

from dotenv import load_dotenv


BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

load_dotenv(
    dotenv_path=BACKEND_ROOT / ".env",
    override=False,
)

from app.database.session import SessionLocal
from app.models.audit_event import AuditEvent
from app.services.audit_service import AuditService


def main() -> int:
    print("USOP Transaction-Safe Audit Regression")
    print("--------------------------------------")

    db = SessionLocal()
    audit_service = AuditService(db)

    suffix = uuid.uuid4().hex
    pending_entity_id = str(uuid.uuid4())
    committed_entity_id = str(uuid.uuid4())

    errors: list[str] = []

    try:
        pending_event = audit_service.record_pending(
            event_type="TransactionRegressionPending",
            entity_type="TransactionRegression",
            entity_id=pending_entity_id,
            actor="USOP Regression",
            message=(
                "Pending audit event should disappear "
                "when the caller rolls back."
            ),
            metadata={
                "regression_suffix": suffix,
                "transaction_mode": "CallerOwned",
            },
        )

        if pending_event.id is None:
            errors.append(
                "Pending audit event did not receive an ID after flush."
            )

        visible_inside_transaction = (
            db.query(AuditEvent)
            .filter(
                AuditEvent.id == pending_event.id,
            )
            .one_or_none()
        )

        if visible_inside_transaction is None:
            errors.append(
                "Pending audit event was not visible inside its transaction."
            )

        db.rollback()

        persisted_after_rollback = (
            db.query(AuditEvent)
            .filter(
                AuditEvent.entity_id == pending_entity_id,
            )
            .one_or_none()
        )

        if persisted_after_rollback is not None:
            errors.append(
                "record_pending() committed an audit event unexpectedly."
            )

        committed_event = audit_service.record(
            event_type="TransactionRegressionCommitted",
            entity_type="TransactionRegression",
            entity_id=committed_entity_id,
            actor="USOP Regression",
            message=(
                "Legacy audit path should remain committed "
                "during incremental migration."
            ),
            metadata={
                "regression_suffix": suffix,
                "transaction_mode": "LegacyCommitted",
            },
        )

        persisted_committed_event = (
            db.query(AuditEvent)
            .filter(
                AuditEvent.id == committed_event.id,
            )
            .one_or_none()
        )

        if persisted_committed_event is None:
            errors.append(
                "Legacy record() path no longer commits audit events."
            )

        if errors:
            print()
            print("Validation: FAILED")

            for error in errors:
                print(f"- {error}")

            return 1

        print(
            "Pending event visible before rollback: "
            f"{visible_inside_transaction is not None}"
        )
        print(
            "Pending event persisted after rollback: "
            f"{persisted_after_rollback is not None}"
        )
        print(
            "Legacy committed event persisted: "
            f"{persisted_committed_event is not None}"
        )
        print("New workflows can share service transactions: True")
        print("Legacy workflows remain compatible: True")

        print()
        print("Validation: PASSED")
        print(
            "Audit persistence now supports caller-owned atomic transactions "
            "without breaking existing committed audit workflows."
        )

        return 0

    finally:
        db.rollback()

        (
            db.query(AuditEvent)
            .filter(
                AuditEvent.entity_id.in_(
                    [
                        pending_entity_id,
                        committed_entity_id,
                    ]
                )
            )
            .delete(
                synchronize_session=False
            )
        )

        db.commit()
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
