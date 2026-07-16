from sqlalchemy.orm import Session

from app.domain.license_status import LicenseStatus
from app.models.license import License


class LicenseRepository:
    """
    Persistence boundary for immutable USOP License records.

    This repository performs no commercial validation and makes no claim
    that an issued License is currently valid or operationally effective.

    Transaction ownership remains with the service layer so installation,
    supersession, and audit creation can occur atomically.
    """

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        license_record: License,
    ) -> License:
        """
        Add a new immutable License record to the current transaction.

        The caller owns commit or rollback.
        """

        self.db.add(license_record)
        self.db.flush()
        self.db.refresh(license_record)

        return license_record

    def get_by_id(
        self,
        license_id: str,
    ) -> License | None:
        return (
            self.db.query(License)
            .filter(
                License.id == license_id,
            )
            .one_or_none()
        )

    def get_by_identifier(
        self,
        license_identifier: str,
    ) -> License | None:
        return (
            self.db.query(License)
            .filter(
                License.license_identifier
                == license_identifier,
            )
            .one_or_none()
        )

    def get_latest_issued_for_organization(
        self,
        organization_id: str,
    ) -> License | None:
        """
        Return the newest License whose persisted lifecycle status is Issued.

        This is not commercial validation and must not be used as effective
        Subscription State. Future validation services will determine whether
        the returned License is currently usable.
        """

        return (
            self.db.query(License)
            .filter(
                License.organization_id
                == organization_id,
                License.status
                == LicenseStatus.ISSUED.value,
            )
            .order_by(
                License.issued_at.desc(),
                License.created_at.desc(),
                License.id.desc(),
            )
            .first()
        )

    def list_history_for_organization(
        self,
        organization_id: str,
    ) -> list[License]:
        return (
            self.db.query(License)
            .filter(
                License.organization_id
                == organization_id,
            )
            .order_by(
                License.issued_at.desc(),
                License.created_at.desc(),
                License.id.desc(),
            )
            .all()
        )
