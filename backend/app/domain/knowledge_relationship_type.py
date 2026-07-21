from enum import StrEnum


class KnowledgeRelationshipType(StrEnum):
    """
    Canonical classifications describing how Organizational Knowledge
    relates to an accountable security decision.

    These values describe relationship meaning only. They do not duplicate
    KnowledgeAsset content or replace the immutable evidence snapshot
    preserved by the DecisionRecord.
    """

    PRIMARY_GUIDANCE = "PrimaryGuidance"
    SUPPORTING_GUIDANCE = "SupportingGuidance"
    REFERENCE = "Reference"
    LESSONS_LEARNED = "LessonsLearned"
    EXCEPTION = "Exception"