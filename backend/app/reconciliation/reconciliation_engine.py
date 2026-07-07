from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.identity import Identity


class ReconciliationEngine:
    def __init__(self, db: Session):
        self.db = db

    def reconcile(self, normalized: dict):
        summary = {
            "identities_created": 0,
            "identities_updated": 0,
            "accounts_created": 0,
            "accounts_updated": 0,
            "groups_created": 0,
            "groups_updated": 0,
            "roles_created": 0,
            "roles_updated": 0,
        }

        #
        # Reconcile identities
        #
        for identity in normalized.get("identities", []):
            existing = (
                self.db.query(Identity)
                .filter(
                    func.lower(Identity.primary_email)
                    == identity["primary_email"].lower()
                )
                .first()
            )

            if existing:
                existing.display_name = identity["display_name"]
                summary["identities_updated"] += 1

            else:
                self.db.add(
                    Identity(
                        display_name=identity["display_name"],
                        primary_email=identity["primary_email"],
                    )
                )

                summary["identities_created"] += 1

        self.db.commit()

        return summary