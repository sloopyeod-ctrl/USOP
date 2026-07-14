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

    def by_identity(
        self,
        identity_id: str,
    ) -> list[DecisionRecord]:
        return (
            self.db.query(DecisionRecord)
            .filter(
                DecisionRecord.identity_id
                == identity_id,
                DecisionRecord.is_active.is_(True),
            )
            .order_by(
                DecisionRecord.created_at.desc()
            )
            .all()
        )
