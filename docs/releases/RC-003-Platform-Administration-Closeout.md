# RC-003 Platform Administration Closeout

## Milestone

- Release Candidate: RC-003
- Milestone: Platform Administration
- Runtime Product Version: 0.14.0
- Architecture: Engine First
- Implementation Completion Commit: 30840e9
- Final Backend Regression: 870 passed, 16 warnings, 0 failures

RC-003 completes the Platform Administration release-candidate work within the USOP 0.14.0 development line.

## Proven Trust Chain

RC-003 validates the following end-to-end boundary:

External identity provider -> cryptographically validated external principal -> exact Platform User correlation -> Platform User lifecycle -> TrustedPlatformCaller -> runtime Platform authorization -> protected Platform Administration operation.

Authentication does not itself grant Platform roles, permissions, commercial seats, or licensing entitlement.

## Platform Administration Capabilities

- Organization-scoped Platform Users
- Canonical Platform Roles and Permissions
- Role-permission mappings
- Platform User role assignments
- Protected invitation and lifecycle operations
- Protected role and permission administration
- Runtime platform-administration.manage enforcement
- Last-effective-administrator protection
- Server-controlled trusted actor attribution
- Organization-boundary enforcement
- Non-enumerating cross-Organization failures

## Microsoft Entra Authentication

Microsoft Entra v2 access tokens are validated for:

- RS256 signature
- Microsoft JWKS signing key
- Tenant-specific issuer
- API audience
- Tenant claim
- External subject oid
- Token version
- Token time validity
- Signing algorithm and key identifier
- Required delegated API scope

Release configuration requires:

- USOP_AUTH_ENTRA_TENANT_ID
- USOP_AUTH_ENTRA_AUDIENCE
- USOP_AUTH_ENTRA_REQUIRED_SCOPE

The validated delegated scope for RC-003 is access_as_user.

A missing, incorrect, ambiguous, or substituted scope fails closed. Application roles do not substitute for the delegated scp claim.

## First Authentication

A real Microsoft Entra identity was validated against the release container.

Before first authentication:

- Platform User status: Invited
- activated_at: None
- last_authenticated_at: None
- PlatformUserInvitationAccepted events: 0

The first successful authenticated request caused exactly one Invited -> Active transition.

The transition recorded authentication completion while explicitly preserving:

- authorization_granted_by_transition=False
- seat_allocated_by_transition=False

Repeat authenticated requests were idempotent:

- status remained Active
- role assignments remained 1
- invitation acceptance events remained 1

## Runtime Authorization

A real authenticated Microsoft Entra Platform Administrator successfully accessed a protected Platform Administration endpoint through the complete chain of token validation, Platform User correlation, TrustedPlatformCaller resolution, runtime RBAC, and platform-administration.manage enforcement.

The protected request returned HTTP 200.

## Protected Platform User Reads

The Platform User inventory endpoints now require authenticated runtime Platform Administration authorization.

- GET /api/v1/organizations/{organization_id}/platform-users/
- GET /api/v1/organizations/{organization_id}/platform-users/{platform_user_id}

Foreign-Organization access fails without exposing cross-Organization object existence.

## Live Delegated-Scope Validation

Positive gate:

- real Microsoft token
- token scp=access_as_user
- USOP required scope=access_as_user
- protected request returned HTTP 200

Negative gate:

- same otherwise-valid Microsoft token
- USOP temporarily required a scope not present in the token
- protected request returned HTTP 401
- external response remained generic: Bearer token authentication failed
- access_as_user policy was restored afterward

## HTTP Trust Boundary

- Missing bearer token -> 401
- Non-Bearer scheme -> 401
- Cryptographically rejected token -> 401
- Missing required delegated scope -> 401
- Authenticated but unresolved USOP caller -> 403
- Runtime permission denial -> 403
- Foreign-Organization Platform User read -> non-enumerating 404
- Authorized Platform Administrator -> 200

## Persistence

Release-stack rebuilds and container recreation preserved PostgreSQL-backed Organization, Platform User, role assignment, licensing, bootstrap audit, invitation-acceptance audit, and lifecycle state.

## Final Regression Evidence

- 870 backend tests passed
- 16 known warnings
- 0 failures
- Consolidated HTTP authentication boundary gate: 12 passed

## Version Decision

The authoritative runtime version remains APP_VERSION = 0.14.0.

The existing product milestone tag remains v0.14.0-decision-intelligence.

RC-003 completion does not introduce a semantic product-version increment.

## Final Implementation State

- 30840e9 RC-003.4.4.2: Add consolidated HTTP authentication boundary gate
- 16d1861 RC-003.4.4.1: Enforce delegated API scope
- 2cdb139 RC-003.4.4.0: Protect Platform User read endpoints
- 3909a36 RC-003.4.3.0: Add release inbound authentication contract
- 8dc5293 RC-003.4.2.3: Wire first-authentication composition into HTTP caller resolution

RC-003 Platform Administration is declared complete when this closeout record is committed and the annotated Git tag rc-003-platform-administration-complete is created.
