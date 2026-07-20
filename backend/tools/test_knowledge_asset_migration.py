import ast
import sys
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(BACKEND_ROOT))


MIGRATION_PATH = (
    BACKEND_ROOT
    / "migrations"
    / "versions"
    / "7080e602d9a0_create_knowledge_assets_table.py"
)


EXPECTED_COLUMNS = {
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
    "id",
    "created_at",
    "updated_at",
    "created_by",
    "updated_by",
    "is_active",
}


EXPECTED_INDEXES = {
    "ix_knowledge_assets_category",
    "ix_knowledge_assets_organization_id",
    "ix_knowledge_assets_status",
    "ix_knowledge_assets_title",
}


PROHIBITED_FRAGMENTS = {
    "platform_permissions",
    "uq_platform_permissions_permission_key",
    "postgresql_nulls_not_distinct",
}


PROHIBITED_OPERATIONS = {
    "drop_constraint",
    "create_unique_constraint",
    "alter_column",
    "add_column",
    "drop_column",
}


def string_argument(node: ast.AST | None) -> str | None:
    if (
        isinstance(node, ast.Constant)
        and isinstance(node.value, str)
    ):
        return node.value

    return None


def assignment_value(
    tree: ast.AST,
    variable_name: str,
) -> str | None:
    """
    Read a string assignment from either:

        revision = "..."
        revision: str = "..."
    """

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if (
                    isinstance(target, ast.Name)
                    and target.id == variable_name
                ):
                    return string_argument(node.value)

        elif isinstance(node, ast.AnnAssign):
            if (
                isinstance(node.target, ast.Name)
                and node.target.id == variable_name
            ):
                return string_argument(node.value)

    return None


def operation_name(node: ast.Call) -> str | None:
    function = node.func

    if not isinstance(function, ast.Attribute):
        return None

    if not isinstance(function.value, ast.Name):
        return None

    if function.value.id != "op":
        return None

    return function.attr


def column_names_from_create_table(
    node: ast.Call,
) -> set[str]:
    columns: set[str] = set()

    for argument in node.args[1:]:
        if not isinstance(argument, ast.Call):
            continue

        if not isinstance(argument.func, ast.Attribute):
            continue

        if argument.func.attr != "Column":
            continue

        if not argument.args:
            continue

        column_name = string_argument(argument.args[0])

        if column_name:
            columns.add(column_name)

    return columns


def index_name_from_call(
    node: ast.Call,
) -> str | None:
    if not node.args:
        return None

    index_expression = ast.unparse(node.args[0])

    for expected_index in EXPECTED_INDEXES:
        if expected_index in index_expression:
            return expected_index

    return None


def keyword_string(
    node: ast.Call,
    keyword_name: str,
) -> str | None:
    for keyword in node.keywords:
        if keyword.arg == keyword_name:
            return string_argument(keyword.value)

    return None


def main() -> int:
    print("USOP Knowledge Asset Migration Contract")
    print("---------------------------------------")

    errors: list[str] = []

    if not MIGRATION_PATH.exists():
        print()
        print("Validation: FAILED")
        print(f"- Migration not found: {MIGRATION_PATH}")
        return 1

    source = MIGRATION_PATH.read_text(
        encoding="utf-8-sig",
    )

    tree = ast.parse(source)

    revision = assignment_value(
        tree,
        "revision",
    )

    down_revision = assignment_value(
        tree,
        "down_revision",
    )

    created_table: str | None = None
    columns: set[str] = set()
    created_indexes: set[str] = set()
    dropped_indexes: set[str] = set()
    dropped_tables: set[str] = set()
    unrelated_operations: list[str] = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue

        operation = operation_name(node)

        if operation is None:
            continue

        if operation == "create_table":
            if not node.args:
                unrelated_operations.append(
                    "create_table:missing_table_name"
                )
                continue

            table_name = string_argument(node.args[0])

            if table_name == "knowledge_assets":
                created_table = table_name
                columns.update(
                    column_names_from_create_table(node)
                )
            else:
                unrelated_operations.append(
                    f"create_table:{table_name}"
                )

        elif operation == "create_index":
            table_name = (
                string_argument(node.args[1])
                if len(node.args) >= 2
                else None
            )

            if table_name == "knowledge_assets":
                index_name = index_name_from_call(node)

                if index_name:
                    created_indexes.add(index_name)
            else:
                unrelated_operations.append(
                    f"create_index:{table_name}"
                )

        elif operation == "drop_index":
            table_name = keyword_string(
                node,
                "table_name",
            )

            if table_name == "knowledge_assets":
                index_name = index_name_from_call(node)

                if index_name:
                    dropped_indexes.add(index_name)
            else:
                unrelated_operations.append(
                    f"drop_index:{table_name}"
                )

        elif operation == "drop_table":
            table_name = (
                string_argument(node.args[0])
                if node.args
                else None
            )

            if table_name == "knowledge_assets":
                dropped_tables.add(table_name)
            else:
                unrelated_operations.append(
                    f"drop_table:{table_name}"
                )

        elif operation in PROHIBITED_OPERATIONS:
            unrelated_operations.append(operation)

    if revision != "7080e602d9a0":
        errors.append(
            f"Unexpected revision: {revision}"
        )

    if down_revision != "d84f6b2e9a31":
        errors.append(
            f"Unexpected down revision: {down_revision}"
        )

    if created_table != "knowledge_assets":
        errors.append(
            "Upgrade does not create knowledge_assets."
        )

    missing_columns = EXPECTED_COLUMNS - columns
    unexpected_columns = columns - EXPECTED_COLUMNS

    if missing_columns:
        errors.append(
            "Missing migration columns: "
            + ", ".join(sorted(missing_columns))
        )

    if unexpected_columns:
        errors.append(
            "Unexpected migration columns: "
            + ", ".join(sorted(unexpected_columns))
        )

    if created_indexes != EXPECTED_INDEXES:
        missing_indexes = (
            EXPECTED_INDEXES - created_indexes
        )

        unexpected_indexes = (
            created_indexes - EXPECTED_INDEXES
        )

        if missing_indexes:
            errors.append(
                "Missing upgrade indexes: "
                + ", ".join(sorted(missing_indexes))
            )

        if unexpected_indexes:
            errors.append(
                "Unexpected upgrade indexes: "
                + ", ".join(sorted(unexpected_indexes))
            )

    if dropped_indexes != EXPECTED_INDEXES:
        missing_indexes = (
            EXPECTED_INDEXES - dropped_indexes
        )

        unexpected_indexes = (
            dropped_indexes - EXPECTED_INDEXES
        )

        if missing_indexes:
            errors.append(
                "Missing downgrade indexes: "
                + ", ".join(sorted(missing_indexes))
            )

        if unexpected_indexes:
            errors.append(
                "Unexpected downgrade indexes: "
                + ", ".join(sorted(unexpected_indexes))
            )

    if dropped_tables != {"knowledge_assets"}:
        errors.append(
            "Downgrade does not drop knowledge_assets."
        )

    if (
        "organizations.id" not in source
        or "ForeignKeyConstraint" not in source
    ):
        errors.append(
            "Organization foreign key is missing."
        )

    if (
        "uq_knowledge_assets_" not in source
        or "organization_title_version" not in source
    ):
        errors.append(
            "Organization/title/version uniqueness is missing."
        )

    if unrelated_operations:
        errors.append(
            "Migration contains unrelated schema operations: "
            + ", ".join(
                sorted(unrelated_operations)
            )
        )

    present_prohibited = {
        fragment
        for fragment in PROHIBITED_FRAGMENTS
        if fragment in source
    }

    if present_prohibited:
        errors.append(
            "Migration contains prohibited unrelated content: "
            + ", ".join(
                sorted(present_prohibited)
            )
        )

    if errors:
        print()
        print("Validation: FAILED")

        for error in errors:
            print(f"- {error}")

        return 1

    print(f"Revision: {revision}")
    print(f"Down revision: {down_revision}")
    print(f"Table: {created_table}")
    print(f"Column count: {len(columns)}")
    print("Organization binding: organizations.id")
    print(
        "Version uniqueness: "
        "organization_id + title + version"
    )
    print(f"Upgrade indexes: {len(created_indexes)}")
    print(f"Downgrade indexes: {len(dropped_indexes)}")
    print("Downgrade drops table: True")
    print("Unrelated schema changes: False")

    print()
    print("Validation: PASSED")
    print(
        "The KnowledgeAsset migration is isolated, reversible, "
        "and consistent with the canonical model contract."
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())