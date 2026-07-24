import sys
from pathlib import Path

from dotenv import load_dotenv


BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(
    0,
    str(BACKEND_ROOT),
)

load_dotenv(
    dotenv_path=BACKEND_ROOT / ".env",
    override=False,
)


from app.database.session import SessionLocal
from app.domain import (
    AcceptanceType,
    DecisionType,
)
from app.intelligence.identity_intelligence_service import (
    IdentityIntelligenceService,
)
from app.models.audit_event import AuditEvent
from app.models.decision_record import DecisionRecord
from app.models.identity import Identity
from app.models.organization import Organization
from app.schemas.decision_record import (
    DecisionRecordAction,
)
from app.services.decision_record_service import (
    DecisionRecordService,
)


def main() -> int:
    print(
        "USOP Decision Record Service Regression"
    )
    print(
        "---------------------------------------"
    )

    db = SessionLocal()
    decision_id = None

    try:
        organization = (
            db.query(Organization)
            .filter(
                Organization.is_active.is_(True)
            )
            .order_by(
                Organization.created_at.asc(),
                Organization.id.asc(),
            )
            .first()
        )

        if organization is None:
            print("Validation: FAILED")
            print(
                "- No active Organization was found."
            )
            return 1

        identity = (
            db.query(Identity)
            .filter(
                Identity.is_active.is_(True)
            )
            .filter(
                Identity.display_name.ilike(
                    "%geoff%"
                )
            )
            .first()
        )

        if identity is None:
            print("Validation: FAILED")
            print(
                "- Geoff identity was not found."
            )
            return 1

        intelligence = (
            IdentityIntelligenceService(db)
            .get_identity_intelligence(
                identity.id
            )
        )

        recommendations = (
            intelligence.get(
                "recommendations",
                [],
            )
            if intelligence
            else []
        )

        if not recommendations:
            print("Validation: FAILED")
            print(
                "- No recommendations were found."
            )
            return 1

        recommendation = recommendations[0]

        recommendation_id = (
            recommendation.get(
                "recommendation_id"
            )
        )

        if not recommendation_id:
            print("Validation: FAILED")
            print(
                "- Recommendation ID was not "
                "generated."
            )
            return 1

        service = DecisionRecordService(db)

        action = DecisionRecordAction(
            decision_type=(
                DecisionType.ACCEPT_RISK
            ),
            justification=(
                "Regression validation of the "
                "Decision Record workflow."
            ),
            notes=(
                "This record will be removed after "
                "the test completes."
            ),
            acceptance_type=(
                AcceptanceType.TEMPORARY
            ),
            actor="Regression Test",
        )

        record = (
            service.create_decision_record(
                organization_id=(
                    organization.id
                ),
                identity_id=identity.id,
                recommendation_id=(
                    recommendation_id
                ),
                action=action,
            )
        )

        decision_id = record.id
        errors = []

        if record.status != "Accepted":
            errors.append(
                "AcceptRisk did not map to "
                "Accepted."
            )

        if (
            record.organization_id
            != organization.id
        ):
            errors.append(
                "Organization context was not "
                "preserved."
            )

        if record.identity_id != identity.id:
            errors.append(
                "Identity context was not "
                "preserved."
            )

        if (
            record.source_identifier
            != recommendation_id
        ):
            errors.append(
                "Stable recommendation identity "
                "was not preserved."
            )

        if not record.recommendation_title:
            errors.append(
                "Recommendation context was not "
                "populated."
            )

        if record.risk_level != "Critical":
            errors.append(
                "Current backend risk priority "
                "was not preserved."
            )

        if record.decision_confidence != 100:
            errors.append(
                "Decision confidence was not "
                "preserved."
            )

        snapshot = (
            record.evidence_snapshot_json or {}
        )

        snapshot_recommendation = (
            snapshot.get(
                "recommendation",
                {},
            )
        )

        if not snapshot_recommendation:
            errors.append(
                "Recommendation evidence was not "
                "stored."
            )

        if (
            snapshot_recommendation.get(
                "recommendation_id"
            )
            != recommendation_id
        ):
            errors.append(
                "Recommendation ID was not stored "
                "in the evidence snapshot."
            )

        events = (
            db.query(AuditEvent)
            .filter(
                AuditEvent.entity_type
                == "DecisionRecord",
                AuditEvent.entity_id
                == record.id,
            )
            .all()
        )

        if len(events) != 1:
            errors.append(
                "Exactly one DecisionCreated audit "
                "event was expected."
            )
        elif (
            events[0].event_type
            != "DecisionCreated"
        ):
            errors.append(
                "Audit event type is incorrect."
            )

        identity_records = (
            service.by_identity(
                organization_id=(
                    organization.id
                ),
                identity_id=identity.id,
            )
        )

        if not any(
            item.id == record.id
            for item in identity_records
        ):
            errors.append(
                "Identity decision-history lookup "
                "did not return the record."
            )

        if errors:
            print()
            print("Validation: FAILED")

            for error in errors:
                print(f"- {error}")

            return 1

        print(
            f"Organization: "
            f"{organization.name}"
        )
        print(
            f"Identity: "
            f"{identity.display_name}"
        )
        print(
            f"Recommendation ID: "
            f"{recommendation_id}"
        )
        print(
            f"Decision ID: {record.id}"
        )
        print(
            f"Decision type: "
            f"{record.decision_type}"
        )
        print(
            f"Status: {record.status}"
        )
        print(
            "Recommendation: "
            f"{record.recommendation_title}"
        )
        print(
            f"Risk level: "
            f"{record.risk_level}"
        )
        print(
            "Decision confidence: "
            f"{record.decision_confidence}%"
        )
        print(
            f"Audit events: {len(events)}"
        )

        print()
        print("Validation: PASSED")
        print(
            "Decision records resolve stable "
            "recommendation identifiers, preserve "
            "organization ownership, capture "
            "evidence, and generate an accountable "
            "audit event."
        )

        return 0

    finally:
        if decision_id:
            (
                db.query(AuditEvent)
                .filter(
                    AuditEvent.entity_type
                    == "DecisionRecord",
                    AuditEvent.entity_id
                    == decision_id,
                )
                .delete(
                    synchronize_session=False
                )
            )

            (
                db.query(DecisionRecord)
                .filter(
                    DecisionRecord.id
                    == decision_id
                )
                .delete(
                    synchronize_session=False
                )
            )

            db.commit()

        db.close()


if __name__ == "__main__":
    raise SystemExit(main())