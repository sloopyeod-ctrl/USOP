# ADR-016 – Continuous Access Reviews

## Status

Accepted

---

## Context

USOP is evolving from an Identity Inventory into a complete Identity Governance & Administration (IGA) platform.

Enterprise identity governance requires periodic certification that user access remains appropriate.

Many regulations require organizations to periodically review user access, privileged accounts, and role assignments.

Examples include:

- CMMC Level 2
- NIST SP 800-171
- NIST 800-53
- ISO 27001
- SOC 2
- FedRAMP

Current commercial IGA platforms perform recurring access certifications.

USOP shall support continuous access certification.

---

## Decision

Each identity shall maintain an active Access Review record.

A review becomes required whenever:

- 30 days have elapsed since approval (default)
- Identity risk score changes
- Account added or removed
- Group membership changes
- Role assignment changes
- Permission changes
- Authentication posture changes
- Identity attributes affecting authorization change

Organizations may configure the review interval.

Default:

30 days

---

## Approval Workflow

Pending

↓

Security Review

↓

Approved

↓

Review Date Updated

↓

Next Due Date = Review Date + Configured Interval

---

## Access Snapshot

Each approval stores a normalized snapshot of:

- Identity
- Accounts
- Groups
- Roles
- Permissions
- Authentication
- Risk Score

A SHA-256 hash will be generated.

Future scans compare the current snapshot hash against the approved snapshot.

If hashes differ:

Status = Needs Review

Reason = Access Changed

---

## Review Status

Pending

Approved

Rejected

Expired

Needs Review

Exception Approved

---

## Review Types

Automatic

Scheduled

Risk Triggered

Manual

Emergency

---

## Design Goals

No identity should go more than the configured interval without review.

Reviews should require minimal manual effort.

Only identities with changes should require analyst attention.

All approvals shall be fully auditable.

---

## Future Enhancements

Manager approvals

System owner approvals

Multi-stage approvals

Email notifications

Dashboard widgets

Approval history

Electronic signatures

Exception tracking

Workflow automation

Compliance reporting