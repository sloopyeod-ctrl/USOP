from enum import StrEnum


class RoleType(StrEnum):
    """
    Canonical role categories used throughout USOP.

    Database models continue storing string values so provider integrations
    and future domain evolution do not require PostgreSQL enum migrations.

    RoleType provides a controlled application vocabulary while preserving
    compatibility with existing role records.
    """

    ACCESS = "Access"
    DIRECTORY = "Directory"
    CLOUD = "Cloud"
    INFRASTRUCTURE = "Infrastructure"
    APPLICATION = "Application"
    PLATFORM = "Platform"
    DATA = "Data"
    CUSTOM = "Custom"
    