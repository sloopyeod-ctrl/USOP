from __future__ import annotations

from collections.abc import (
    Callable,
    Iterable,
)

from app.timeline.timeline_contributor import (
    TimelineContributor,
)
from app.timeline.timeline_contributor_descriptor import (
    TimelineContributorDescriptor,
)


TimelineContributorFactory = Callable[
    [],
    TimelineContributor,
]


class TimelineContributorRegistry:
    """
    Catalog of timeline-contributor descriptors and factories.

    Runtime health, licensing, customer activation, and query execution remain
    outside the registry.
    """

    def __init__(
        self,
    ) -> None:
        self._descriptors: dict[
            str,
            TimelineContributorDescriptor,
        ] = {}

        self._factories: dict[
            str,
            TimelineContributorFactory,
        ] = {}

    def register(
        self,
        *,
        descriptor: (
            TimelineContributorDescriptor
        ),
        factory: TimelineContributorFactory,
    ) -> None:
        name = descriptor.contributor_name

        if name in self._descriptors:
            raise ValueError(
                "Timeline contributor already "
                f"registered: {name}"
            )

        self._descriptors[name] = descriptor
        self._factories[name] = factory

    def unregister(
        self,
        contributor_name: str,
    ) -> None:
        normalized = self._normalize_name(
            contributor_name
        )

        self._descriptors.pop(
            normalized,
            None,
        )
        self._factories.pop(
            normalized,
            None,
        )

    def get_descriptor(
        self,
        contributor_name: str,
    ) -> (
        TimelineContributorDescriptor
        | None
    ):
        return self._descriptors.get(
            self._normalize_name(
                contributor_name
            )
        )

    def descriptors(
        self,
    ) -> Iterable[
        TimelineContributorDescriptor
    ]:
        return tuple(
            self._descriptors[name]
            for name in self.contributor_names()
        )

    def contributor_names(
        self,
    ) -> tuple[str, ...]:
        return tuple(
            sorted(
                self._descriptors,
                key=lambda name: (
                    self._descriptors[
                        name
                    ].priority,
                    name,
                ),
            )
        )

    def create(
        self,
        contributor_name: str,
    ) -> TimelineContributor | None:
        normalized = self._normalize_name(
            contributor_name
        )

        factory = self._factories.get(
            normalized
        )

        if factory is None:
            return None

        contributor = factory()

        if (
            contributor.descriptor
            .contributor_name
            != normalized
        ):
            raise ValueError(
                "Timeline contributor factory "
                "returned a contributor whose "
                "name does not match its descriptor."
            )

        return contributor

    def create_all(
        self,
    ) -> list[TimelineContributor]:
        contributors: list[
            TimelineContributor
        ] = []

        for name in self.contributor_names():
            contributor = self.create(name)

            if contributor is not None:
                contributors.append(
                    contributor
                )

        return contributors

    @staticmethod
    def _normalize_name(
        value: str,
    ) -> str:
        return str(
            value or ""
        ).strip().lower()
