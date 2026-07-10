from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.account import Account
from app.models.group import Group
from app.models.identity import Identity
from app.models.membership import Membership
from app.models.role import Role
from app.models.role_assignment import RoleAssignment


class ReconciliationEngine:
    """
    Reconcile normalized provider records into the canonical USOP domain.

    Stable provider source identifiers are preferred for matching. Human-
    readable values are used only as controlled fallbacks when a provider
    does not supply a durable identifier.
    """

    def __init__(self, db: Session):
        self.db = db

    def reconcile(self, normalized: dict):
        summary = {
            "identities_created": 0,
            "identities_updated": 0,
            "accounts_created": 0,
            "accounts_updated": 0,
            "accounts_skipped": 0,
            "groups_created": 0,
            "groups_updated": 0,
            "groups_skipped": 0,
            "roles_created": 0,
            "roles_updated": 0,
            "memberships_created": 0,
            "memberships_updated": 0,
            "role_assignments_created": 0,
            "role_assignments_updated": 0,
        }

        self._reconcile_identities(
            normalized.get("identities", []),
            summary,
        )

        self._reconcile_accounts(
            normalized.get("accounts", []),
            summary,
        )

        self._reconcile_groups(
            normalized.get("groups", []),
            summary,
        )

        self._reconcile_roles(
            normalized.get("roles", []),
            summary,
        )

        self._reconcile_memberships(
            normalized.get("memberships", []),
            summary,
        )

        self._reconcile_role_assignments(
            normalized.get("role_assignments", []),
            summary,
        )

        self.db.commit()

        return summary

    def _reconcile_identities(
        self,
        identities: list[dict],
        summary: dict,
    ) -> None:
        for identity in identities:
            source_system = identity.get(
                "source_system"
            )
            source_identifier = identity.get(
                "source_identifier"
            )
            primary_email = identity.get(
                "primary_email"
            )

            existing = None

            if source_system and source_identifier:
                existing = (
                    self.db.query(Identity)
                    .filter(
                        Identity.source_system
                        == source_system,
                        Identity.source_identifier
                        == source_identifier,
                    )
                    .first()
                )

            if existing is None and primary_email:
                existing = (
                    self.db.query(Identity)
                    .filter(
                        func.lower(
                            Identity.primary_email
                        )
                        == primary_email.lower()
                    )
                    .first()
                )

            if existing:
                existing.display_name = identity[
                    "display_name"
                ]
                existing.identity_class = identity.get(
                    "identity_class",
                    existing.identity_class,
                )
                existing.primary_email = primary_email
                existing.status = identity.get(
                    "status",
                    existing.status,
                )
                existing.source_system = source_system
                existing.source_identifier = (
                    source_identifier
                )
                existing.confidence_score = identity.get(
                    "confidence_score",
                    existing.confidence_score,
                )
                existing.is_active = True

                summary["identities_updated"] += 1
                continue

            self.db.add(
                Identity(
                    display_name=identity[
                        "display_name"
                    ],
                    identity_class=identity.get(
                        "identity_class",
                        "Person",
                    ),
                    primary_email=primary_email,
                    status=identity.get(
                        "status",
                        "Active",
                    ),
                    source_system=source_system,
                    source_identifier=(
                        source_identifier
                    ),
                    confidence_score=identity.get(
                        "confidence_score",
                        100,
                    ),
                )
            )

            summary["identities_created"] += 1

        self.db.flush()

    def _reconcile_accounts(
        self,
        accounts: list[dict],
        summary: dict,
    ) -> None:
        for account in accounts:
            source_system = account.get(
                "source_system"
            )
            source_identifier = account.get(
                "source_identifier"
            )
            system_name = account.get(
                "system_name"
            )
            username = account.get(
                "username"
            )

            if not username or not system_name:
                summary["accounts_skipped"] += 1
                continue

            identity = self._resolve_account_identity(
                account
            )

            if identity is None:
                summary["accounts_skipped"] += 1
                continue

            existing = self._find_existing_account(
                source_system=source_system,
                source_identifier=source_identifier,
                system_name=system_name,
                username=username,
            )

            if existing:
                self._update_account(
                    existing=existing,
                    account=account,
                    identity=identity,
                )

                summary["accounts_updated"] += 1
                continue

            self.db.add(
                Account(
                    identity_id=identity.id,
                    username=username,
                    display_name=account.get(
                        "display_name"
                    ),
                    account_type=account.get(
                        "account_type",
                        "User",
                    ),
                    status=account.get(
                        "status",
                        "Active",
                    ),
                    system_name=system_name,
                    source_system=source_system,
                    source_identifier=(
                        source_identifier
                    ),
                    privilege_level=account.get(
                        "privilege_level"
                    ),
                    authentication_method=account.get(
                        "authentication_method"
                    ),
                    authentication_strength=account.get(
                        "authentication_strength"
                    ),
                    authentication_provider=account.get(
                        "authentication_provider"
                    ),
                    mfa_enabled=account.get(
                        "mfa_enabled",
                        False,
                    ),
                    last_seen_at=account.get(
                        "last_seen_at"
                    ),
                    confidence_score=account.get(
                        "confidence_score",
                        100,
                    ),
                )
            )

            summary["accounts_created"] += 1

        self.db.flush()

    def _resolve_account_identity(
        self,
        account: dict,
    ) -> Identity | None:
        identity_source_system = account.get(
            "identity_source_system"
        )
        identity_source_identifier = account.get(
            "identity_source_identifier"
        )

        if (
            not identity_source_system
            or not identity_source_identifier
        ):
            return None

        return (
            self.db.query(Identity)
            .filter(
                Identity.source_system
                == identity_source_system,
                Identity.source_identifier
                == identity_source_identifier,
                Identity.is_active.is_(True),
            )
            .first()
        )

    def _find_existing_account(
        self,
        source_system: str | None,
        source_identifier: str | None,
        system_name: str,
        username: str,
    ) -> Account | None:
        if source_system and source_identifier:
            existing = (
                self.db.query(Account)
                .filter(
                    Account.source_system
                    == source_system,
                    Account.source_identifier
                    == source_identifier,
                )
                .first()
            )

            if existing:
                return existing

        return (
            self.db.query(Account)
            .filter(
                func.lower(Account.username)
                == username.lower(),
                Account.system_name
                == system_name,
            )
            .first()
        )

    @staticmethod
    def _update_account(
        existing: Account,
        account: dict,
        identity: Identity,
    ) -> None:
        existing.identity_id = identity.id
        existing.username = account["username"]
        existing.display_name = account.get(
            "display_name"
        )
        existing.account_type = account.get(
            "account_type",
            existing.account_type,
        )
        existing.status = account.get(
            "status",
            existing.status,
        )
        existing.system_name = account[
            "system_name"
        ]
        existing.source_system = account.get(
            "source_system"
        )
        existing.source_identifier = account.get(
            "source_identifier"
        )
        existing.privilege_level = account.get(
            "privilege_level"
        )
        existing.authentication_method = account.get(
            "authentication_method"
        )
        existing.authentication_strength = account.get(
            "authentication_strength"
        )
        existing.authentication_provider = account.get(
            "authentication_provider"
        )
        existing.mfa_enabled = account.get(
            "mfa_enabled",
            existing.mfa_enabled,
        )
        existing.last_seen_at = account.get(
            "last_seen_at"
        )
        existing.confidence_score = account.get(
            "confidence_score",
            existing.confidence_score,
        )
        existing.is_active = True

    def _reconcile_groups(
        self,
        groups: list[dict],
        summary: dict,
    ) -> None:
        """
        Create or update canonical groups.

        Provider source identity is the primary match. Name and system are used
        only as a fallback for providers that do not expose stable identifiers.
        """

        for group in groups:
            name = group.get("name")
            system_name = group.get(
                "system_name"
            )
            source_system = group.get(
                "source_system"
            )
            source_identifier = group.get(
                "source_identifier"
            )

            if not name or not system_name:
                summary["groups_skipped"] += 1
                continue

            existing = self._find_existing_group(
                source_system=source_system,
                source_identifier=source_identifier,
                system_name=system_name,
                name=name,
            )

            if existing:
                self._update_group(
                    existing=existing,
                    group=group,
                )

                summary["groups_updated"] += 1
                continue

            self.db.add(
                Group(
                    name=name,
                    display_name=group.get(
                        "display_name"
                    ),
                    group_type=group.get(
                        "group_type",
                        "Security",
                    ),
                    status=group.get(
                        "status",
                        "Active",
                    ),
                    system_name=system_name,
                    description=group.get(
                        "description"
                    ),
                    privilege_level=group.get(
                        "privilege_level"
                    ),
                    source_system=source_system,
                    source_identifier=(
                        source_identifier
                    ),
                    confidence_score=group.get(
                        "confidence_score",
                        100,
                    ),
                )
            )

            summary["groups_created"] += 1

        self.db.flush()

    def _find_existing_group(
        self,
        source_system: str | None,
        source_identifier: str | None,
        system_name: str,
        name: str,
    ) -> Group | None:
        if source_system and source_identifier:
            existing = (
                self.db.query(Group)
                .filter(
                    Group.source_system
                    == source_system,
                    Group.source_identifier
                    == source_identifier,
                )
                .first()
            )

            if existing:
                return existing

        return (
            self.db.query(Group)
            .filter(
                func.lower(Group.name)
                == name.lower(),
                Group.system_name
                == system_name,
            )
            .first()
        )

    @staticmethod
    def _update_group(
        existing: Group,
        group: dict,
    ) -> None:
        existing.name = group["name"]
        existing.display_name = group.get(
            "display_name"
        )
        existing.group_type = group.get(
            "group_type",
            existing.group_type,
        )
        existing.status = group.get(
            "status",
            existing.status,
        )
        existing.system_name = group[
            "system_name"
        ]
        existing.description = group.get(
            "description"
        )
        existing.privilege_level = group.get(
            "privilege_level"
        )
        existing.source_system = group.get(
            "source_system"
        )
        existing.source_identifier = group.get(
            "source_identifier"
        )
        existing.confidence_score = group.get(
            "confidence_score",
            existing.confidence_score,
        )
        existing.is_active = True

    def _reconcile_roles(
        self,
        roles: list[dict],
        summary: dict,
    ) -> None:
        for role in roles:
            existing = (
                self.db.query(Role)
                .filter(
                    func.lower(Role.name)
                    == role["name"].lower(),
                    Role.system_name
                    == role["system_name"],
                )
                .first()
            )

            if existing:
                summary["roles_updated"] += 1
                continue

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

    def _reconcile_memberships(
        self,
        memberships: list[dict],
        summary: dict,
    ) -> None:
        for membership in memberships:
            account = (
                self.db.query(Account)
                .filter(
                    func.lower(Account.username)
                    == membership[
                        "username"
                    ].lower()
                )
                .first()
            )

            group = (
                self.db.query(Group)
                .filter(
                    func.lower(Group.name)
                    == membership[
                        "group_name"
                    ].lower()
                )
                .first()
            )

            if not account or not group:
                continue

            existing = (
                self.db.query(Membership)
                .filter(
                    Membership.account_id
                    == account.id,
                    Membership.group_id
                    == group.id,
                )
                .first()
            )

            if existing:
                summary["memberships_updated"] += 1
                continue

            self.db.add(
                Membership(
                    account_id=account.id,
                    group_id=group.id,
                )
            )

            summary["memberships_created"] += 1

    def _reconcile_role_assignments(
        self,
        assignments: list[dict],
        summary: dict,
    ) -> None:
        for assignment in assignments:
            account = (
                self.db.query(Account)
                .filter(
                    func.lower(Account.username)
                    == assignment[
                        "username"
                    ].lower()
                )
                .first()
            )

            role = (
                self.db.query(Role)
                .filter(
                    func.lower(Role.name)
                    == assignment[
                        "role_name"
                    ].lower()
                )
                .first()
            )

            if not account or not role:
                continue

            existing = (
                self.db.query(RoleAssignment)
                .filter(
                    RoleAssignment.subject_type
                    == "Account",
                    RoleAssignment.subject_id
                    == account.id,
                    RoleAssignment.role_id
                    == role.id,
                )
                .first()
            )

            if existing:
                summary[
                    "role_assignments_updated"
                ] += 1
                continue

            self.db.add(
                RoleAssignment(
                    subject_type="Account",
                    subject_id=account.id,
                    role_id=role.id,
                )
            )

            summary[
                "role_assignments_created"
            ] += 1
