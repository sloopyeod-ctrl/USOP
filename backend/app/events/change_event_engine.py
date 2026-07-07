from sqlalchemy.orm import Session

from app.services.audit_service import AuditService


class ChangeEventEngine:
    def __init__(self, db: Session):
        self.db = db
        self.audit_service = AuditService(db)

    def generate(self, identity_id: str, changes: dict):
        events = []

        event_map = {
            "added_accounts": "AccountAdded",
            "removed_accounts": "AccountRemoved",
            "added_groups": "GroupAdded",
            "removed_groups": "GroupRemoved",
            "added_roles": "RoleAdded",
            "removed_roles": "RoleRemoved",
        }

        for change_key, event_type in event_map.items():
            for value in changes.get(change_key, []):
                event = self.audit_service.record(
                    event_type=event_type,
                    entity_type="Identity",
                    entity_id=identity_id,
                    actor="USOP Change Event Engine",
                    message=f"{event_type}: {value}",
                    metadata={
                        "identity_id": identity_id,
                        "change_type": change_key,
                        "value": value,
                    },
                )

                events.append(
                    {
                        "event_type": event_type,
                        "value": value,
                        "event_id": event.id,
                    }
                )

        return events