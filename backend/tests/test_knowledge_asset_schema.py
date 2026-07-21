from datetime import UTC, datetime
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from app.domain import (
    KnowledgeAssetStatus,
    KnowledgeCategory,
)
from app.schemas.knowledge_asset import (
    KnowledgeAssetCreate,
    KnowledgeAssetRead,
)


EXPECTED_CREATE_FIELDS = {
    "title",
    "guidance",
    "category",
    "status",
    "summary",
    "source_system",
    "source_identifier",
    "confidence_score",
}

EXPECTED_READ_FIELDS = {
    "id",
    "organization_id",
    "title",
    "summary",
    "guidance",
    "category",
    "status",
    "version",
    "source_system",
    "source_identifier",
    "confidence_score",
    "created_at",
    "updated_at",
    "created_by",
    "updated_by",
    "is_active",
}

SERVER_CONTROLLED_CREATE_FIELDS = {
    "id",
    "organization_id",
    "version",
    "actor",
    "created_at",
    "updated_at",
    "created_by",
    "updated_by",
    "is_active",
}


def valid_create_payload() -> dict:
    return {
        "title": "Global Administrator elevation review",
        "guidance": (
            "Require analyst review for every material privilege "
            "elevation, including eligible and temporary assignments."
        ),
        "category": KnowledgeCategory.AUTHORIZATION,
        "summary": "Guidance for material authorization changes.",
        "source_system": "USOP",
        "source_identifier": "ADR-019",
        "confidence_score": 100,
    }


def test_knowledge_asset_create_contract_is_exact():
    assert (
        set(KnowledgeAssetCreate.model_fields)
        == EXPECTED_CREATE_FIELDS
    )


def test_knowledge_asset_read_contract_is_exact():
    assert (
        set(KnowledgeAssetRead.model_fields)
        == EXPECTED_READ_FIELDS
    )


@pytest.mark.parametrize(
    "field_name",
    sorted(SERVER_CONTROLLED_CREATE_FIELDS),
)
def test_create_rejects_server_controlled_fields(
    field_name: str,
):
    payload = valid_create_payload()
    payload[field_name] = "caller-controlled-value"

    with pytest.raises(ValidationError):
        KnowledgeAssetCreate.model_validate(payload)


def test_create_rejects_unknown_fields():
    payload = valid_create_payload()
    payload["unexpected_field"] = "not allowed"

    with pytest.raises(ValidationError):
        KnowledgeAssetCreate.model_validate(payload)


def test_create_applies_canonical_defaults():
    schema = KnowledgeAssetCreate.model_validate(
        {
            "title": "Privileged access review",
            "guidance": "Require explicit analyst resolution.",
            "category": KnowledgeCategory.AUTHORIZATION,
        }
    )

    assert schema.status == KnowledgeAssetStatus.DRAFT
    assert schema.confidence_score == 100
    assert schema.summary is None
    assert schema.source_system is None
    assert schema.source_identifier is None


def test_create_accepts_canonical_enum_values():
    schema = KnowledgeAssetCreate.model_validate(
        {
            "title": "Authentication exception review",
            "guidance": "Review exceptions before acceptance.",
            "category": "Authentication",
            "status": "UnderReview",
        }
    )

    assert schema.category == KnowledgeCategory.AUTHENTICATION
    assert schema.status == KnowledgeAssetStatus.UNDER_REVIEW


@pytest.mark.parametrize(
    ("field_name", "invalid_value"),
    [
        ("category", "UnknownCategory"),
        ("status", "UnknownStatus"),
    ],
)
def test_create_rejects_unknown_domain_values(
    field_name: str,
    invalid_value: str,
):
    payload = valid_create_payload()
    payload[field_name] = invalid_value

    with pytest.raises(ValidationError):
        KnowledgeAssetCreate.model_validate(payload)


@pytest.mark.parametrize(
    ("field_name", "invalid_value"),
    [
        ("title", ""),
        ("title", "x" * 256),
        ("guidance", ""),
        ("source_system", "x" * 101),
        ("source_identifier", "x" * 256),
        ("confidence_score", -1),
        ("confidence_score", 101),
    ],
)
def test_create_rejects_invalid_field_constraints(
    field_name: str,
    invalid_value,
):
    payload = valid_create_payload()
    payload[field_name] = invalid_value

    with pytest.raises(ValidationError):
        KnowledgeAssetCreate.model_validate(payload)


def test_read_serializes_from_orm_attributes():
    timestamp = datetime.now(UTC)

    knowledge_asset = SimpleNamespace(
        id="knowledge-asset-001",
        organization_id="organization-001",
        title="Global Administrator elevation review",
        summary="Review all material privilege elevation.",
        guidance="Require an explicit analyst decision.",
        category=KnowledgeCategory.AUTHORIZATION.value,
        status=KnowledgeAssetStatus.ACTIVE.value,
        version=3,
        source_system="MicrosoftEntraID",
        source_identifier="role-assignment-001",
        confidence_score=95,
        created_at=timestamp,
        updated_at=timestamp,
        created_by="analyst@example.com",
        updated_by="analyst@example.com",
        is_active=True,
    )

    schema = KnowledgeAssetRead.model_validate(
        knowledge_asset
    )

    assert schema.id == "knowledge-asset-001"
    assert schema.organization_id == "organization-001"
    assert schema.category == "Authorization"
    assert schema.status == "Active"
    assert schema.version == 3
    assert schema.confidence_score == 95
    assert schema.created_by == "analyst@example.com"
    assert schema.is_active is True


def test_read_rejects_unknown_mapping_fields():
    timestamp = datetime.now(UTC)

    payload = {
        "id": "knowledge-asset-001",
        "organization_id": "organization-001",
        "title": "Privileged access review",
        "summary": None,
        "guidance": "Require analyst review.",
        "category": "Authorization",
        "status": "Draft",
        "version": 1,
        "source_system": None,
        "source_identifier": None,
        "confidence_score": 100,
        "created_at": timestamp,
        "updated_at": timestamp,
        "created_by": None,
        "updated_by": None,
        "is_active": True,
        "unexpected_field": "not allowed",
    }

    with pytest.raises(ValidationError):
        KnowledgeAssetRead.model_validate(payload)
