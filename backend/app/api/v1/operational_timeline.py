from __future__ import annotations

from datetime import datetime

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.timeline import (
    OperationalTimelineEngine,
    OperationalTimelineResult,
    TimelineCategory,
    TimelineCursorError,
    TimelineDuplicateEventError,
    TimelineOrganizationScopeError,
    TimelineQuery,
    TimelineVisibility,
)
from app.timeline.contributors import (
    build_core_timeline_registry,
)


router = APIRouter(
    prefix=(
        "/api/v1/organizations/"
        "{organization_id}/operational-timeline"
    ),
    tags=["Operational Timeline"],
)


@router.get(
    "/",
    response_model=OperationalTimelineResult,
)
def get_operational_timeline(
    organization_id: str,
    identity_id: str | None = None,
    work_item_id: str | None = None,
    decision_id: str | None = None,
    correlation_id: str | None = None,
    categories: list[TimelineCategory] | None = Query(
        default=None,
        alias="category",
    ),
    visibility_levels: (
        list[TimelineVisibility] | None
    ) = Query(
        default=None,
        alias="visibility",
    ),
    start_at: datetime | None = None,
    end_at: datetime | None = None,
    cursor: str | None = None,
    limit: int = Query(
        default=100,
        ge=1,
        le=500,
    ),
    sort_direction: str = Query(
        default="descending",
        pattern="^(ascending|descending)$",
    ),
    db: Session = Depends(get_db),
):
    """
    Return one Organization-scoped operational chronology.

    The controller remains contributor-neutral. Core contributor discovery,
    chronology, filtering, pagination, and diagnostics remain backend-owned.
    """

    try:
        query = TimelineQuery(
            organization_id=organization_id,
            identity_id=identity_id,
            work_item_id=work_item_id,
            decision_id=decision_id,
            correlation_id=correlation_id,
            categories=frozenset(
                categories or ()
            ),
            visibility_levels=frozenset(
                visibility_levels or ()
            ),
            start_at=start_at,
            end_at=end_at,
            cursor=cursor,
            limit=limit,
            sort_direction=sort_direction,
        )

        registry = build_core_timeline_registry(
            db
        )

        return OperationalTimelineEngine(
            registry
        ).build(query)

    except TimelineCursorError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error

    except TimelineOrganizationScopeError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error

    except TimelineDuplicateEventError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error
