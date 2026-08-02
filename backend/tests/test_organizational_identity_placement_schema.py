import pytest
from pydantic import ValidationError

from app.schemas.organizational_identity_placement import (
    OrganizationalIdentityPlacementItem,
    OrganizationalIdentityPlacementRequest,
    PlacementDisposition,
)


def test_placement_item_rejects_organization_override():
    with pytest.raises(ValidationError):
        OrganizationalIdentityPlacementItem.model_validate(
            {
                "identity_id": "identity-001",
                "organization_id": "organization-075",
            }
        )


def test_placement_request_requires_at_least_one_item():
    with pytest.raises(ValidationError):
        OrganizationalIdentityPlacementRequest(
            placements=[]
        )


def test_placement_item_normalizes_text():
    item = OrganizationalIdentityPlacementItem(
        identity_id="  identity-001  ",
        display_name="  John Smith  ",
        status="  Active  ",
    )

    assert item.identity_id == "identity-001"
    assert item.display_name == "John Smith"
    assert item.status == "Active"


def test_disposition_vocabulary_is_stable():
    assert {
        disposition.value
        for disposition in PlacementDisposition
    } == {
        "Ready",
        "Already Placed",
        "Invalid",
        "Created",
    }
