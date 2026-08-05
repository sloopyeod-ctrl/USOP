import pytest

from app.timeline import (
    TimelineCategory,
    TimelineContributorDescriptor,
    TimelineContributorRegistry,
)


class FakeContributor:
    DESCRIPTOR = TimelineContributorDescriptor(
        contributor_name=(
            "example-contributor"
        ),
        display_name="Example Contributor",
        component_version="1.0.0",
        categories=(
            TimelineCategory.OPERATIONAL,
        ),
        priority=20,
    )

    @property
    def descriptor(self):
        return self.DESCRIPTOR

    def contribute(self, query):
        return []


def test_descriptor_rejects_noncanonical_name():
    with pytest.raises(
        ValueError,
        match="canonical lowercase",
    ):
        TimelineContributorDescriptor(
            contributor_name=(
                "Example-Contributor"
            ),
            display_name="Example",
            component_version="1.0.0",
            categories=(
                TimelineCategory.SYSTEM,
            ),
        )


def test_registry_registers_and_creates():
    registry = TimelineContributorRegistry()

    registry.register(
        descriptor=FakeContributor.DESCRIPTOR,
        factory=FakeContributor,
    )

    contributor = registry.create(
        "example-contributor"
    )

    assert contributor is not None
    assert (
        contributor.descriptor
        == FakeContributor.DESCRIPTOR
    )


def test_registry_rejects_duplicate_name():
    registry = TimelineContributorRegistry()

    registry.register(
        descriptor=FakeContributor.DESCRIPTOR,
        factory=FakeContributor,
    )

    with pytest.raises(
        ValueError,
        match="already registered",
    ):
        registry.register(
            descriptor=FakeContributor.DESCRIPTOR,
            factory=FakeContributor,
        )


def test_registry_order_is_deterministic():
    class First(FakeContributor):
        DESCRIPTOR = (
            TimelineContributorDescriptor(
                contributor_name="first",
                display_name="First",
                component_version="1.0.0",
                categories=(
                    TimelineCategory.SYSTEM,
                ),
                priority=10,
            )
        )

    class Second(FakeContributor):
        DESCRIPTOR = (
            TimelineContributorDescriptor(
                contributor_name="second",
                display_name="Second",
                component_version="1.0.0",
                categories=(
                    TimelineCategory.SYSTEM,
                ),
                priority=20,
            )
        )

    registry = TimelineContributorRegistry()
    registry.register(
        descriptor=Second.DESCRIPTOR,
        factory=Second,
    )
    registry.register(
        descriptor=First.DESCRIPTOR,
        factory=First,
    )

    assert registry.contributor_names() == (
        "first",
        "second",
    )
