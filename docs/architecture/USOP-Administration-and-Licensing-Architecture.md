# USOP Administration and Licensing Architecture

**Version:** 1.0  
**Status:** Draft

---

## 1. Mission

USOP Administration provides trustworthy access control, authenticated actor attribution, customer-configurable governance, and subscription-seat enforcement without becoming a replacement identity provider.

USOP should authenticate enterprise identities, authorize access within USOP, enforce subscription limits, and preserve an auditable record of every material action.

---

## 2. Core Separation of Responsibilities

### Authentication

Authentication determines who signed in.

USOP should rely on supported enterprise identity providers such as Microsoft Entra ID through standards-based authentication.

USOP should not create a separate local password directory unless a future deployment model explicitly requires it.

### Authorization

Authorization determines what an authenticated user may do inside USOP.

USOP roles and permissions are separate from provider roles.

A Microsoft Entra Global Administrator may still have Read Only access inside USOP.

### Licensing

Licensing determines whether the organization may assign another active USOP user seat.

Supported plans may include:

- Up to 10 active users
- Up to 20 active users
- Unlimited active users

Inactive or revoked users should not consume an active seat unless the selected commercial policy states otherwise.

### Governance

Governance determines organization-specific workflow requirements.

Examples include:

- Review interval
- Approval requirements
- Required notes
- Required justification
- Permanent acceptance availability
- Temporary acceptance limits
- Verification requirements
- Ticket-reference requirements

USOP does not define these policies. USOP helps customers configure, enforce, monitor, and evidence them.

---

## 3. Canonical Objects

### Organization

Represents the customer or tenant operating USOP.

Core attributes:

- Organization ID
- Name
- Status
- Primary domain
- Subscription plan
- Seat limit
- Time zone
- Created at
- Updated at

### USOP User

Represents an enterprise identity that has been granted access to USOP.

A USOP User references an existing synchronized identity where possible.

Core attributes:

- User ID
- Organization ID
- Identity ID
- Login subject
- Display name
- Email
- Status
- Seat assigned
- Last authenticated at
- Created at
- Updated at

### USOP Role

Represents a role within USOP.

Initial roles may include:

- Super Administrator
- Organization Administrator
- Governance Manager
- Security Engineer
- Security Analyst
- Read Only
- Executive Viewer

### Permission

Represents a specific allowed operation.

Examples:

- Manage organization settings
- Manage users
- Assign roles
- Manage governance policy
- Create decisions
- Approve decisions
- Verify remediation
- View audit history
- View executive reporting
- Manage integrations

### User Role Assignment

Associates a USOP User with one or more USOP Roles.

### Subscription

Represents commercial entitlement.

Core attributes:

- Plan
- Seat limit
- Effective date
- Expiration date
- Status
- Feature entitlements

### Governance Settings

Represent customer-defined policy choices.

Governance settings are independent of subscription and user authorization.

---

## 4. User Provisioning Lifecycle

```text
Enterprise identity synchronized
    ↓
Administrator grants USOP access
    ↓
Seat availability validated
    ↓
USOP User activated
    ↓
USOP Role assigned
    ↓
User authenticates through enterprise IdP
    ↓
Session resolves authenticated USOP User
    ↓
Actions are authorized and audited

USOP should never require an administrator to recreate identity information already synchronized from the customer’s identity provider.

## 5. User Deactivation and Removal

Deactivating a USOP User should:

Prevent future sign-in
Revoke active sessions
Preserve historical decisions
Preserve audit history
Preserve authorship attribution
Release the active seat when applicable

Historical records must never lose attribution because a user leaves the organization.

A decision created by Johnny must remain attributable to Johnny even after Johnny’s USOP access is disabled.

## 6. Authenticated Actor Attribution

Every material action should be linked to an authenticated USOP User ID.

Examples include:

Decision created
Risk accepted
Corrective action recorded
Approval granted
Verification completed
Governance policy changed
User role assigned
User deactivated
Subscription changed

Human-readable names may be displayed, but stable IDs must remain the authoritative references.

User-supplied actor names must not be treated as trusted attribution.

## 7. Audit and Chain of Accountability

Every material administration and governance action must create an append-only audit event.

An audit event should include:

Organization ID
Authenticated USOP User ID
Authentication subject
Session or request correlation ID
Event type
Entity type
Entity ID
Server-generated timestamp
Human-readable message
Relevant metadata

Audit history must support questions such as:

Who granted this user access?
Who assigned this role?
Who accepted this risk?
What justification was supplied?
Which governance policy applied?
Who later reviewed or changed the decision?

## 8. Subscription and Seat Enforcement

Seat limits apply to active users with assigned USOP access.

Example plans:

Starter
Seat limit: 10

Professional
Seat limit: 20

Enterprise
Seat limit: Unlimited

The system should expose:

Seat limit
Seats assigned
Seats available
Pending invitations or assignments
Disabled users
Subscription status

The backend must enforce seat limits.

The frontend may display seat availability but must not be the authoritative enforcement point.

## 9. Role and Permission Enforcement

Permissions must be evaluated server-side.

The frontend may hide unavailable actions for usability, but API authorization remains authoritative.

Example:

Security Analyst
- View identity intelligence
- Create decision records
- Add investigation notes

Governance Manager
- Approve decisions
- Configure governance policy
- Review overdue decisions

Organization Administrator
- Manage users
- Assign roles
- Manage integrations
- View audit history

Role definitions should be configurable in the future, but Version 1 may begin with controlled built-in roles.

## 10. Customer-Defined Governance

USOP must not hardcode customer governance requirements.

Examples of configurable settings:

Identity review interval
Require approval for risk acceptance
Require justification
Require analyst notes
Allow permanent acceptance
Require review date for temporary acceptance
Maximum temporary acceptance duration
Require remediation verification
Require ticket reference
Allowed approver roles
Overdue-review handling

A customer may select any supported interval or disable a requirement when policy allows.

USOP records and enforces the selected configuration.

## 11. Policy Snapshotting

Every decision and review should preserve the governance policy evaluation used at that time.

Example:

Approval required: No
Review interval: 90 days
Permanent acceptance allowed: Yes
Verification required: Yes

If settings change later, historical decisions must remain explainable under the policy that applied when they were created.


## 12. Authentication Strategy

Version 1 should prioritize Microsoft Entra ID using OIDC/OAuth2.

The authenticated identity should resolve to:

Identity Provider Subject
    ↓
USOP User
    ↓
Organization
    ↓
Roles
    ↓
Permissions
    ↓
Active Subscription Seat

Authentication success alone does not grant access.

The user must also:

belong to an active organization;
have an active USOP User record;
have an assigned seat when required;
possess permission for the requested action.

## 13. Session Security

Sessions should support:

Secure tokens
Short-lived access tokens
Refresh-token rotation where applicable
Revocation
Session expiration
Authentication timestamps
Organization binding
User binding
Audit correlation
Least-privilege claims

Secrets and provider tokens must never be stored in audit metadata or decision evidence.

## 14. Administration Experience

The administration workspace should include:

Organization
Organization profile
Subscription plan
Seat usage
Time zone
Status
Users
Active users
Disabled users
Available synchronized identities
Grant access
Revoke access
Seat assignment
Last sign-in
Roles and Permissions
Assigned roles
Effective permissions
Role changes
Administrative audit history
Governance Settings
Review intervals
Decision requirements
Approval rules
Verification rules
Overdue behavior
Audit
User-management events
Role changes
Governance-setting changes
Decision activity
Authentication events

## 15. Historical Attribution

Deleting or disabling a user must never delete:

Decision records
Notes
Justifications
Approvals
Verification history
Audit events

Historical displays should retain the actor’s recorded name and stable user identifier even when the account is inactive.

## 16. Security Principles
Never trust browser-supplied actor identity.
Never authorize solely in React.
Never delete audit history when a user is removed.
Never require users to re-enter synchronized identity data.
Never mix provider roles with USOP roles.
Never hardcode customer governance policy.
Never allow seat-limit enforcement to exist only in the frontend.
Always attribute material actions to authenticated users.
Always use server-generated timestamps.
Always preserve the policy context used for historical decisions.

## 17. Success Criteria

This subsystem succeeds when:

Administrators can grant or revoke USOP access.
Subscription seat limits are enforced.
Users authenticate through supported enterprise identity providers.
USOP permissions are evaluated independently from provider privileges.
Every decision is attributable to an authenticated user.
Historical attribution survives user deactivation.
Customers define their own governance requirements.
Governance changes are auditable.
Analysts can see who made earlier decisions and why.
USOP reduces administrative burden rather than creating another directory to maintain.

## 18. Architectural Summary

USOP authenticates enterprise identities, authorizes USOP users, enforces subscription entitlements, and attributes every material action to a trustworthy actor.

Organizations define governance policy.

USOP applies and evidences that policy without replacing the customer’s identity provider, ticketing platform, or GRC system.
