from app.recommendations.recommendation_engine import (
    RecommendationEngine,
)


def test_recommendations_receive_stable_ids():
    engine = RecommendationEngine()

    findings = [
        {
            "type": "weak_authentication",
            "username": "analyst@example.com",
        },
    ]

    first = engine.generate(findings)
    second = engine.generate(findings)

    assert len(first) == 1
    assert len(second) == 1

    recommendation_id = first[0][
        "recommendation_id"
    ]

    assert recommendation_id.startswith(
        "rec_v1_"
    )
    assert len(recommendation_id) == 31
    assert recommendation_id == second[0][
        "recommendation_id"
    ]


def test_ids_do_not_depend_on_input_order():
    engine = RecommendationEngine()

    first_findings = [
        {
            "type": "weak_authentication",
            "username": "analyst@example.com",
        },
        {
            "type": "dormant_account",
            "username": "service@example.com",
        },
    ]

    second_findings = list(
        reversed(first_findings)
    )

    first = engine.generate(first_findings)
    second = engine.generate(second_findings)

    first_ids = {
        item["title"]: item["recommendation_id"]
        for item in first
    }

    second_ids = {
        item["title"]: item["recommendation_id"]
        for item in second
    }

    assert first_ids == second_ids


def test_semantically_different_targets_get_different_ids():
    engine = RecommendationEngine()

    recommendations = engine.generate(
        [
            {
                "type": "weak_authentication",
                "username": "first@example.com",
            },
            {
                "type": "weak_authentication",
                "username": "second@example.com",
            },
        ]
    )

    recommendation_ids = {
        item["recommendation_id"]
        for item in recommendations
    }

    assert len(recommendations) == 2
    assert len(recommendation_ids) == 2


def test_authorization_recommendation_id_is_stable():
    engine = RecommendationEngine()

    classifications = [
        {
            "role": {
                "role_name": (
                    "Global Administrator"
                ),
            },
            "classification": {
                "risk_level": "Critical",
                "capability": "TenantControl",
                "scope_classification": (
                    "TenantWide"
                ),
                "assignment_classification": (
                    "Eligible"
                ),
                "classification_source": (
                    "CanonicalRoleCatalog"
                ),
            },
        },
    ]

    first = engine.generate(
        [],
        classifications,
    )

    second = engine.generate(
        [],
        classifications,
    )

    assert first[0]["recommendation_id"] == (
        second[0]["recommendation_id"]
    )