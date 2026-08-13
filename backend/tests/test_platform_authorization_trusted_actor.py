import pytest

from app.services.platform_authorization_service import (
    AUTHENTICATED_PLATFORM_USER_ACTOR_PREFIX,
    SYSTEM_PLATFORM_AUTHORIZATION_ACTOR,
    PlatformAuthorizationOrganizationBoundaryError,
    PlatformAuthorizationService,
)
from app.services.trusted_external_principal import TrustedExternalPrincipal
from app.services.trusted_platform_caller import TrustedPlatformCaller


ORG_42 = "org-42"
ORG_92 = "org-92"
ACTOR_USER = "platform-user-admin"


def trusted_caller(
    *,
    organization_id=ORG_42,
    platform_user_id=ACTOR_USER,
):
    return TrustedPlatformCaller(
        organization_id=organization_id,
        platform_user_id=platform_user_id,
        principal=TrustedExternalPrincipal(
            identity_provider="microsoft-entra",
            external_tenant_id="tenant-42",
            external_subject_id="subject-admin",
        ),
    )


def test_system_actor_remains_default_for_internal_workflows():
    actor, trust = PlatformAuthorizationService._resolve_actor_context(
        organization_id=ORG_42,
        trusted_caller=None,
    )

    assert actor == SYSTEM_PLATFORM_AUTHORIZATION_ACTOR
    assert trust == "ServerAssignedSystemActor"


def test_authenticated_actor_uses_immutable_platform_user_id():
    actor, trust = PlatformAuthorizationService._resolve_actor_context(
        organization_id=ORG_42,
        trusted_caller=trusted_caller(),
    )

    assert actor == (
        f"{AUTHENTICATED_PLATFORM_USER_ACTOR_PREFIX}{ACTOR_USER}"
    )
    assert trust == "AuthenticatedPlatformCaller"


def test_trusted_actor_cannot_cross_organization_boundary():
    with pytest.raises(
        PlatformAuthorizationOrganizationBoundaryError
    ):
        PlatformAuthorizationService._resolve_actor_context(
            organization_id=ORG_42,
            trusted_caller=trusted_caller(
                organization_id=ORG_92,
            ),
        )
