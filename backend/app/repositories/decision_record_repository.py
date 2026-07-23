from sqlalchemy.orm import Session

from app.models.decision_record import DecisionRecord
from app.repositories.base_repository import (
    BaseRepository,
)
from app.schemas.decision_record import (
    DecisionRecordCreate,
)


class DecisionRecordRepository(
    BaseRepository[
        DecisionRecord,
        DecisionRecordCreate,
    ]
):
    def __init__(self, db: Session):
        super().__init__(
            db,
            DecisionRecord,
        )

    def list_for_organization(
        self,
        organization_id: str,
    ) -> list[DecisionRecord]:
        return (
            self.db.query(DecisionRecord)
            .filter(
                DecisionRecord.organization_id
                == organization_id,
                DecisionRecord.is_active.is_(True),
            )
            .order_by(
                DecisionRecord.created_at.desc(),
                DecisionRecord.id.asc(),
            )
            .all()
        )

    def get_by_id_for_organization(
        self,
        *,
        organization_id: str,
        decision_id: str,
    ) -> DecisionRecord | None:
        return (
            self.db.query(DecisionRecord)
            .filter(
                DecisionRecord.organization_id
                == organization_id,
                DecisionRecord.id
                == decision_id,
                DecisionRecord.is_active.is_(True),
            )
            .one_or_none()
        )

    def by_identity(
        self,
        *,
        organization_id: str,
        identity_id: str,
    ) -> list[DecisionRecord]:
        return (
            self.db.query(DecisionRecord)
            .filter(
                DecisionRecord.organization_id
                == organization_id,
                DecisionRecord.identity_id
                == identity_id,
                DecisionRecord.is_active.is_(True),
            )
            .order_by(
                DecisionRecord.created_at.desc(),
                DecisionRecord.id.asc(),
            )
            .all()
        )
