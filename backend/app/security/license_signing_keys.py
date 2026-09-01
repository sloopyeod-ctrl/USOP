from dataclasses import dataclass
from typing import Iterable


class LicenseSigningKeyRegistryError(ValueError):
    """Base error for trusted License signing-key registry failures."""


class InvalidLicenseSigningKeyError(
    LicenseSigningKeyRegistryError
):
    """Raised when trusted signing-key material is structurally invalid."""


class DuplicateLicenseSigningKeyError(
    LicenseSigningKeyRegistryError
):
    """Raised when one signing-key identifier is registered more than once."""


class UnknownLicenseSigningKeyError(
    LicenseSigningKeyRegistryError
):
    """Raised when a License references an untrusted signing-key identifier."""


@dataclass(frozen=True)
class TrustedLicenseSigningKey:
    """
    Public verification material trusted by the USOP runtime.

    Private signing material must never be represented by this model.
    """

    key_identifier: str
    public_key_pem: bytes

    def __post_init__(self) -> None:
        normalized_identifier = self.key_identifier.strip()

        if not normalized_identifier:
            raise InvalidLicenseSigningKeyError(
                "License signing-key identifier must not be empty."
            )

        if not isinstance(self.public_key_pem, bytes):
            raise InvalidLicenseSigningKeyError(
                "License public verification key must be bytes."
            )

        if not self.public_key_pem.strip():
            raise InvalidLicenseSigningKeyError(
                "License public verification key must not be empty."
            )

        object.__setattr__(
            self,
            "key_identifier",
            normalized_identifier,
        )


class TrustedLicenseSigningKeyRegistry:
    """
    Immutable runtime lookup for trusted License verification keys.

    The registry contains public verification material only. Unknown signing
    keys fail closed rather than falling back to another trusted key.
    """

    def __init__(
        self,
        keys: Iterable[TrustedLicenseSigningKey] = (),
    ) -> None:
        registry: dict[str, TrustedLicenseSigningKey] = {}

        for key in keys:
            if key.key_identifier in registry:
                raise DuplicateLicenseSigningKeyError(
                    "Duplicate License signing-key identifier: "
                    f"{key.key_identifier}"
                )

            registry[key.key_identifier] = key

        self._keys = registry

    def resolve(
        self,
        key_identifier: str,
    ) -> TrustedLicenseSigningKey:
        normalized_identifier = key_identifier.strip()

        if not normalized_identifier:
            raise UnknownLicenseSigningKeyError(
                "License signing-key identifier is empty."
            )

        key = self._keys.get(normalized_identifier)

        if key is None:
            raise UnknownLicenseSigningKeyError(
                "License signing-key identifier is not trusted."
            )

        return key

    def contains(
        self,
        key_identifier: str,
    ) -> bool:
        try:
            self.resolve(key_identifier)
        except UnknownLicenseSigningKeyError:
            return False

        return True

    def identifiers(self) -> tuple[str, ...]:
        return tuple(sorted(self._keys))
