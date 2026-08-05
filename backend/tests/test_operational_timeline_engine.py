from datetime import UTC, datetime, timedelta

import pytest

from app.timeline import (
    OperationalTimelineEngine,
    TimelineCategory,
    TimelineContributorDescriptor,
    TimelineContributorRegistry,
    TimelineDuplicateEventError,
    TimelineEvent,
    TimelineOrganizationScopeError,
    TimelineQuery,
    TimelineSubjectReference,
    TimelineVisibility,
)


BASE_TIME = datetime(
    2026,
    8,
    4,
    12,
    0,
    tzinfo=UTC,
)


def event(
    event_id,
    *,
    occurred_at=BASE_TIME,
    organization_id="organization-001",
    title=None,
):
    return TimelineEvent(
        event_id=event_id,
        occurred_at=occurred_at,
        category=(
            TimelineCategory.OPERATIONAL
        ),
        visibility=(
            TimelineVisibility.NOTICE
        ),
        title=title or event_id,
        contributor_name="example",
        contributor_version="1.0.0",
        source_type="Example",
        source_id=event_id,
        organization_id=organization_id,
        subject_references=(
            TimelineSubjectReference(
                subject_type="Identity",
                subject_id="identity-001",
            ),
        ),
        metadata={"opaque": True},
    )


def contributor_class(
    name,
    events,
    *,
    priority=100,
    failure=None,
):
    descriptor = (
        TimelineContributorDescriptor(
            contributor_name=name,
            display_name=name,
            component_version="1.0.0",
            categories=(
                TimelineCategory.OPERATIONAL,
            ),
            priority=priority,
        )
    )

    class Contributor:
        @property
        def descriptor(self):
            return self.DESCRIPTOR

        def contribute(self, query):
            if failure is not None:
                raise failure

            return list(events)

    Contributor.DESCRIPTOR = descriptor

    return Contributor


def build_engine(*contributors):
    registry = TimelineContributorRegistry()

    for contributor in contributors:
        registry.register(
            descriptor=contributor.DESCRIPTOR,
            factory=contributor,
        )

    return OperationalTimelineEngine(
        registry
    )


def query(**overrides):
    values = {
        "organization_id": (
            "organization-001"
        ),
    }
    values.update(overrides)
    return TimelineQuery(**values)


def test_empty_registry_returns_empty_result():
    result = build_engine().build(
        query()
    )

    assert result.events == ()
    assert result.is_partial is False
    assert (
        result.contributor_diagnostics
        == ()
    )


def test_multiple_contributors_merge_and_sort():
    earlier = event(
        "event:earlier",
        occurred_at=(
            BASE_TIME - timedelta(minutes=1)
        ),
    )
    later = event(
        "event:later",
        occurred_at=BASE_TIME,
    )

    First = contributor_class(
        "first",
        [earlier],
    )
    Second = contributor_class(
        "second",
        [later],
    )

    result = build_engine(
        First,
        Second,
    ).build(query())

    assert [
        item.event_id
        for item in result.events
    ] == [
        "event:later",
        "event:earlier",
    ]


def test_equal_timestamps_use_event_id():
    Alpha = contributor_class(
        "alpha",
        [
            event("event:a"),
            event("event:b"),
        ],
    )

    result = build_engine(
        Alpha
    ).build(query())

    assert [
        item.event_id
        for item in result.events
    ] == [
        "event:b",
        "event:a",
    ]


def test_contributor_failure_is_isolated():
    Good = contributor_class(
        "good",
        [event("event:good")],
    )
    Bad = contributor_class(
        "bad",
        [],
        failure=RuntimeError("boom"),
    )

    result = build_engine(
        Good,
        Bad,
    ).build(query())

    assert [
        item.event_id
        for item in result.events
    ] == ["event:good"]
    assert result.is_partial is True
    assert {
        diagnostic.status
        for diagnostic
        in result.contributor_diagnostics
    } == {
        "Succeeded",
        "Failed",
    }


def test_cross_organization_event_is_rejected():
    Bad = contributor_class(
        "bad",
        [
            event(
                "event:bad",
                organization_id=(
                    "organization-002"
                ),
            )
        ],
    )

    with pytest.raises(
        TimelineOrganizationScopeError
    ):
        build_engine(Bad).build(
            query()
        )


def test_identical_duplicate_is_deduplicated():
    duplicate = event("event:duplicate")

    First = contributor_class(
        "first",
        [duplicate],
    )
    Second = contributor_class(
        "second",
        [duplicate],
    )

    result = build_engine(
        First,
        Second,
    ).build(query())

    assert len(result.events) == 1
    assert len(result.warnings) == 1


def test_conflicting_duplicate_is_rejected():
    First = contributor_class(
        "first",
        [
            event(
                "event:duplicate",
                title="First",
            )
        ],
    )
    Second = contributor_class(
        "second",
        [
            event(
                "event:duplicate",
                title="Second",
            )
        ],
    )

    with pytest.raises(
        TimelineDuplicateEventError
    ):
        build_engine(
            First,
            Second,
        ).build(query())


def test_limit_and_cursor_are_stable():
    Contributor = contributor_class(
        "example",
        [
            event(
                f"event:{index}",
                occurred_at=(
                    BASE_TIME
                    + timedelta(minutes=index)
                ),
            )
            for index in range(3)
        ],
    )

    engine = build_engine(
        Contributor
    )

    first = engine.build(
        query(limit=2)
    )

    assert len(first.events) == 2
    assert first.next_cursor is not None

    second = engine.build(
        query(
            limit=2,
            cursor=first.next_cursor,
        )
    )

    assert [
        item.event_id
        for item in second.events
    ] == ["event:0"]


def test_identity_selector_filters_subjects():
    Contributor = contributor_class(
        "example",
        [event("event:identity")],
    )

    matching = build_engine(
        Contributor
    ).build(
        query(
            identity_id="identity-001"
        )
    )

    missing = build_engine(
        Contributor
    ).build(
        query(
            identity_id="identity-999"
        )
    )

    assert len(matching.events) == 1
    assert missing.events == ()
