from enum import StrEnum


class SubjectType(StrEnum):
    """
    Canonical subject types used by USOP relationships.

    Database models continue storing string values so provider integrations
    and future domain evolution do not require PostgreSQL enum migrations.
    This enum provides a controlled vocabulary within application code.
    """

    ACCOUNT = "Account"
    SERVICE_PRINCIPAL = "ServicePrincipal"
    DEVICE = "Device"
    GROUP = "Group"
    WORKLOAD = "Workload"
    EXTERNAL_PRINCIPAL = "ExternalPrincipal"