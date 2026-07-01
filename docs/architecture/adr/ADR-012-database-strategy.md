# ADR-012: Database Strategy

Version: 1.0  
Status: Accepted  
Author: Marvin G. Dewitt  

---

## Context

USOP stores operational security data including identities, accounts, relationships, evidence, tasks, risks, POA&Ms, controls, framework mappings, connector metadata, and operational journal entries.

The database strategy must support structured relationships, auditability, schema evolution, semi-structured connector data, and future cloud-native deployment.

---

## Decision

USOP will use PostgreSQL as the primary operational database.

Alembic will be the standard mechanism for all schema migrations.

SQLAlchemy will be used as the ORM layer.

All persistent operational entities will use UUID identifiers through the shared BaseModel.

Repository classes will be the primary persistence boundary between business logic and the database.

---

## Design Rules

- PostgreSQL is the primary development and production database.
- SQLite may be used only for lightweight local testing if needed.
- All schema changes require Alembic migrations.
- Application code must not modify schema directly.
- Business logic must not access SQLAlchemy sessions directly outside repository boundaries.
- Semi-structured connector metadata may use PostgreSQL JSONB where appropriate.
- Database configuration must be environment-driven.
- Persistent entities should inherit from BaseModel unless an ADR approves an exception.

---

## Consequences

USOP gains a production-grade relational database foundation.

Schema changes are versioned and repeatable.

Future entities can be added consistently.

The platform can support structured relationships while still allowing flexible connector metadata.

---

## Benefits

- Strong relational integrity
- Native UUID support
- JSONB support for connector data
- Mature indexing
- Reliable transactions
- Production parity during development
- Repeatable migrations
- Strong audit history

---

## Tradeoffs

- Requires PostgreSQL during development
- Adds Docker dependency for local work
- More complex than SQLite
- Developers must understand migration workflow

---

## Product Principle

Operational security data should be durable, auditable, relational, and evolvable.