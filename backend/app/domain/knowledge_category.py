from enum import StrEnum


class KnowledgeCategory(StrEnum):
    """
    Canonical Organizational Memory categories.

    Categories organize reusable organizational experience rather than
    implementation details.
    """

    IDENTITY_RESOLUTION = "IdentityResolution"
    AUTHENTICATION = "Authentication"
    AUTHORIZATION = "Authorization"
    ACCOUNT_LIFECYCLE = "AccountLifecycle"
    INFRASTRUCTURE = "Infrastructure"
    CLOUD = "Cloud"
    THREAT_INTELLIGENCE = "ThreatIntelligence"
    COMPLIANCE = "Compliance"
    POLICY_EXCEPTION = "PolicyException"
    OPERATIONAL_PROCEDURE = "OperationalProcedure"
    LESSONS_LEARNED = "LessonsLearned"
    PLATFORM_ADMINISTRATION = "PlatformAdministration"
    CONNECTOR_GUIDANCE = "ConnectorGuidance"
