from sqlalchemy.orm import Session

from app.connectors.provider.ProviderIdentityCorrelationRegistry import (
    ProviderIdentityCorrelationRegistry,
    build_default_identity_correlation_registry,
)
from app.repositories.account_repository import AccountRepository
from app.repositories.platform_user_repository import PlatformUserRepository
from app.services.platform_user_identity_correlation_result import (
    PlatformUserIdentityCorrelationDisposition,
    PlatformUserIdentityCorrelationResult,
)


class PlatformUserIdentityCorrelationService:
    """
    Evaluate deterministic PlatformUser-to-Account identity evidence.

    This service never performs a binding.
    """

    def __init__(
        self,
        db: Session,
        *,
        provider_registry: (
            ProviderIdentityCorrelationRegistry | None
        ) = None,
        platform_user_repository: PlatformUserRepository | None = None,
        account_repository: AccountRepository | None = None,
    ):
        self.db = db
        self.provider_registry = (
            provider_registry
            or build_default_identity_correlation_registry()
        )
        self.platform_user_repository = (
            platform_user_repository
            or PlatformUserRepository(db)
        )
        self.account_repository = (
            account_repository
            or AccountRepository(db)
        )

    @staticmethod
    def _required(value: str, field_name: str) -> str:
        normalized = str(value or "").strip()
        if not normalized:
            raise ValueError(f"{field_name} is required.")
        return normalized

    def evaluate(
        self,
        *,
        organization_id: str,
        platform_user_id: str,
    ) -> PlatformUserIdentityCorrelationResult:
        organization_id = self._required(
            organization_id,
            "organization_id",
        )
        platform_user_id = self._required(
            platform_user_id,
            "platform_user_id",
        )

        platform_user = self.platform_user_repository.get_by_id(
            platform_user_id
        )

        if (
            platform_user is None
            or platform_user.organization_id != organization_id
        ):
            return PlatformUserIdentityCorrelationResult(
                disposition=(
                    PlatformUserIdentityCorrelationDisposition.NO_MATCH
                ),
                organization_id=organization_id,
                platform_user_id=platform_user_id,
                message=(
                    "Platform User not found in the active Organization."
                ),
            )

        if platform_user.organizational_identity_id:
            return PlatformUserIdentityCorrelationResult(
                disposition=(
                    PlatformUserIdentityCorrelationDisposition.ALREADY_BOUND
                ),
                organization_id=organization_id,
                platform_user_id=platform_user.id,
                organizational_identity_id=(
                    platform_user.organizational_identity_id
                ),
                message="Platform User is already bound.",
            )

        provider_name = str(
            platform_user.identity_provider or ""
        ).strip().lower()
        tenant_id = str(
            platform_user.external_tenant_id or ""
        ).strip()
        subject_id = str(
            platform_user.external_subject_id or ""
        ).strip()

        if not provider_name or not tenant_id or not subject_id:
            return PlatformUserIdentityCorrelationResult(
                disposition=(
                    PlatformUserIdentityCorrelationDisposition
                    .INSUFFICIENT_EVIDENCE
                ),
                organization_id=organization_id,
                platform_user_id=platform_user.id,
                provider_name=provider_name or None,
                external_tenant_id=tenant_id or None,
                external_subject_id=subject_id or None,
                message=(
                    "Provider, tenant, and subject evidence are required."
                ),
            )

        contract = self.provider_registry.get(provider_name)

        if (
            contract is None
            or not contract.supports_deterministic_subject_match
        ):
            return PlatformUserIdentityCorrelationResult(
                disposition=(
                    PlatformUserIdentityCorrelationDisposition
                    .UNSUPPORTED_PROVIDER
                ),
                organization_id=organization_id,
                platform_user_id=platform_user.id,
                provider_name=provider_name,
                external_tenant_id=tenant_id,
                external_subject_id=subject_id,
                message=(
                    "Provider does not declare deterministic correlation."
                ),
            )

        accounts = (
            self.account_repository.list_by_source_for_organization(
                organization_id=organization_id,
                source_system=contract.account_source_system,
                source_identifier=subject_id,
            )
        )

        if not accounts:
            return PlatformUserIdentityCorrelationResult(
                disposition=(
                    PlatformUserIdentityCorrelationDisposition.NO_MATCH
                ),
                organization_id=organization_id,
                platform_user_id=platform_user.id,
                provider_name=provider_name,
                external_tenant_id=tenant_id,
                external_subject_id=subject_id,
                message="No tenant-scoped Account matched.",
            )

        if len(accounts) > 1:
            return PlatformUserIdentityCorrelationResult(
                disposition=(
                    PlatformUserIdentityCorrelationDisposition.AMBIGUOUS
                ),
                organization_id=organization_id,
                platform_user_id=platform_user.id,
                provider_name=provider_name,
                external_tenant_id=tenant_id,
                external_subject_id=subject_id,
                evidence=(f"candidate_count={len(accounts)}",),
                message=(
                    "Multiple tenant-scoped Accounts matched. "
                    "No binding may occur."
                ),
            )

        account = accounts[0]

        if (
            not account.organizational_identity_id
            or not account.identity_id
        ):
            return PlatformUserIdentityCorrelationResult(
                disposition=(
                    PlatformUserIdentityCorrelationDisposition.CONFLICT
                ),
                organization_id=organization_id,
                platform_user_id=platform_user.id,
                provider_name=provider_name,
                external_tenant_id=tenant_id,
                external_subject_id=subject_id,
                account_id=account.id,
                message=(
                    "Matched Account lacks complete organization ownership."
                ),
            )

        return PlatformUserIdentityCorrelationResult(
            disposition=(
                PlatformUserIdentityCorrelationDisposition
                .DETERMINISTIC_MATCH
            ),
            organization_id=organization_id,
            platform_user_id=platform_user.id,
            provider_name=provider_name,
            external_tenant_id=tenant_id,
            external_subject_id=subject_id,
            account_id=account.id,
            organizational_identity_id=(
                account.organizational_identity_id
            ),
            identity_id=account.identity_id,
            evidence=(
                f"provider={provider_name}",
                f"tenant={tenant_id}",
                f"subject={subject_id}",
                f"account_source_system={contract.account_source_system}",
                f"account_id={account.id}",
            ),
            message=(
                "Exactly one tenant-scoped Account matched "
                "deterministic provider evidence."
            ),
        )
