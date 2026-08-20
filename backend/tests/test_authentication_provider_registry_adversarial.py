import inspect

import pytest

from app.security.auth.AuthenticationAdapter import (
    AuthenticationAdapter,
)
from app.security.auth.AuthenticationProviderRegistry import (
    AuthenticationProviderRegistry,
)
from app.services.trusted_external_principal import (
    TrustedExternalPrincipal,
)


FORBIDDEN_EXECUTABLE_POLICY_TOKENS = (
    "PlatformRuntimeAuthorizationService",
    "PlatformUserRepository",
    "LicenseRepository",
    "grant_permission",
    "assign_role",
    ".commit(",
    ".rollback(",
)


class GoodAdapter(AuthenticationAdapter):
    @property
    def provider_name(self) -> str:
        return "good-provider"

    def authenticate(
        self,
        credential: str,
    ) -> TrustedExternalPrincipal:
        if credential != "valid":
            raise ValueError("invalid credential")

        return TrustedExternalPrincipal(
            identity_provider=self.provider_name,
            external_tenant_id="tenant-1",
            external_subject_id="subject-1",
        )


class UppercaseNameAdapter(AuthenticationAdapter):
    @property
    def provider_name(self) -> str:
        return "GOOD-PROVIDER"

    def authenticate(
        self,
        credential: str,
    ) -> TrustedExternalPrincipal:
        raise NotImplementedError


class InvalidNameAdapter(AuthenticationAdapter):
    @property
    def provider_name(self) -> str:
        return "bad_provider"

    def authenticate(
        self,
        credential: str,
    ) -> TrustedExternalPrincipal:
        raise NotImplementedError


def _source(obj) -> str:
    return inspect.getsource(obj)


def test_gate_registry_owns_no_authorization_policy():
    source = _source(AuthenticationProviderRegistry)

    for token in FORBIDDEN_EXECUTABLE_POLICY_TOKENS:
        assert token not in source, (
            "AuthenticationProviderRegistry must not own "
            f"authorization/lifecycle policy primitive: {token}"
        )


def test_gate_adapter_contract_owns_no_authorization_policy():
    source = _source(AuthenticationAdapter)

    for token in FORBIDDEN_EXECUTABLE_POLICY_TOKENS:
        assert token not in source, (
            "AuthenticationAdapter must not own "
            f"authorization/lifecycle policy primitive: {token}"
        )


def test_gate_unknown_provider_returns_none_without_fallback():
    registry = AuthenticationProviderRegistry()

    assert registry.create("unknown-provider") is None
    assert registry.provider_names() == ()


def test_gate_duplicate_registration_fails_closed():
    registry = AuthenticationProviderRegistry()

    registry.register(
        "good-provider",
        GoodAdapter,
    )

    with pytest.raises(ValueError, match="already registered"):
        registry.register(
            "GOOD-PROVIDER",
            GoodAdapter,
        )

    assert registry.provider_names() == (
        "good-provider",
    )


def test_gate_invalid_provider_name_cannot_be_registered():
    registry = AuthenticationProviderRegistry()

    with pytest.raises(ValueError):
        registry.register(
            "bad_provider",
            InvalidNameAdapter,
        )

    assert registry.provider_names() == ()


def test_gate_factory_cannot_return_arbitrary_object():
    registry = AuthenticationProviderRegistry()

    registry.register(
        "good-provider",
        lambda: object(),
    )

    with pytest.raises(TypeError, match="does not implement"):
        registry.create("good-provider")


def test_gate_factory_name_mismatch_is_rejected():
    registry = AuthenticationProviderRegistry()

    registry.register(
        "good-provider",
        InvalidNameAdapter,
    )

    with pytest.raises(ValueError):
        registry.create("good-provider")


def test_gate_adapter_name_is_normalized_before_match():
    registry = AuthenticationProviderRegistry()

    registry.register(
        "good-provider",
        UppercaseNameAdapter,
    )

    adapter = registry.create("GOOD-PROVIDER")

    assert isinstance(
        adapter,
        UppercaseNameAdapter,
    )


def test_gate_successful_adapter_returns_trusted_external_principal():
    registry = AuthenticationProviderRegistry()

    registry.register(
        "good-provider",
        GoodAdapter,
    )

    adapter = registry.create("good-provider")

    principal = adapter.authenticate("valid")

    assert isinstance(
        principal,
        TrustedExternalPrincipal,
    )
    assert principal.identity_provider == "good-provider"


def test_gate_registry_does_not_authenticate_credentials_itself():
    source = _source(AuthenticationProviderRegistry)

    assert ".authenticate(" not in source
    assert "def authenticate(" not in source


def test_gate_registry_does_not_create_trusted_platform_caller():
    source = _source(AuthenticationProviderRegistry)

    assert "TrustedPlatformCaller" not in source
    assert "TrustedCallerIdentityService" not in source


def test_gate_registry_does_not_import_provider_specific_adapter():
    source = _source(AuthenticationProviderRegistry)

    assert "EntraOidcAuthenticationAdapter" not in source
    assert "Microsoft" not in source
    assert "Okta" not in source
    assert "Google" not in source
    assert "SecureW2" not in source


def test_gate_adapter_contract_does_not_import_provider_specific_adapter():
    source = _source(AuthenticationAdapter)

    assert "EntraOidcAuthenticationAdapter" not in source
    assert "Microsoft" not in source
    assert "Okta" not in source
    assert "Google" not in source
    assert "SecureW2" not in source


def test_gate_unregister_does_not_affect_other_provider():
    registry = AuthenticationProviderRegistry()

    class OtherAdapter(AuthenticationAdapter):
        @property
        def provider_name(self) -> str:
            return "other-provider"

        def authenticate(
            self,
            credential: str,
        ) -> TrustedExternalPrincipal:
            raise NotImplementedError

    registry.register(
        "good-provider",
        GoodAdapter,
    )
    registry.register(
        "other-provider",
        OtherAdapter,
    )

    registry.unregister("good-provider")

    assert registry.create("good-provider") is None
    assert isinstance(
        registry.create("other-provider"),
        OtherAdapter,
    )


def test_gate_provider_inventory_is_deterministic_and_immutable_snapshot():
    registry = AuthenticationProviderRegistry()

    class OtherAdapter(AuthenticationAdapter):
        @property
        def provider_name(self) -> str:
            return "other-provider"

        def authenticate(
            self,
            credential: str,
        ) -> TrustedExternalPrincipal:
            raise NotImplementedError

    registry.register(
        "other-provider",
        OtherAdapter,
    )
    registry.register(
        "good-provider",
        GoodAdapter,
    )

    names = registry.provider_names()

    assert names == (
        "good-provider",
        "other-provider",
    )
    assert isinstance(names, tuple)
