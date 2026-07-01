# ADR-014: Shared Domain Base Classes

Version: 1.0  
Status: Accepted  
Author: Marvin G. Dewitt  

---

## Context

USOP contains many persistent domain entities including identities, accounts, groups, roles, permissions, applications, resources, evidence, risks, findings, investigations, and relationships between those objects.

As the domain model grows, repeated fields such as identifiers, timestamps, active status, source system, source identifier, and confidence score can create unnecessary duplication and inconsistent implementation.

A shared base class strategy is needed to keep the codebase consistent, maintainable, and easier to extend.

---

## Decision

USOP will use shared SQLAlchemy base classes for common persistent entity behavior.

The existing `BaseModel` will remain the universal base class for persistent objects.

`BaseModel` provides:

- UUID primary identifier
- Created timestamp
- Updated timestamp
- Created by
- Updated by
- Active status

USOP will introduce `BaseSourceModel` for operational security objects that require source attribution and confidence scoring.

`BaseSourceModel` will extend `BaseModel` and provide:

- Source system
- Source identifier
- Confidence score

---

## Design Rules

- All persistent domain entities should inherit from `BaseModel` or a subclass of it.
- Entities that represent imported, discovered, correlated, or operational security data should inherit from `BaseSourceModel`.
- Source attribution must be preserved when data is imported from external systems.
- Confidence scoring should be used when data may come from multiple systems or heuristic matching.
- Models should not redefine fields already provided by their base class.
- Any exception to this inheritance strategy should be documented with an ADR.

---

## Consequences

USOP gains a more consistent domain model.

Future entities can be created faster and with fewer duplicate field definitions.

The scaffold generator can create more consistent vertical slices.

Graph traversal, analytics, and reporting can rely on common metadata across domain objects.

---

## Benefits

- Reduced code duplication
- Consistent audit metadata
- Consistent provenance tracking
- Consistent confidence scoring
- Cleaner model definitions
- Easier future refactoring
- Stronger platform architecture

---

## Tradeoffs

- Existing models may require refactoring.
- Database migrations must account for moving common fields into shared base classes.
- Developers must understand which base class to use for each entity.

---

## Product Principle

Security data should preserve where it came from, how confident USOP is in it, and when it changed.