from typing import Any

from app.domain.authorization_risk_level import (
    AuthorizationRiskLevel,
)


class AuthorizationClassificationService:
    """
    Classify canonical authorization evidence using explicit metadata and
    trusted provider identifiers.

    The service intentionally returns Unknown when evidence is insufficient.
    It never classifies authorization using loose display-name matching.
    """

    MICROSOFT_ENTRA_SYSTEM_NAMES = {
        "Microsoft Entra ID",
        "Entra ID",
    }

    MICROSOFT_ENTRA_ROLE_POLICY = {
        # Global Administrator
        "62e90394-69f5-4237-9190-012177145e10": {
            "risk_level": AuthorizationRiskLevel.CRITICAL,
            "capability": "TenantAdministrator",
            "reason": (
                "Role can manage all aspects of Microsoft Entra ID "
                "and connected Microsoft services."
            ),
        },
        # User Administrator
        "fe930be7-5e62-47db-91af-98c3a49a38b1": {
            "risk_level": AuthorizationRiskLevel.HIGH,
            "capability": "IdentityAdministrator",
            "reason": (
                "Role can manage users and groups and reset passwords "
                "for limited administrators."
            ),
        },
        # Security Operator
        "5f2222b1-57c3-48ba-8ad5-d4759f1fde6f": {
            "risk_level": AuthorizationRiskLevel.HIGH,
            "capability": "SecurityOperationsAdministrator",
            "reason": (
                "Role can create and manage security events."
            ),
        },
        # Compliance Administrator
        "17315797-102d-40b4-93e0-432062caca18": {
            "risk_level": AuthorizationRiskLevel.HIGH,
            "capability": "ComplianceAdministrator",
            "reason": (
                "Role can manage compliance configuration and reports."
            ),
        },
        # Billing Administrator
        "b0f54661-2d74-4c50-afa3-1ec803f12efe": {
            "risk_level": AuthorizationRiskLevel.MODERATE,
            "capability": "BillingAdministrator",
            "reason": (
                "Role can perform billing administration tasks."
            ),
        },
        # Directory Readers
        "88d8e3e3-8f55-4a1e-953a-9b9898b8876b": {
            "risk_level": AuthorizationRiskLevel.LOW,
            "capability": "DirectoryReader",
            "reason": (
                "Role provides read access to basic directory information."
            ),
        },
        # Attribute Provisioning Reader
        "422218e4-db15-4ef9-bbe0-8afb41546d79": {
            "risk_level": AuthorizationRiskLevel.LOW,
            "capability": "ProvisioningConfigurationReader",
            "reason": (
                "Role provides read-only access to provisioning "
                "configuration."
            ),
        },
    }

    EXPLICIT_PRIVILEGE_POLICY = {
        "critical": AuthorizationRiskLevel.CRITICAL,
        "privileged": AuthorizationRiskLevel.HIGH,
        "admin": AuthorizationRiskLevel.HIGH,
        "administrator": AuthorizationRiskLevel.HIGH,
        "owner": AuthorizationRiskLevel.HIGH,
        "high": AuthorizationRiskLevel.HIGH,
        "moderate": AuthorizationRiskLevel.MODERATE,
        "medium": AuthorizationRiskLevel.MODERATE,
        "readonly": AuthorizationRiskLevel.LOW,
        "read-only": AuthorizationRiskLevel.LOW,
        "low": AuthorizationRiskLevel.LOW,
    }

    def classify(
        self,
        role_evidence: dict[str, Any],
    ) -> dict[str, Any]:
        explicit_result = self._classify_explicit_privilege(
            role_evidence
        )

        if explicit_result:
            result = explicit_result
        else:
            result = self._classify_provider_role(
                role_evidence
            )

        return {
            **result,
            "scope_classification": (
                self._classify_scope(role_evidence)
            ),
            "assignment_classification": (
                self._classify_assignment(role_evidence)
            ),
            "evidence": self._safe_evidence(
                role_evidence
            ),
        }

    def _classify_explicit_privilege(
        self,
        role_evidence: dict[str, Any],
    ) -> dict[str, Any] | None:
        privilege_level = role_evidence.get(
            "privilege_level"
        )

        if not privilege_level:
            return None

        risk_level = self.EXPLICIT_PRIVILEGE_POLICY.get(
            str(privilege_level).strip().lower()
        )

        if risk_level is None:
            return {
                "risk_level": (
                    AuthorizationRiskLevel.UNKNOWN.value
                ),
                "capability": "Unclassified",
                "classification_source": (
                    "CanonicalPrivilegeMetadata"
                ),
                "reasons": [
                    "Canonical privilege metadata is present but "
                    "does not map to a recognized risk level."
                ],
            }

        return {
            "risk_level": risk_level.value,
            "capability": str(privilege_level),
            "classification_source": (
                "CanonicalPrivilegeMetadata"
            ),
            "reasons": [
                "Classification uses explicit canonical privilege "
                "metadata."
            ],
        }

    def _classify_provider_role(
        self,
        role_evidence: dict[str, Any],
    ) -> dict[str, Any]:
        system_name = role_evidence.get(
            "system_name"
        )
        source_identifier = role_evidence.get(
            "role_source_identifier"
        )

        if (
            system_name
            in self.MICROSOFT_ENTRA_SYSTEM_NAMES
            and source_identifier
        ):
            policy = (
                self.MICROSOFT_ENTRA_ROLE_POLICY.get(
                    str(source_identifier)
                )
            )

            if policy:
                return {
                    "risk_level": (
                        policy["risk_level"].value
                    ),
                    "capability": policy["capability"],
                    "classification_source": (
                        "MicrosoftEntraRolePolicy"
                    ),
                    "reasons": [
                        policy["reason"],
                    ],
                }

        return {
            "risk_level": (
                AuthorizationRiskLevel.UNKNOWN.value
            ),
            "capability": "Unclassified",
            "classification_source": (
                "InsufficientEvidence"
            ),
            "reasons": [
                "No explicit canonical privilege metadata or trusted "
                "provider-role policy matched this assignment."
            ],
        }

    @staticmethod
    def _classify_scope(
        role_evidence: dict[str, Any],
    ) -> str:
        directory_scope = role_evidence.get(
            "directory_scope"
        )
        application_scope = role_evidence.get(
            "application_scope"
        )

        if directory_scope == "/":
            return "TenantWide"

        if directory_scope:
            return "DirectoryScoped"

        if application_scope:
            return "ApplicationScoped"

        return "Unknown"

    @staticmethod
    def _classify_assignment(
        role_evidence: dict[str, Any],
    ) -> str:
        assignment_type = role_evidence.get(
            "assignment_type"
        )

        if not assignment_type:
            return "Unknown"

        return str(assignment_type)

    @staticmethod
    def _safe_evidence(
        role_evidence: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "role_name": role_evidence.get(
                "role_name"
            ),
            "role_source_identifier": (
                role_evidence.get(
                    "role_source_identifier"
                )
            ),
            "system_name": role_evidence.get(
                "system_name"
            ),
            "privilege_level": (
                role_evidence.get(
                    "privilege_level"
                )
            ),
            "assignment_type": (
                role_evidence.get(
                    "assignment_type"
                )
            ),
            "directory_scope": (
                role_evidence.get(
                    "directory_scope"
                )
            ),
            "application_scope": (
                role_evidence.get(
                    "application_scope"
                )
            ),
        }
