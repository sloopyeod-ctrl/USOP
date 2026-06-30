ADR-004: Identity and Account Separation

Version: 1.0
Status: Accepted
Author: Marvin G. Dewitt

Context

One person may have multiple accounts across systems such as Entra ID, GitHub, Docker, Keeper, NetBox, Snowflake, VPN, and privileged systems.

Combining identity and account data would create duplication and poor lifecycle visibility.

Decision

USOP will model Identity and Account as separate core objects.

An Identity represents a person or organizational actor.

An Account represents a system-specific login, credential, role assignment, or access relationship.

Consequences

One Identity may have many Accounts.

Accounts may have different roles, authentication methods, MFA status, privilege levels, and review history.

This supports RBAC validation, privileged account review, JML lifecycle review, and access certification.

Product Principle

A person is not the same thing as a login.
