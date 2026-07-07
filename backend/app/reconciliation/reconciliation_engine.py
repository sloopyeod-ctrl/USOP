from sqlalchemy.orm import Session


class ReconciliationEngine:
    def __init__(self, db: Session):
        self.db = db

    def reconcile(self, normalized: dict):
        return {
            "identities_created": 0,
            "identities_updated": 0,
            "accounts_created": 0,
            "accounts_updated": 0,
            "groups_created": 0,
            "groups_updated": 0,
            "roles_created": 0,
            "roles_updated": 0,
        }