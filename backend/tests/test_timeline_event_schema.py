from datetime import datetime

import pytest
from pydantic import ValidationError

from app.timeline import (
    TimelineCategory,
    TimelineEvent,
    TimelineQuery,
    TimelineSubjectReference,
    TimelineVisibility,
)


def build_event(**overrides):
    payload = {
        "event_id": "example:event-001",
        "occurred_at": datetime(
            2026,
            8,
            4,
            12,
            0,
        ),
        "category": (
            TimelineCategory.OPERATIONAL
        ),
        "visibility": (
            TimelineVisibility.NOTICE
        ),
        "title": "Example event",
        "contributor_name": (
            "example-contributor"
        ),
        "contributor_version": "1.0.0",
        "source_type": "Example",
        "source_id": "source-001",
        "organization_id": (
            "organization-001"
        ),
        "subject_references": (
            TimelineSubjectReference(
                subject_type="Identity",
                subject_id="identity-001",
            ),
        ),
    }
    payload.update(overrides)
    return TimelineEvent(**payload)


def test_event_normalizes_naive_timestamp_to_utc():
    event = build_event()

    assert event.occurred_at.tzinfo is not None
    assert event.occurred_at.utcoffset().total_seconds() == 0


def test_event_rejects_unknown_category():
    with pytest.raises(ValidationError):
        build_event(category="DatabaseRow")


def test_event_rejects_unknown_visibility():
    with pytest.raises(ValidationError):
        build_event(visibility="Severe")


def test_event_rejects_unknown_fields():
    with pytest.raises(ValidationError):
        build_event(unexpected=True)


def test_query_requires_organization_scope():
    with pytest.raises(ValidationError):
        TimelineQuery(organization_id="")


def test_query_rejects_invalid_limit():
    with pytest.raises(ValidationError):
        TimelineQuery(
            organization_id="organization-001",
            limit=501,
        )
