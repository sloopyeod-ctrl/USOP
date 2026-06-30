# ADR-010: Base Model Standardization

Version: 1.0  
Status: Accepted  
Author: Marvin G. Dewitt  

---

## Context

USOP contains many core operational objects including Identities, Accounts, Service Accounts, Assets, Applications, Relationships, Tasks, Evidence, Risks, POA&Ms, Policies, Procedures, Controls, Frameworks, and Connectors.

Each object requires consistent lifecycle tracking, auditability, and identification.

Without a shared base model, each object would need to independently implement identifiers, timestamps, audit fields, and active-state tracking.

---

## Decision

All persistent USOP objects will inherit from a shared `BaseModel`.

The shared model will provide:

- UUID primary identifier
- Created timestamp
- Updated timestamp
- Created by
- Updated by
- Active status

---

## Consequences

All USOP objects will have consistent operational metadata.

This improves auditability, traceability, development consistency, API design, and future reporting.

Future models may extend `BaseModel`, but should not bypass it unless an explicit ADR is created.

---

## Benefits

- Consistent object identity
- Simplified model creation
- Better audit support
- Easier API standardization
- Cleaner repository and service logic
- Stronger alignment with the ERD

---

## Tradeoffs

- Some lightweight lookup tables may contain more metadata than strictly required.
- Developers must understand inherited fields when creating new models.
- Changes to `BaseModel` affect every persistent object.

---

## Product Principle

Every operational object should be identifiable, auditable, and traceable.
