from sqlalchemy import func
from sqlalchemy.orm import Session

from app.domain.principal_type import PrincipalType
from app.domain.role_type import RoleType
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

    Normalization preserves provider identity. Reconciliation resolves
    provider references into canonical database identifiers.
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
            "memberships_skipped": 0,
            "role_assignments_created": 0,
            "role_assignments_updated": 0,
            "role_assignments_skipped": 0,
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
        """
        Reconcile canonical authorization roles.

        Stable source-system and source-identifier values are preferred.
        Name and system are retained only as a controlled fallback for legacy
        or manually created role records.
        """

        for role in roles:
            name = role.get("name")
            system_name = role.get("system_name")
            source_system = role.get(
                "source_system"
            )
            source_identifier = role.get(
                "source_identifier"
            )

            if not name or not system_name:
                continue

            existing = self._find_existing_role(
                source_system=source_system,
                source_identifier=source_identifier,
                system_name=system_name,
                name=name,
            )

            if existing:
                self._update_role(
                    existing=existing,
                    role=role,
                )

                summary["roles_updated"] += 1
                continue

            self.db.add(
                Role(
                    name=name,
                    display_name=role.get(
                        "display_name"
                    ),
                    role_type=role.get(
                        "role_type",
                        RoleType.ACCESS.value,
                    ),
                    status=role.get(
                        "status",
                        "Active",
                    ),
                    system_name=system_name,
                    description=role.get(
                        "description"
                    ),
                    privilege_level=role.get(
                        "privilege_level"
                    ),
                    source_system=source_system,
                    source_identifier=source_identifier,
                    confidence_score=role.get(
                        "confidence_score",
                        100,
                    ),
                )
            )

            summary["roles_created"] += 1

        self.db.flush()

    def _find_existing_role(
        self,
        source_system: str | None,
        source_identifier: str | None,
        system_name: str,
        name: str,
    ) -> Role | None:
        if source_system and source_identifier:
            existing = (
                self.db.query(Role)
                .filter(
                    Role.source_system
                    == source_system,
                    Role.source_identifier
                    == source_identifier,
                )
                .first()
            )

            if existing:
                return existing

        return (
            self.db.query(Role)
            .filter(
                func.lower(Role.name)
                == name.lower(),
                Role.system_name
                == system_name,
            )
            .first()
        )

    @staticmethod
    def _update_role(
        existing: Role,
        role: dict,
    ) -> None:
        existing.name = role["name"]
        existing.display_name = role.get(
            "display_name"
        )
        existing.role_type = role.get(
            "role_type",
            existing.role_type,
        )
        existing.status = role.get(
            "status",
            existing.status,
        )
        existing.system_name = role[
            "system_name"
        ]
        existing.description = role.get(
            "description"
        )
        existing.privilege_level = role.get(
            "privilege_level"
        )
        existing.source_system = role.get(
            "source_system"
        )
        existing.source_identifier = role.get(
            "source_identifier"
        )
        existing.confidence_score = role.get(
            "confidence_score",
            existing.confidence_score,
        )
        existing.is_active = True

    def _reconcile_memberships(
        self,
        memberships: list[dict],
        summary: dict,
    ) -> None:
        """
        Reconcile canonical principal-to-group relationships.

        Provider source references are resolved into canonical database IDs.
        Explicit canonical IDs remain supported for internal callers, while
        username and group-name lookups remain controlled legacy fallbacks.
        """

        for membership in memberships:
            subject_type = membership.get(
                "subject_type",
                PrincipalType.ACCOUNT.value,
            )

            subject_id = self._resolve_membership_subject(
                membership=membership,
                subject_type=subject_type,
            )

            group_id = self._resolve_membership_group_id(
                membership
            )

            if not subject_id or not group_id:
                summary["memberships_skipped"] += 1
                continue

            existing = self._find_existing_membership(
                membership=membership,
                subject_type=subject_type,
                subject_id=subject_id,
                group_id=group_id,
            )

            if existing:
                self._update_membership(
                    existing=existing,
                    membership=membership,
                )

                summary["memberships_updated"] += 1
                continue

            self.db.add(
                Membership(
                    subject_type=subject_type,
                    subject_id=subject_id,
                    group_id=group_id,
                    membership_type=membership.get(
                        "membership_type",
                        "Direct",
                    ),
                    status=membership.get(
                        "status",
                        "Active",
                    ),
                    source_system=membership.get(
                        "source_system",
                        membership.get("source"),
                    ),
                    source_identifier=membership.get(
                        "source_identifier"
                    ),
                    first_seen_at=membership.get(
                        "first_seen_at"
                    ),
                    last_seen_at=membership.get(
                        "last_seen_at"
                    ),
                    confidence_score=membership.get(
                        "confidence_score",
                        100,
                    ),
                )
            )

            summary["memberships_created"] += 1

        self.db.flush()

    def _resolve_account_reference(
        self,
        source_system: str | None,
        source_identifier: str | None,
    ) -> Account | None:
        """
        Resolve an active canonical account from a provider reference.
        """

        if not source_system or not source_identifier:
            return None

        return (
            self.db.query(Account)
            .filter(
                Account.source_system == source_system,
                Account.source_identifier
                == source_identifier,
                Account.is_active.is_(True),
            )
            .first()
        )

    def _resolve_group_reference(
        self,
        source_system: str | None,
        source_identifier: str | None,
    ) -> Group | None:
        """
        Resolve an active canonical group from a provider reference.
        """

        if not source_system or not source_identifier:
            return None

        return (
            self.db.query(Group)
            .filter(
                Group.source_system == source_system,
                Group.source_identifier
                == source_identifier,
                Group.is_active.is_(True),
            )
            .first()
        )

    def _resolve_role_reference(
        self,
        source_system: str | None,
        source_identifier: str | None,
    ) -> Role | None:
        """
        Resolve an active canonical role from a provider reference.

        Role-assignment persistence will consume this helper in the next
        focused implementation milestone.
        """

        if not source_system or not source_identifier:
            return None

        return (
            self.db.query(Role)
            .filter(
                Role.source_system == source_system,
                Role.source_identifier
                == source_identifier,
                Role.is_active.is_(True),
            )
            .first()
        )

    def _resolve_membership_subject(
        self,
        membership: dict,
        subject_type: str,
    ) -> str | None:
        """
        Resolve the canonical subject for a membership relationship.

        Explicit canonical IDs are accepted for internal callers. Provider
        references are preferred for synchronized records, with username
        lookup retained only as a controlled legacy fallback.
        """

        explicit_subject_id = membership.get(
            "subject_id"
        )

        if explicit_subject_id:
            return explicit_subject_id

        if subject_type == PrincipalType.ACCOUNT.value:
            account = self._resolve_account_reference(
                source_system=membership.get(
                    "subject_source_system"
                ),
                source_identifier=membership.get(
                    "subject_source_identifier"
                ),
            )

            if account:
                return account.id

            account = self._resolve_membership_account_by_username(
                membership
            )

            if account:
                return account.id

        return None

    def _resolve_membership_group_id(
        self,
        membership: dict,
    ) -> str | None:
        """
        Resolve the canonical group target for a membership relationship.
        """

        explicit_group_id = membership.get(
            "group_id"
        )

        if explicit_group_id:
            return explicit_group_id

        group = self._resolve_group_reference(
            source_system=membership.get(
                "group_source_system"
            ),
            source_identifier=membership.get(
                "group_source_identifier"
            ),
        )

        if group:
            return group.id

        group = self._resolve_membership_group_by_name(
            membership
        )

        if group:
            return group.id

        return None

    def _resolve_membership_account_by_username(
        self,
        membership: dict,
    ) -> Account | None:
        username = membership.get("username")

        if not username:
            return None

        return (
            self.db.query(Account)
            .filter(
                func.lower(Account.username)
                == username.lower(),
                Account.is_active.is_(True),
            )
            .first()
        )

    def _resolve_membership_group_by_name(
        self,
        membership: dict,
    ) -> Group | None:
        group_name = membership.get("group_name")

        if not group_name:
            return None

        return (
            self.db.query(Group)
            .filter(
                func.lower(Group.name)
                == group_name.lower(),
                Group.is_active.is_(True),
            )
            .first()
        )

    def _find_existing_membership(
        self,
        membership: dict,
        subject_type: str,
        subject_id: str,
        group_id: str,
    ) -> Membership | None:
        source_system = membership.get(
            "source_system"
        )
        source_identifier = membership.get(
            "source_identifier"
        )

        if source_system and source_identifier:
            existing = (
                self.db.query(Membership)
                .filter(
                    Membership.source_system
                    == source_system,
                    Membership.source_identifier
                    == source_identifier,
                )
                .first()
            )

            if existing:
                return existing

        return (
            self.db.query(Membership)
            .filter(
                Membership.subject_type
                == subject_type,
                Membership.subject_id
                == subject_id,
                Membership.group_id
                == group_id,
            )
            .first()
        )

    @staticmethod
    def _update_membership(
        existing: Membership,
        membership: dict,
    ) -> None:
        existing.membership_type = membership.get(
            "membership_type",
            existing.membership_type,
        )
        existing.status = membership.get(
            "status",
            existing.status,
        )
        existing.source_system = membership.get(
            "source_system",
            membership.get(
                "source",
                existing.source_system,
            ),
        )
        existing.source_identifier = membership.get(
            "source_identifier",
            existing.source_identifier,
        )
        existing.first_seen_at = membership.get(
            "first_seen_at",
            existing.first_seen_at,
        )
        existing.last_seen_at = membership.get(
            "last_seen_at",
            existing.last_seen_at,
        )
        existing.confidence_score = membership.get(
            "confidence_score",
            existing.confidence_score,
        )
        existing.is_active = True

    def _reconcile_role_assignments(
        self,
        assignments: list[dict],
        summary: dict,
    ) -> None:
        """
        Reconcile canonical principal-to-role relationships.

        Stable provider references are resolved into canonical IDs. Explicit
        IDs remain supported for internal callers, while username and role
        name lookups remain controlled compatibility fallbacks.

        Scope is part of relationship identity because one principal may hold
        the same role at multiple directory or application scopes.
        """

        for assignment in assignments:
            subject_type = assignment.get(
                "subject_type",
                PrincipalType.ACCOUNT.value,
            )

            subject_id = self._resolve_role_assignment_subject(
                assignment=assignment,
                subject_type=subject_type,
            )
            role_id = self._resolve_role_assignment_role_id(
                assignment
            )

            if not subject_id or not role_id:
                summary["role_assignments_skipped"] += 1
                continue

            existing = self._find_existing_role_assignment(
                assignment=assignment,
                subject_type=subject_type,
                subject_id=subject_id,
                role_id=role_id,
            )

            if existing:
                self._update_role_assignment(
                    existing=existing,
                    assignment=assignment,
                )

                summary["role_assignments_updated"] += 1
                continue

            self.db.add(
                RoleAssignment(
                    subject_type=subject_type,
                    subject_id=subject_id,
                    role_id=role_id,
                    assignment_type=assignment.get(
                        "assignment_type",
                        "Direct",
                    ),
                    status=assignment.get(
                        "status",
                        "Active",
                    ),
                    directory_scope=assignment.get(
                        "directory_scope"
                    ),
                    application_scope=assignment.get(
                        "application_scope"
                    ),
                    source_system=assignment.get(
                        "source_system",
                        assignment.get("source"),
                    ),
                    source_identifier=assignment.get(
                        "source_identifier"
                    ),
                    first_seen_at=assignment.get(
                        "first_seen_at"
                    ),
                    last_seen_at=assignment.get(
                        "last_seen_at"
                    ),
                    confidence_score=assignment.get(
                        "confidence_score",
                        100,
                    ),
                )
            )

            summary["role_assignments_created"] += 1

        self.db.flush()

    def _resolve_role_assignment_subject(
        self,
        assignment: dict,
        subject_type: str,
    ) -> str | None:
        """
        Resolve the canonical principal for a role assignment.
        """

        explicit_subject_id = assignment.get(
            "subject_id"
        )

        if explicit_subject_id:
            return explicit_subject_id

        if subject_type == PrincipalType.ACCOUNT.value:
            account = self._resolve_account_reference(
                source_system=assignment.get(
                    "subject_source_system"
                ),
                source_identifier=assignment.get(
                    "subject_source_identifier"
                ),
            )

            if account:
                return account.id

            username = assignment.get("username")

            if username:
                account = (
                    self.db.query(Account)
                    .filter(
                        func.lower(Account.username)
                        == username.lower(),
                        Account.is_active.is_(True),
                    )
                    .first()
                )

                if account:
                    return account.id

        return None

    def _resolve_role_assignment_role_id(
        self,
        assignment: dict,
    ) -> str | None:
        """
        Resolve the canonical role target for a role assignment.
        """

        explicit_role_id = assignment.get(
            "role_id"
        )

        if explicit_role_id:
            return explicit_role_id

        role = self._resolve_role_reference(
            source_system=assignment.get(
                "role_source_system"
            ),
            source_identifier=assignment.get(
                "role_source_identifier"
            ),
        )

        if role:
            return role.id

        role_name = assignment.get("role_name")

        if role_name:
            role = (
                self.db.query(Role)
                .filter(
                    func.lower(Role.name)
                    == role_name.lower(),
                    Role.is_active.is_(True),
                )
                .first()
            )

            if role:
                return role.id

        return None

    def _find_existing_role_assignment(
        self,
        assignment: dict,
        subject_type: str,
        subject_id: str,
        role_id: str,
    ) -> RoleAssignment | None:
        """
        Find an existing role assignment by provider identity first.
        """

        source_system = assignment.get(
            "source_system"
        )
        source_identifier = assignment.get(
            "source_identifier"
        )

        if source_system and source_identifier:
            existing = (
                self.db.query(RoleAssignment)
                .filter(
                    RoleAssignment.source_system
                    == source_system,
                    RoleAssignment.source_identifier
                    == source_identifier,
                )
                .first()
            )

            if existing:
                return existing

        return (
            self.db.query(RoleAssignment)
            .filter(
                RoleAssignment.subject_type
                == subject_type,
                RoleAssignment.subject_id
                == subject_id,
                RoleAssignment.role_id
                == role_id,
                RoleAssignment.directory_scope
                == assignment.get("directory_scope"),
                RoleAssignment.application_scope
                == assignment.get("application_scope"),
            )
            .first()
        )

    @staticmethod
    def _update_role_assignment(
        existing: RoleAssignment,
        assignment: dict,
    ) -> None:
        """
        Refresh a canonical role assignment from normalized provider data.
        """

        existing.assignment_type = assignment.get(
            "assignment_type",
            existing.assignment_type,
        )
        existing.status = assignment.get(
            "status",
            existing.status,
        )
        existing.directory_scope = assignment.get(
            "directory_scope"
        )
        existing.application_scope = assignment.get(
            "application_scope"
        )
        existing.source_system = assignment.get(
            "source_system",
            assignment.get(
                "source",
                existing.source_system,
            ),
        )
        existing.source_identifier = assignment.get(
            "source_identifier",
            existing.source_identifier,
        )
        existing.first_seen_at = assignment.get(
            "first_seen_at",
            existing.first_seen_at,
        )
        existing.last_seen_at = assignment.get(
            "last_seen_at",
            existing.last_seen_at,
        )
        existing.confidence_score = assignment.get(
            "confidence_score",
            existing.confidence_score,
        )
        existing.is_active = True