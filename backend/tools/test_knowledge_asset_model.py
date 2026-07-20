import sys
from pathlib import Path

from sqlalchemy import UniqueConstraint


BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))


from app.database.base import Base
from app.domain import (
    KnowledgeAssetStatus,
    KnowledgeCategory,
)
from app.models.base import BaseSourceModel
from app.models.knowledge_asset import KnowledgeAsset


EXPECTED_COLUMNS = {
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


PROHIBITED_COLUMNS = {
    "identity_id",
    "account_id",
    "decision_id",
    "decision_record_id",
    "governance_policy_id",
    "policy_id",
    "license_id",
    "platform_user_id",
    "role_id",
    "permission_id",
    "attachment_id",
    "evidence_id",
    "review_id",
    "approval_id",
    "owner_id",
}


def unique_constraint_present(
    table,
    expected_columns: set[str],
) -> bool:
    return any(
        {
            column.name
            for column in constraint.columns
        }
        == expected_columns
        for constraint in table.constraints
        if isinstance(
            constraint,
            UniqueConstraint,
        )
    )


def main() -> int:
    print("USOP Canonical Knowledge Asset Model Regression")
    print("-----------------------------------------------")

    errors: list[str] = []

    table = KnowledgeAsset.__table__

    columns = {
        column.name: column
        for column in table.columns
    }

    actual_columns = set(columns)

    missing_columns = EXPECTED_COLUMNS - actual_columns
    unexpected_columns = actual_columns - EXPECTED_COLUMNS

    if missing_columns:
        errors.append(
            "Missing KnowledgeAsset columns: "
            + ", ".join(sorted(missing_columns))
        )

    if unexpected_columns:
        errors.append(
            "Unexpected KnowledgeAsset columns: "
            + ", ".join(sorted(unexpected_columns))
        )

    if not issubclass(
        KnowledgeAsset,
        BaseSourceModel,
    ):
        errors.append(
            "KnowledgeAsset does not inherit BaseSourceModel."
        )

    organization_foreign_keys = {
        foreign_key.target_fullname
        for foreign_key
        in columns["organization_id"].foreign_keys
    }

    if organization_foreign_keys != {
        "organizations.id"
    }:
        errors.append(
            "KnowledgeAsset is not bound to organizations.id."
        )

    if not unique_constraint_present(
        table,
        {
            "organization_id",
            "title",
            "version",
        },
    ):
        errors.append(
            "KnowledgeAsset uniqueness is not scoped by "
            "Organization, title, and version."
        )

    if columns["title"].nullable:
        errors.append(
            "KnowledgeAsset title is nullable."
        )

    if columns["guidance"].nullable:
        errors.append(
            "KnowledgeAsset guidance is nullable."
        )

    if columns["category"].nullable:
        errors.append(
            "KnowledgeAsset category is nullable."
        )

    if (
        columns["status"].default is None
        or columns["status"].default.arg
        != KnowledgeAssetStatus.DRAFT.value
    ):
        errors.append(
            "KnowledgeAsset does not default to Draft."
        )

    if (
        columns["version"].default is None
        or columns["version"].default.arg != 1
    ):
        errors.append(
            "KnowledgeAsset version does not default to 1."
        )

    if (
        columns["confidence_score"].default is None
        or columns["confidence_score"].default.arg != 100
    ):
        errors.append(
            "KnowledgeAsset does not preserve the "
            "BaseSourceModel confidence default."
        )

    embedded_prohibited_columns = (
        PROHIBITED_COLUMNS & actual_columns
    )

    if embedded_prohibited_columns:
        errors.append(
            "KnowledgeAsset embeds prohibited relationships: "
            + ", ".join(
                sorted(embedded_prohibited_columns)
            )
        )

    if table.name != "knowledge_assets":
        errors.append(
            "KnowledgeAsset table name is incorrect."
        )

    if "knowledge_assets" not in Base.metadata.tables:
        errors.append(
            "KnowledgeAsset table is not registered "
            "with shared SQLAlchemy metadata."
        )

    expected_statuses = {
        "Draft",
        "UnderReview",
        "Approved",
        "Active",
        "Deprecated",
        "Retired",
    }

    actual_statuses = {
        item.value
        for item in KnowledgeAssetStatus
    }

    if actual_statuses != expected_statuses:
        errors.append(
            "KnowledgeAssetStatus vocabulary is incorrect."
        )

    if not {
        "IdentityResolution",
        "Authentication",
        "Authorization",
        "LessonsLearned",
        "PlatformAdministration",
    }.issubset(
        {
            item.value
            for item in KnowledgeCategory
        }
    ):
        errors.append(
            "Required KnowledgeCategory vocabulary is missing."
        )

    if errors:
        print()
        print("Validation: FAILED")

        for error in errors:
            print(f"- {error}")

        return 1

    print(f"Table: {table.name}")
    print(f"Column count: {len(actual_columns)}")
    print("Organization binding: organizations.id")
    print(
        "Version uniqueness: "
        "organization_id + title + version"
    )
    print(
        "BaseSourceModel inheritance: True"
    )
    print(
        "Default status: "
        f"{columns['status'].default.arg}"
    )
    print(
        "Default version: "
        f"{columns['version'].default.arg}"
    )
    print(
        "Default confidence score: "
        f"{columns['confidence_score'].default.arg}"
    )
    print("Decision relationship embedded: False")
    print("Identity relationship embedded: False")
    print("Policy relationship embedded: False")
    print("Evidence relationship embedded: False")
    print("Approval workflow embedded: False")
    print("Authorization state embedded: False")
    print("Commercial state embedded: False")

    print()
    print("Validation: PASSED")
    print(
        "KnowledgeAsset is an Organization-scoped, source-aware, "
        "versioned Organizational Memory object with strict separation "
        "from decisions, customer identities, policies, evidence, "
        "workflow, authorization, and commercial state."
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
