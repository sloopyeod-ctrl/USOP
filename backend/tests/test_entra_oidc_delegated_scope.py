from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa

from app.security.auth.EntraOidcAuthenticationAdapter import (
    EntraOidcAuthenticationAdapter,
    EntraOidcAuthenticationError,
)
from app.security.auth.EntraOidcValidationConfig import (
    EntraOidcValidationConfig,
)


TENANT = "11111111-2222-3333-4444-555555555555"
AUDIENCE = "api://usop-test-api"
REQUIRED_SCOPE = "access_as_user"
ISSUER = (
    f"https://login.microsoftonline.com/{TENANT}/v2.0"
)
NOW = datetime.now(UTC).replace(microsecond=0)

PRIVATE_KEY = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)
PUBLIC_KEY = PRIVATE_KEY.public_key()


class StaticJwkClient:
    def get_signing_key_from_jwt(self, token):
        return SimpleNamespace(key=PUBLIC_KEY)


def config(required_scope=REQUIRED_SCOPE):
    return EntraOidcValidationConfig(
        tenant_id=TENANT,
        audience=AUDIENCE,
        required_scope=required_scope,
    )


def claims(**overrides):
    values = {
        "aud": AUDIENCE,
        "exp": NOW + timedelta(minutes=10),
        "iat": NOW - timedelta(minutes=1),
        "iss": ISSUER,
        "nbf": NOW - timedelta(minutes=1),
        "oid": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
        "tid": TENANT,
        "ver": "2.0",
        "scp": REQUIRED_SCOPE,
    }
    values.update(overrides)
    return values


def encode(payload):
    return jwt.encode(
        payload,
        PRIVATE_KEY,
        algorithm="RS256",
        headers={"kid": "test-key"},
    )


def adapter(required_scope=REQUIRED_SCOPE):
    return EntraOidcAuthenticationAdapter(
        config(required_scope),
        jwk_client=StaticJwkClient(),
    )


def test_exact_required_delegated_scope_is_accepted():
    principal = adapter().authenticate(
        encode(claims()),
        now=NOW,
    )

    assert principal.external_tenant_id == TENANT


def test_required_scope_among_multiple_scopes_is_accepted():
    principal = adapter().authenticate(
        encode(
            claims(
                scp="openid access_as_user profile"
            )
        ),
        now=NOW,
    )

    assert principal.external_tenant_id == TENANT


def test_missing_scope_claim_fails_closed():
    payload = claims()
    payload.pop("scp")

    with pytest.raises(
        EntraOidcAuthenticationError,
        match="Required claim missing: scp",
    ):
        adapter().authenticate(
            encode(payload),
            now=NOW,
        )


@pytest.mark.parametrize(
    "scope_claim",
    [
        "",
        "profile",
        "access_as_user_evil",
        "evil_access_as_user",
        "access-as-user",
    ],
)
def test_wrong_or_ambiguous_scope_fails_closed(
    scope_claim,
):
    with pytest.raises(
        EntraOidcAuthenticationError
    ):
        adapter().authenticate(
            encode(
                claims(scp=scope_claim)
            ),
            now=NOW,
        )


def test_roles_claim_cannot_substitute_for_delegated_scope():
    payload = claims(
        roles=[REQUIRED_SCOPE],
    )
    payload.pop("scp")

    with pytest.raises(
        EntraOidcAuthenticationError
    ):
        adapter().authenticate(
            encode(payload),
            now=NOW,
        )


@pytest.mark.parametrize(
    "required_scope",
    [
        "",
        " ",
        "access_as_user profile",
        "access_as_user\tprofile",
    ],
)
def test_required_scope_configuration_fails_closed(
    required_scope,
):
    with pytest.raises(ValueError):
        config(required_scope)


@pytest.mark.parametrize(
    "configured_scope",
    [
        "  access_as_user  ",
        "\taccess_as_user",
        "access_as_user\t",
        "\naccess_as_user\n",
    ],
)
def test_required_scope_configuration_is_normalized(
    configured_scope,
):
    cfg = config(configured_scope)

    assert cfg.required_scope == "access_as_user"
