from __future__ import annotations

import base64
import json
from datetime import UTC, datetime
from typing import Any

from app.timeline.operational_timeline_result import (
    OperationalTimelineResult,
    TimelineContributorDiagnostic,
)
from app.timeline.timeline_contributor_registry import (
    TimelineContributorRegistry,
)
from app.timeline.timeline_event import (
    TimelineEvent,
)
from app.timeline.timeline_query import (
    TimelineQuery,
)


class OperationalTimelineError(Exception):
    """Base error for timeline assembly."""


class TimelineOrganizationScopeError(
    OperationalTimelineError
):
    pass


class TimelineDuplicateEventError(
    OperationalTimelineError
):
    pass


class TimelineCursorError(
    OperationalTimelineError
):
    pass


class OperationalTimelineEngine:
    """
    Assemble canonical operational chronology from registered contributors.

    Contributors produce history. The engine produces chronology.
    """

    def __init__(
        self,
        registry: (
            TimelineContributorRegistry
        ),
    ):
        self.registry = registry

    def build(
        self,
        query: TimelineQuery,
    ) -> OperationalTimelineResult:
        events_by_id: dict[
            str,
            TimelineEvent,
        ] = {}

        diagnostics: list[
            TimelineContributorDiagnostic
        ] = []

        warnings: list[str] = []
        is_partial = False

        for contributor in (
            self.registry.create_all()
        ):
            descriptor = (
                contributor.descriptor
            )

            try:
                contributed = (
                    contributor.contribute(
                        query
                    )
                )

                accepted_count = 0

                for event in contributed:
                    self._validate_scope(
                        query=query,
                        event=event,
                    )

                    if not self._matches_query(
                        query=query,
                        event=event,
                    ):
                        continue

                    existing = events_by_id.get(
                        event.event_id
                    )

                    if existing is not None:
                        if (
                            existing.canonical_payload()
                            == event.canonical_payload()
                        ):
                            warnings.append(
                                "Identical duplicate event "
                                f"deduplicated: {event.event_id}"
                            )
                            continue

                        raise TimelineDuplicateEventError(
                            "Conflicting duplicate timeline "
                            f"event: {event.event_id}"
                        )

                    events_by_id[
                        event.event_id
                    ] = event
                    accepted_count += 1

                diagnostics.append(
                    TimelineContributorDiagnostic(
                        contributor_name=(
                            descriptor
                            .contributor_name
                        ),
                        contributor_version=(
                            descriptor
                            .component_version
                        ),
                        status="Succeeded",
                        event_count=accepted_count,
                    )
                )

            except (
                TimelineOrganizationScopeError,
                TimelineDuplicateEventError,
            ):
                raise

            except Exception:
                is_partial = True

                diagnostics.append(
                    TimelineContributorDiagnostic(
                        contributor_name=(
                            descriptor
                            .contributor_name
                        ),
                        contributor_version=(
                            descriptor
                            .component_version
                        ),
                        status="Failed",
                        event_count=0,
                        message=(
                            "Contributor failed while "
                            "assembling operational history."
                        ),
                    )
                )

        ordered = sorted(
            events_by_id.values(),
            key=lambda event: (
                event.occurred_at,
                event.event_id,
            ),
            reverse=(
                query.sort_direction
                == "descending"
            ),
        )

        ordered = self._apply_cursor(
            events=ordered,
            query=query,
        )

        page = ordered[
            : query.limit
        ]

        next_cursor = None

        if len(ordered) > query.limit:
            next_cursor = self._encode_cursor(
                page[-1]
            )

        return OperationalTimelineResult(
            organization_id=(
                query.organization_id
            ),
            events=tuple(page),
            contributor_diagnostics=tuple(
                diagnostics
            ),
            warnings=tuple(warnings),
            is_partial=is_partial,
            next_cursor=next_cursor,
            generated_at=datetime.now(UTC),
            schema_version=1,
        )

    @staticmethod
    def _validate_scope(
        *,
        query: TimelineQuery,
        event: TimelineEvent,
    ) -> None:
        if (
            event.organization_id
            != query.organization_id
        ):
            raise TimelineOrganizationScopeError(
                "Timeline contributor returned "
                "an event outside the requested "
                "Organization scope."
            )

    @staticmethod
    def _matches_query(
        *,
        query: TimelineQuery,
        event: TimelineEvent,
    ) -> bool:
        if (
            query.categories
            and event.category
            not in query.categories
        ):
            return False

        if (
            query.visibility_levels
            and event.visibility
            not in query.visibility_levels
        ):
            return False

        if (
            query.start_at is not None
            and event.occurred_at
            < query.start_at
        ):
            return False

        if (
            query.end_at is not None
            and event.occurred_at
            > query.end_at
        ):
            return False

        if (
            query.correlation_id is not None
            and event.correlation_id
            != query.correlation_id
        ):
            return False

        requested_subjects = {
            (
                reference.subject_type,
                reference.subject_id,
            )
            for reference
            in query.subject_references
        }

        event_subjects = {
            (
                reference.subject_type,
                reference.subject_id,
            )
            for reference
            in event.subject_references
        }

        if (
            requested_subjects
            and not requested_subjects
            .issubset(event_subjects)
        ):
            return False

        selectors = (
            ("Identity", query.identity_id),
            (
                "PendingDecisionWorkItem",
                query.work_item_id,
            ),
            (
                "DecisionRecord",
                query.decision_id,
            ),
        )

        for subject_type, subject_id in selectors:
            if subject_id is None:
                continue

            if (
                subject_type,
                subject_id,
            ) not in event_subjects:
                return False

        return True

    def _apply_cursor(
        self,
        *,
        events: list[TimelineEvent],
        query: TimelineQuery,
    ) -> list[TimelineEvent]:
        if query.cursor is None:
            return events

        occurred_at, event_id = (
            self._decode_cursor(
                query.cursor
            )
        )

        cursor_key = (
            occurred_at,
            event_id,
        )

        if (
            query.sort_direction
            == "descending"
        ):
            return [
                event
                for event in events
                if (
                    event.occurred_at,
                    event.event_id,
                ) < cursor_key
            ]

        return [
            event
            for event in events
            if (
                event.occurred_at,
                event.event_id,
            ) > cursor_key
        ]

    @staticmethod
    def _encode_cursor(
        event: TimelineEvent,
    ) -> str:
        payload = {
            "occurred_at": (
                event.occurred_at.isoformat()
            ),
            "event_id": event.event_id,
            "cursor_version": 1,
        }

        serialized = json.dumps(
            payload,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")

        return (
            base64.urlsafe_b64encode(
                serialized
            )
            .decode("ascii")
            .rstrip("=")
        )

    @staticmethod
    def _decode_cursor(
        cursor: str,
    ) -> tuple[datetime, str]:
        try:
            padding = "=" * (
                (-len(cursor)) % 4
            )

            payload: dict[str, Any] = (
                json.loads(
                    base64.urlsafe_b64decode(
                        cursor + padding
                    ).decode("utf-8")
                )
            )

            if (
                payload.get(
                    "cursor_version"
                )
                != 1
            ):
                raise ValueError(
                    "Unsupported cursor version."
                )

            occurred_at = (
                datetime.fromisoformat(
                    payload["occurred_at"]
                )
            )

            if occurred_at.tzinfo is None:
                occurred_at = (
                    occurred_at.replace(
                        tzinfo=UTC
                    )
                )
            else:
                occurred_at = (
                    occurred_at.astimezone(
                        UTC
                    )
                )

            event_id = str(
                payload["event_id"]
            ).strip()

            if not event_id:
                raise ValueError(
                    "Cursor event_id is empty."
                )

            return (
                occurred_at,
                event_id,
            )

        except Exception as error:
            raise TimelineCursorError(
                "Timeline cursor is invalid."
            ) from error
