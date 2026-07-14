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
from app.domain import (
    ApprovalStatus,
    DecisionStatus,
    DecisionType,
    VerificationStatus,
)
from app.models.identity import Identity
from app.repositories.decision_record_repository import (
    DecisionRecordRepository,
)
from app.schemas.decision_record import (
    DecisionRecordCreate,
)


def main() -> int:
    print("USOP Decision Record Persistence Regression")
    print("-------------------------------------------")

    db = SessionLocal()
    created_record_id = None

    try:
        identity = (
            db.query(Identity)
            .filter(Identity.is_active.is_(True))
            .order_by(Identity.display_name)
            .first()
        )

        if identity is None:
            print("Validation: FAILED")
            print("- No active identity is available for testing.")
            return 1

        repository = DecisionRecordRepository(db)

        source_identifier = (
            "decision-record-regression-"
            f"{uuid.uuid4()}"
        )

        payload = DecisionRecordCreate(
            identity_id=identity.id,
            decision_type=DecisionType.ACCEPT_RISK,
            status=DecisionStatus.DRAFT,
            title="Regression test risk decision",
            justification=(
                "Validate DecisionRecord persistence "
                "without establishing organizational policy."
            ),
            notes="Temporary automated regression record.",
            recommendation_type="Authorization",
            recommendation_title=(
                "Review privileged role assignment"
            ),
            risk_level="Critical",
            risk_score=95,
            decision_confidence=100,
            evidence_snapshot_json={
                "source": "RegressionTest",
                "role": "Global Administrator",
                "scope": "TenantWide",
                "contains_secret": False,
            },
            approval_status=(
                ApprovalStatus.NOT_REQUIRED
            ),
            verification_status=(
                VerificationStatus.NOT_REQUIRED
            ),
            source_system="USOP",
            source_identifier=source_identifier,
            confidence_score=100,
        )

        created = repository.create(payload)
        created_record_id = created.id

        errors = []

        if not created.id:
            errors.append(
                "Created DecisionRecord has no ID."
            )

        if created.identity_id != identity.id:
            errors.append(
                "Identity foreign key was not persisted."
            )

        if (
            created.decision_type
            != DecisionType.ACCEPT_RISK.value
        ):
            errors.append(
                "Decision type was not persisted canonically."
            )

        if (
            created.status
            != DecisionStatus.DRAFT.value
        ):
            errors.append(
                "Decision status was not persisted canonically."
            )

        if (
            created.approval_status
            != ApprovalStatus.NOT_REQUIRED.value
        ):
            errors.append(
                "Approval status was not persisted correctly."
            )

        if (
            created.verification_status
            != VerificationStatus.NOT_REQUIRED.value
        ):
            errors.append(
                "Verification status was not persisted correctly."
            )

        if created.risk_score != 95:
            errors.append(
                "Risk score was not persisted."
            )

        if created.decision_confidence != 100:
            errors.append(
                "Decision confidence was not persisted."
            )

        evidence = created.evidence_snapshot_json or {}

        if evidence.get("role") != "Global Administrator":
            errors.append(
                "Evidence snapshot was not persisted."
            )

        if evidence.get("contains_secret") is not False:
            errors.append(
                "Evidence snapshot changed unexpectedly."
            )

        if created.source_identifier != source_identifier:
            errors.append(
                "Source identifier was not persisted."
            )

        if not created.created_at:
            errors.append(
                "Created timestamp was not generated."
            )

        if not created.updated_at:
            errors.append(
                "Updated timestamp was not generated."
            )

        identity_records = repository.by_identity(
            identity.id
        )

        matching_records = [
            record
            for record in identity_records
            if record.id == created.id
        ]

        if len(matching_records) != 1:
            errors.append(
                "Identity lookup did not return the "
                "created DecisionRecord exactly once."
            )

        if errors:
            print()
            print("Validation: FAILED")

            for error in errors:
                print(f"- {error}")

            return 1

        print(f"Identity: {identity.display_name}")
        print(f"Decision ID: {created.id}")
        print(f"Decision type: {created.decision_type}")
        print(f"Status: {created.status}")
        print(f"Risk level: {created.risk_level}")
        print(f"Risk score: {created.risk_score}")
        print(
            "Decision confidence: "
            f"{created.decision_confidence}"
        )
        print(
            "Approval status: "
            f"{created.approval_status}"
        )
        print(
            "Verification status: "
            f"{created.verification_status}"
        )
        print(
            "Identity decision count: "
            f"{len(identity_records)}"
        )

        print()
        print("Validation: PASSED")
        print(
            "DecisionRecord persistence, canonical "
            "vocabulary, evidence storage, and identity "
            "retrieval are operating correctly."
        )

        return 0

    finally:
        if created_record_id:
            record = repository.get_by_id(
                created_record_id
            )

            if record is not None:
                db.delete(record)
                db.commit()

        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
