from datetime import UTC, datetime
from unittest.mock import Mock

import pytest
from fastapi import HTTPException, status

from app.api.v1 import operational_timeline as api
from app.timeline import (
    OperationalTimelineResult,
    TimelineCategory,
    TimelineContributorDiagnostic,
    TimelineCursorError,
    TimelineDuplicateEventError,
    TimelineEvent,
    TimelineOrganizationScopeError,
    TimelineVisibility,
)


NOW = datetime(
    2026,
    8,
    5,
    12,
    0,
    tzinfo=UTC,
)


def result() -> OperationalTimelineResult:
    event = TimelineEvent(
        event_id="event-001",
        occurred_at=NOW,
        category=(
            TimelineCategory.OPERATIONAL
        ),
        visibility=(
            TimelineVisibility.NOTICE
        ),
        title="Investigation opened",
        contributor_name="pending-decision",
        contributor_version="1.0.0",
        source_type=(
            "PendingDecisionWorkItem"
        ),
        source_id="work-001",
        organization_id="organization-001",
    )

    diagnostic = (
        TimelineContributorDiagnostic(
            contributor_name=(
                "pending-decision"
            ),
            contributor_version="1.0.0",
            status="Succeeded",
            event_count=1,
        )
    )

    return OperationalTimelineResult(
        organization_id="organization-001",
        events=(event,),
        contributor_diagnostics=(
            diagnostic,
        ),
        generated_at=NOW,
    )


def install_engine(
    monkeypatch,
    *,
    expected_result=None,
    error=None,
):
    registry = object()
    engine = Mock()

    if error is not None:
        engine.build.side_effect = error
    else:
        engine.build.return_value = (
            expected_result or result()
        )

    registry_builder = Mock(
        return_value=registry
    )
    engine_factory = Mock(
        return_value=engine
    )

    monkeypatch.setattr(
        api,
        "build_core_timeline_registry",
        registry_builder,
    )
    monkeypatch.setattr(
        api,
        "OperationalTimelineEngine",
        engine_factory,
    )

    return (
        registry,
        registry_builder,
        engine,
        engine_factory,
    )


def test_get_delegates_complete_query(
    monkeypatch,
):
    (
        registry,
        registry_builder,
        engine,
        engine_factory,
    ) = install_engine(
        monkeypatch,
    )

    db = object()

    response = api.get_operational_timeline(
        organization_id="organization-001",
        identity_id="identity-001",
        work_item_id="work-001",
        decision_id="decision-001",
        correlation_id="correlation-001",
        categories=[
            TimelineCategory.OPERATIONAL,
            TimelineCategory.DECISION,
        ],
        visibility_levels=[
            TimelineVisibility.WARNING,
        ],
        start_at=NOW,
        end_at=NOW,
        cursor=None,
        limit=50,
        sort_direction="ascending",
        db=db,
    )

    registry_builder.assert_called_once_with(
        db
    )
    engine_factory.assert_called_once_with(
        registry
    )

    query = engine.build.call_args.args[0]

    assert query.organization_id == (
        "organization-001"
    )
    assert query.identity_id == "identity-001"
    assert query.work_item_id == "work-001"
    assert query.decision_id == "decision-001"
    assert query.correlation_id == (
        "correlation-001"
    )
    assert query.categories == frozenset(
        {
            TimelineCategory.OPERATIONAL,
            TimelineCategory.DECISION,
        }
    )
    assert query.visibility_levels == frozenset(
        {
            TimelineVisibility.WARNING,
        }
    )
    assert query.start_at == NOW
    assert query.end_at == NOW
    assert query.limit == 50
    assert query.sort_direction == "ascending"
    assert response.organization_id == (
        "organization-001"
    )


@pytest.mark.parametrize(
    ("error", "expected_status"),
    [
        (
            TimelineCursorError(
                "Timeline cursor is invalid."
            ),
            status.HTTP_400_BAD_REQUEST,
        ),
        (
            TimelineOrganizationScopeError(
                "Organization scope conflict."
            ),
            status.HTTP_409_CONFLICT,
        ),
        (
            TimelineDuplicateEventError(
                "Conflicting duplicate event."
            ),
            status.HTTP_409_CONFLICT,
        ),
        (
            ValueError("Invalid query."),
            status.HTTP_400_BAD_REQUEST,
        ),
    ],
)
def test_get_translates_engine_errors(
    monkeypatch,
    error,
    expected_status,
):
    install_engine(
        monkeypatch,
        error=error,
    )

    with pytest.raises(
        HTTPException
    ) as caught:
        api.get_operational_timeline(
            organization_id=(
                "organization-001"
            ),
            categories=None,
            visibility_levels=None,
            limit=100,
            sort_direction="descending",
            db=object(),
        )

    assert (
        caught.value.status_code
        == expected_status
    )
    assert caught.value.detail == str(error)
