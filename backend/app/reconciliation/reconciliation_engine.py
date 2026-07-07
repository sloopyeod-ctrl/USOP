from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.identity import Identity
from app.models.account import Account
from app.models.group import Group
from app.models.role import Role
from app.models.membership import Membership

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
            "memberships_created": 0,
            "memberships_updated": 0,
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

            #
        # Reconcile accounts
        #
        for account in normalized.get("accounts", []):
            existing = (
                self.db.query(Account)
                .filter(
                    func.lower(Account.username) == account["username"].lower(),
                    Account.system_name == account["system_name"],
                )
                .first()
            )

            if existing:
                existing.system_name = account["system_name"]
                summary["accounts_updated"] += 1

            else:
                identity = (
                    self.db.query(Identity)
                    .filter(Identity.is_active == True)
                    .first()
                )

                if identity:
                    self.db.add(
                        Account(
                            identity_id=identity.id,
                            username=account["username"],
                            display_name=account["username"],
                            system_name=account["system_name"],
                            source_system=account["source"],
                            source_identifier=account["username"],
                        )
                    )

                    summary["accounts_created"] += 1   

                #
        # Reconcile groups
        #
        for group in normalized.get("groups", []):
            existing = (
                self.db.query(Group)
                .filter(
                    func.lower(Group.name) == group["name"].lower()
                )
                .first()
            )

            if existing:
                summary["groups_updated"] += 1

            else:
                self.db.add(
                    Group(
                        name=group["name"],
                        source_system=group["source"],
                        source_identifier=group["name"],
                    )
                )

                summary["groups_created"] += 1  

                #
        # Reconcile roles
        #
        for role in normalized.get("roles", []):
           existing = (
                self.db.query(Role)
                .filter(
                    func.lower(Role.name) == role["name"].lower(),
                    Role.system_name == role["system_name"],
                )
                .first()
            )

           if existing:
                summary["roles_updated"] += 1

           else:
                self.db.add(
                    Role(
                        name=role["name"],
                        display_name=role["name"],
                        system_name=role["system_name"],
                        source_system=role["source"],
                        source_identifier=role["name"],
                    )
                )

                summary["roles_created"] += 1   

                #
        # Reconcile memberships
        #

        for membership in normalized.get("memberships", []):

            account = (
                self.db.query(Account)
                .filter(
                    func.lower(Account.username)
                    == membership["username"].lower()
                )
                .first()
            )

            group = (
                self.db.query(Group)
                .filter(
                    func.lower(Group.name)
                    == membership["group_name"].lower()
                )
                .first()
            )

            if not account or not group:
                continue

            existing = (
                self.db.query(Membership)
                .filter(
                    Membership.account_id == account.id,
                    Membership.group_id == group.id,
                )
                .first()
            )

            if existing:
                summary.setdefault("memberships_updated", 0)
                summary["memberships_updated"] += 1

            else:
                self.db.add(
                    Membership(
                        account_id=account.id,
                        group_id=group.id,
                    )
                )

                summary.setdefault("memberships_created", 0)
                summary["memberships_created"] += 1                                

        self.db.commit()

        return summary