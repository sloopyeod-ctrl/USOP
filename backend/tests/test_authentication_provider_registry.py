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


class ExampleAuthenticationAdapter(
    AuthenticationAdapter
):
    @property
    def provider_name(self) -> str:
        return "example-provider"

    def authenticate(
        self,
        credential: str,
    ) -> TrustedExternalPrincipal:
        if credential != "valid":
            raise ValueError("Credential rejected.")

        return TrustedExternalPrincipal(
            identity_provider=self.provider_name,
            external_tenant_id="tenant-1",
            external_subject_id="subject-1",
        )


class WrongNameAuthenticationAdapter(
    AuthenticationAdapter
):
    @property
    def provider_name(self) -> str:
        return "wrong-provider"

    def authenticate(
        self,
        credential: str,
    ) -> TrustedExternalPrincipal:
        raise NotImplementedError


def test_registry_registers_and_creates_adapter():
    registry = AuthenticationProviderRegistry()
    registry.register(
        "example-provider",
        ExampleAuthenticationAdapter,
    )

    adapter = registry.create("example-provider")

    assert isinstance(
        adapter,
        ExampleAuthenticationAdapter,
    )

    principal = adapter.authenticate("valid")
    assert isinstance(
        principal,
        TrustedExternalPrincipal,
    )
    assert (
        principal.identity_provider
        == "example-provider"
    )


def test_registry_normalizes_lookup_name():
    registry = AuthenticationProviderRegistry()
    registry.register(
        "example-provider",
        ExampleAuthenticationAdapter,
    )

    adapter = registry.create(
        "  EXAMPLE-PROVIDER  "
    )

    assert isinstance(
        adapter,
        ExampleAuthenticationAdapter,
    )


def test_registry_rejects_duplicate_provider():
    registry = AuthenticationProviderRegistry()
    registry.register(
        "example-provider",
        ExampleAuthenticationAdapter,
    )

    with pytest.raises(
        ValueError,
        match="already registered",
    ):
        registry.register(
            "EXAMPLE-PROVIDER",
            ExampleAuthenticationAdapter,
        )


@pytest.mark.parametrize(
    "provider_name",
    [
        "",
        " ",
        "-provider",
        "provider-",
        "provider--name",
        "provider_name",
        "provider name",
        "provider/name",
    ],
)
def test_registry_rejects_invalid_provider_names(
    provider_name,
):
    registry = AuthenticationProviderRegistry()

    with pytest.raises(ValueError):
        registry.register(
            provider_name,
            ExampleAuthenticationAdapter,
        )


def test_registry_returns_none_for_unknown_provider():
    registry = AuthenticationProviderRegistry()

    assert (
        registry.create("unknown-provider")
        is None
    )


def test_registry_lists_provider_names_deterministically():
    registry = AuthenticationProviderRegistry()

    class AnotherAuthenticationAdapter(
        AuthenticationAdapter
    ):
        @property
        def provider_name(self) -> str:
            return "another-provider"

        def authenticate(
            self,
            credential: str,
        ) -> TrustedExternalPrincipal:
            raise NotImplementedError

    registry.register(
        "example-provider",
        ExampleAuthenticationAdapter,
    )
    registry.register(
        "another-provider",
        AnotherAuthenticationAdapter,
    )

    assert registry.provider_names() == (
        "another-provider",
        "example-provider",
    )


def test_registry_rejects_non_callable_factory():
    registry = AuthenticationProviderRegistry()

    with pytest.raises(TypeError):
        registry.register(
            "example-provider",
            object(),
        )


def test_registry_rejects_non_adapter_factory_result():
    registry = AuthenticationProviderRegistry()

    registry.register(
        "example-provider",
        lambda: object(),
    )

    with pytest.raises(
        TypeError,
        match="does not implement",
    ):
        registry.create("example-provider")


def test_registry_rejects_adapter_name_mismatch():
    registry = AuthenticationProviderRegistry()

    registry.register(
        "example-provider",
        WrongNameAuthenticationAdapter,
    )

    with pytest.raises(
        ValueError,
        match="does not match",
    ):
        registry.create("example-provider")


def test_registry_unregister_is_idempotent():
    registry = AuthenticationProviderRegistry()
    registry.register(
        "example-provider",
        ExampleAuthenticationAdapter,
    )

    registry.unregister("example-provider")
    registry.unregister("example-provider")

    assert (
        registry.create("example-provider")
        is None
    )
