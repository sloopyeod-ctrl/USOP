from app.domain import KnowledgeRelationshipType


def test_knowledge_relationship_type_values_are_stable():
    assert (
        KnowledgeRelationshipType.PRIMARY_GUIDANCE.value
        == "PrimaryGuidance"
    )
    assert (
        KnowledgeRelationshipType.SUPPORTING_GUIDANCE.value
        == "SupportingGuidance"
    )
    assert (
        KnowledgeRelationshipType.REFERENCE.value
        == "Reference"
    )
    assert (
        KnowledgeRelationshipType.LESSONS_LEARNED.value
        == "LessonsLearned"
    )
    assert (
        KnowledgeRelationshipType.EXCEPTION.value
        == "Exception"
    )


def test_knowledge_relationship_type_is_string_compatible():
    assert (
        str(KnowledgeRelationshipType.PRIMARY_GUIDANCE)
        == "PrimaryGuidance"
    )


def test_knowledge_relationship_type_contains_only_canonical_values():
    assert {
        relationship_type.value
        for relationship_type in KnowledgeRelationshipType
    } == {
        "PrimaryGuidance",
        "SupportingGuidance",
        "Reference",
        "LessonsLearned",
        "Exception",
    }