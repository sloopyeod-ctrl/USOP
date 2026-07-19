import sys
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))


from app.domain import (
    KnowledgeAssetStatus,
    KnowledgeCategory,
)


def validate_unique(enum_type) -> bool:
    values = [item.value for item in enum_type]
    return len(values) == len(set(values))


def main() -> int:
    print("USOP Organizational Memory Domain Vocabulary")
    print("-------------------------------------------")

    checks = {
        "KnowledgeAssetStatus unique": (
            validate_unique(KnowledgeAssetStatus)
        ),
        "KnowledgeCategory unique": (
            validate_unique(KnowledgeCategory)
        ),
        "Draft lifecycle exists": (
            KnowledgeAssetStatus.DRAFT.value
            == "Draft"
        ),
        "Identity Resolution exists": (
            KnowledgeCategory.IDENTITY_RESOLUTION.value
            == "IdentityResolution"
        ),
        "Lessons Learned exists": (
            KnowledgeCategory.LESSONS_LEARNED.value
            == "LessonsLearned"
        ),
        "Platform Administration exists": (
            KnowledgeCategory.PLATFORM_ADMINISTRATION.value
            == "PlatformAdministration"
        ),
    }

    errors = []

    for name, passed in checks.items():
        print(
            f"{name:.<45}"
            f"{'PASS' if passed else 'FAIL'}"
        )

        if not passed:
            errors.append(name)

    if errors:
        print()
        print("Validation: FAILED")

        for error in errors:
            print(f"- {error}")

        return 1

    print()
    print("Validation: PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
