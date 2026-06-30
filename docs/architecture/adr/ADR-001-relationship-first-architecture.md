# ADR-001: Relationship-First Architecture

Version: 1.0  
Status: Accepted  
Date: 2026-06-30  
Author: Marvin G. Dewitt  

---

## Context

USOP is designed to reduce operational friction for Security Engineers by connecting identities, accounts, service accounts, assets, applications, documentation, evidence, risks, and compliance controls into a unified operational workspace.

Traditional security platforms often store isolated records in disconnected modules. This approach forces engineers to manually reconstruct context across multiple systems during investigations, reviews, audits, and daily operations.

USOP requires a model that can answer operational questions such as:

- Who owns this service account?
- What systems depend on this application?
- Which controls does this evidence support?
- What breaks if this asset is retired?
- Which identities have access to this system?

These questions are relationship-based, not record-based.

---

## Decision

USOP will use a relationship-first architecture.

Relationships are treated as first-class operational objects rather than simple database joins.

Each relationship may include metadata such as:

- Relationship type
- Source object
- Target object
- Verification status
- Confidence score
- Source system
- Last sync date
- Review history
- Supporting evidence
- Notes

---

## Consequences

### Benefits

- Enables operational context across systems
- Supports 360° object views
- Improves audit evidence traceability
- Reduces manual investigation effort
- Supports impact analysis
- Preserves institutional knowledge
- Enables future graph-based capabilities

### Tradeoffs

- Requires more careful data modeling
- Relationship validation becomes a core platform function
- UI must clearly explain object connections
- Additional logic is required to prevent stale or incorrect relationships

---

## Product Principle

Security Engineers should not have to manually reconstruct context.

USOP should show how security objects connect.
