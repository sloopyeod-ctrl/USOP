# ADR-013: Identity Domain Model

Version: 1.0  
Status: Accepted  
Author: Marvin G. Dewitt

---

## Context

USOP correlates operational information from numerous enterprise systems including identity providers, endpoint management systems, cloud providers, HR systems, ticketing platforms, and custom connectors.

Traditional identity systems often attempt to store every attribute directly on the identity record, creating tightly coupled schemas that resemble HR systems and become difficult to extend.

USOP is an operational intelligence platform rather than a human resources system. The identity model must remain stable while allowing flexible ingestion of changing data from many sources.

---

## Decision

The Identity entity will represent only the stable operational identity.

Dynamic business attributes such as department, manager, location, cost center, business unit, organization, title, and similar metadata will not be stored directly on the Identity table.

Instead, these values will be represented as separate IdentityAttribute records linked to the Identity.

Accounts, relationships, evidence, assets, workflow items, and future entities will reference Identity through foreign keys.

---

## Identity Responsibilities

The Identity entity is responsible for:

- Unique identifier (UUID)
- Display name
- Identity class
- Operational status
- Primary contact information
- Source system
- Source identifier
- Confidence score
- Audit timestamps

---

## Design Principles

- Identity represents operational identity.
- Identity is intentionally minimal.
- Dynamic information belongs in separate entities.
- Multiple systems may provide conflicting information.
- USOP preserves source attribution rather than overwriting values.
- Every attribute should maintain provenance and confidence.

---

## Consequences

Identity remains stable as the platform evolves.

Additional attributes can be introduced without database redesign.

Connectors can import differing values while preserving operational history.

The model naturally supports identity resolution and relationship intelligence.

---

## Benefits

- Extensible schema
- Reduced coupling
- Better normalization
- Improved provenance
- Supports confidence scoring
- Simplifies future integrations

---

## Tradeoffs

- Additional joins when retrieving complete identity information
- Slightly more complex repository layer
- More entities to manage

---

## Product Principle

Identity is the operational anchor for the USOP knowledge graph, not an HR record.